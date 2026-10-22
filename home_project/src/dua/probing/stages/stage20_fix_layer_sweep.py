"""Stage 20: sweep the *fix* direction across layers.

Stage 18 swept induce; fix had only ever run at the peak-decodability layer, so
the "steering cannot fix hallucination" null rested on the one layer Hase et
al. warn is not necessarily the best edit site. Same layer set and norm control
as Stage 18, on the Stage 17 mid-HR2 headroom pool where there is room to
improve. Either outcome is useful: no layer fixing hardens the null, some layer
fixing is a new positive result.

Usage
─────
  python -m dua.probing.stages.stage20_fix_layer_sweep \
      --model_path   /scratch/$USER/scholar_qwen/models/Qwen3-32B \
      --run_dir      /scratch/$USER/scholar_qwen/run_qwen3_32b \
      --data_csv     data/interim/probing_prompts_9108.csv \
      --meta_json    /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_meta.json \
      --layers       24 40 48 56 63 --norm_ref_layer 48 \
      --hr2_lo 0.35 --hr2_hi 0.65 --alphas 1 2 3 4 \
      --out_dir      /scratch/$USER/scholar_qwen/steering_qwen3_32b
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(__file__))
from stage1_generate import detect_model_config, load_model_and_tokenizer
from stage2_score import load_ground_truth
from stage14_activation_steering import (
    MAX_NEW_TOKENS,
    build_random_norm_matched_vector,
    get_decoder_layers,
    run_condition,
    summarize_condition,
)
from stage17_graded_bin_steering import select_band_pool
from stage18_layer_sweep import extract_p1_multilayer, load_pool

RANDOM_SEED = 42


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 20: fix-direction layer sweep (mid-HR2 pool)")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--run_dir", required=True)
    parser.add_argument("--data_csv", required=True)
    parser.add_argument("--meta_json", required=True,
                        help="steering_meta.json from a completed Stage 14 run (vector pool IDs)")
    parser.add_argument("--layers", type=int, nargs="+", required=True,
                        help="Decoder layers to sweep (match Stage 18: Qwen 24 40 48 56 63; Mistral 10 22 28 36)")
    parser.add_argument("--alphas", type=float, nargs="+", default=[1.0, 2.0, 3.0, 4.0])
    parser.add_argument("--hr2_lo", type=float, default=0.35)
    parser.add_argument("--hr2_hi", type=float, default=0.65)
    parser.add_argument("--n_eval", type=int, default=50,
                        help="Mid-HR2 band pool size (Stage 17 used 50)")
    parser.add_argument("--also_induce", action="store_true",
                        help="Also run the induce direction (-vec) on the same pool for a "
                             "same-population specificity reference")
    parser.add_argument("--target_norm", type=float, default=None,
                        help="Common L2 norm for every layer's vector (fair direction test). "
                             "If unset, falls back to --norm_ref_layer's norm, else median layer norm.")
    parser.add_argument("--norm_ref_layer", type=int, default=None,
                        help="Layer whose raw vector norm sets the common target norm "
                             "(recommended: peak layer, 48 Qwen / 22 Mistral)")
    parser.add_argument("--max_new_tokens", type=int, default=MAX_NEW_TOKENS)
    parser.add_argument("--quantize", default="none", choices=["none", "8bit", "4bit"])
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16"])
    parser.add_argument("--chat_style", default=None)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    out_dir = Path(args.out_dir)
    band_tag = f"hr2_{args.hr2_lo}_{args.hr2_hi}"

    scored = pd.read_csv(Path(args.run_dir) / "scored.tsv", sep="\t")
    scored["citation_count"] = pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0)
    gt_dict = load_ground_truth(args.data_csv)
    meta = json.load(open(args.meta_json))

    vector_correct = load_pool(scored, meta["pool_paper_ids"]["vector_correct"])
    vector_hallucinated = load_pool(scored, meta["pool_paper_ids"]["vector_hallucinated"])
    eval_pool = select_band_pool(scored, meta, args.hr2_lo, args.hr2_hi, args.n_eval, args.seed)
    print(f"[stage20] pools — vector_correct={len(vector_correct)} "
          f"vector_hallucinated={len(vector_hallucinated)} band({args.hr2_lo},{args.hr2_hi}]={len(eval_pool)}")
    if eval_pool.empty:
        raise RuntimeError(f"[stage20] mid-HR2 band ({args.hr2_lo},{args.hr2_hi}] is empty after "
                           "disjointness exclusion — nothing to sweep")

    registry_cfg = detect_model_config(args.model_path)
    chat_style = args.chat_style or (registry_cfg["chat_style"] if registry_cfg else "chatml")
    dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16
    print(f"[stage20] loading model {args.model_path} (chat_style={chat_style!r})")
    model, tokenizer = load_model_and_tokenizer(args.model_path, dtype, args.quantize)
    device = next(model.parameters()).device
    decoder_layers = get_decoder_layers(model)
    n_layers = len(decoder_layers)
    layers = [L for L in args.layers if L < n_layers]
    if len(layers) != len(args.layers):
        dropped = sorted(set(args.layers) - set(layers))
        print(f"[stage20] WARNING: dropping out-of-range layers {dropped} for a {n_layers}-layer model")

    # ── Build per-layer diff-of-means vectors (one forward pass per paper) ───
    print(f"[stage20] extracting P1 at layers {layers} for vector pools")
    correct_by_layer = {L: [] for L in layers}
    hallu_by_layer = {L: [] for L in layers}
    for _, r in vector_correct.iterrows():
        d = extract_p1_multilayer(model, tokenizer, r["title"], r["year"], chat_style, device, layers)
        for L in layers:
            correct_by_layer[L].append(d[L])
    for _, r in vector_hallucinated.iterrows():
        d = extract_p1_multilayer(model, tokenizer, r["title"], r["year"], chat_style, device, layers)
        for L in layers:
            hallu_by_layer[L].append(d[L])

    vectors = {}
    raw_norms = {}
    for L in layers:
        vec = np.stack(correct_by_layer[L]).mean(axis=0) - np.stack(hallu_by_layer[L]).mean(axis=0)
        vectors[L] = vec.astype(np.float32)
        raw_norms[L] = float(np.linalg.norm(vec))
        print(f"[stage20] layer {L}: raw vector norm={raw_norms[L]:.4f}")

    # Common norm so the sweep isolates direction quality, not magnitude
    # (identical rationale to Stage 18).
    if args.target_norm and args.target_norm > 0:
        target_norm = args.target_norm
    elif args.norm_ref_layer is not None and args.norm_ref_layer in raw_norms:
        target_norm = raw_norms[args.norm_ref_layer]
    else:
        target_norm = float(np.median(list(raw_norms.values())))
    print(f"[stage20] scaling all layer vectors to common norm {target_norm:.4f}")
    for L in layers:
        if raw_norms[L] > 0:
            vectors[L] = (vectors[L] / raw_norms[L] * target_norm).astype(np.float32)
    dim = int(next(iter(vectors.values())).shape[0])

    depth_pct = {L: round(100.0 * L / (n_layers - 1), 1) for L in layers}
    results_summary: list[dict] = []
    predictions: list[pd.DataFrame] = []

    def record(df: pd.DataFrame, **tags) -> None:
        if not df.empty:
            tagged = df.copy()
            for k, v in tags.items():
                tagged[k] = v
            predictions.append(tagged)
        results_summary.append(summarize_condition(df, **tags))

    # ── Baseline on the mid-HR2 pool (no steering) ──────────────────────────
    print("[stage20] baseline (no steering)")
    df = run_condition(model, tokenizer, decoder_layers, layers[0], device, chat_style,
                       eval_pool, gt_dict, args.max_new_tokens, vector=None, alpha=0.0)
    record(df, layer=-1, layer_depth_pct=float("nan"), applied_vector_norm=0.0, raw_vector_norm=0.0,
           condition="baseline", direction="none", alpha=0.0)

    # ── Per layer: fix (+vec), norm-matched control, optional induce (-vec) ──
    for L in layers:
        rand_vec = build_random_norm_matched_vector(dim, target_norm, seed=args.seed + 500 + L)
        for alpha in args.alphas:
            print(f"[stage20] FIX layer {L} (depth {depth_pct[L]}%), alpha={alpha}")
            df = run_condition(model, tokenizer, decoder_layers, L, device, chat_style,
                               eval_pool, gt_dict, args.max_new_tokens,
                               vector=vectors[L], alpha=alpha)
            record(df, layer=L, layer_depth_pct=depth_pct[L],
                   applied_vector_norm=round(target_norm, 4), raw_vector_norm=round(raw_norms[L], 4),
                   condition="fix", direction="toward_cited", alpha=alpha)

            print(f"[stage20] control(norm-matched) layer {L}, alpha={alpha}")
            df = run_condition(model, tokenizer, decoder_layers, L, device, chat_style,
                               eval_pool, gt_dict, args.max_new_tokens,
                               vector=rand_vec, alpha=alpha)
            record(df, layer=L, layer_depth_pct=depth_pct[L],
                   applied_vector_norm=round(target_norm, 4), raw_vector_norm=round(raw_norms[L], 4),
                   condition="control_norm_matched", direction="toward_cited", alpha=alpha)

            if args.also_induce:
                print(f"[stage20] INDUCE layer {L}, alpha={alpha}")
                df = run_condition(model, tokenizer, decoder_layers, L, device, chat_style,
                                   eval_pool, gt_dict, args.max_new_tokens,
                                   vector=-vectors[L], alpha=alpha)
                record(df, layer=L, layer_depth_pct=depth_pct[L],
                       applied_vector_norm=round(target_norm, 4), raw_vector_norm=round(raw_norms[L], 4),
                       condition="induce", direction="toward_hallucinated", alpha=alpha)

    summary_df = pd.DataFrame(results_summary)
    summary_df.to_csv(out_dir / f"fix_layer_sweep_results_{band_tag}.csv", index=False)
    print(f"[stage20] wrote {out_dir / f'fix_layer_sweep_results_{band_tag}.csv'}")

    if predictions:
        pd.concat(predictions, ignore_index=True).to_csv(
            out_dir / f"fix_layer_sweep_predictions_{band_tag}.tsv", sep="\t", index=False)
        print(f"[stage20] wrote {out_dir / f'fix_layer_sweep_predictions_{band_tag}.tsv'}")

    meta_out = {
        "model_path": args.model_path,
        "layers": layers,
        "layer_depth_pct": depth_pct,
        "alphas": args.alphas,
        "hr2_band": [args.hr2_lo, args.hr2_hi],
        "n_eval": len(eval_pool),
        "also_induce": args.also_induce,
        "common_target_norm": round(target_norm, 6),
        "raw_vector_norms": {str(L): round(raw_norms[L], 6) for L in layers},
        "eval_pool_paper_ids": eval_pool["paper_id"].astype(str).tolist(),
    }
    with open(out_dir / f"fix_layer_sweep_meta_{band_tag}.json", "w") as f:
        json.dump(meta_out, f, indent=2)
    print(f"[stage20] wrote {out_dir / f'fix_layer_sweep_meta_{band_tag}.json'}")

    print("\n[stage20] === summary ===")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
