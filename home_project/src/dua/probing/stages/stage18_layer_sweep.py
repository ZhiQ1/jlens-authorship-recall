"""Stage 18: is the induce effect specific to the peak-decodability layer?

Sweeps layers chosen from the per-layer P1 R2 curve, builds a diff-of-means
vector at each, and measures induced hallucination on a small held-out pool.
Every layer is scaled to a common norm, so the sweep tests direction, not
magnitude. Exploratory: n is about 30, one alpha.

Usage
─────
  python -m dua.probing.stages.stage18_layer_sweep \
      --model_path   /scratch/$USER/scholar_qwen/models/Qwen3-32B \
      --run_dir      /scratch/$USER/scholar_qwen/run_qwen3_32b \
      --data_csv     data/interim/probing_prompts_9108.csv \
      --meta_json    /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_meta.json \
      --layers       24 40 48 56 63 \
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
    build_input,
    get_decoder_layers,
    run_condition,
    summarize_condition,
)

RANDOM_SEED = 42


@torch.no_grad()
def extract_p1_multilayer(model, tokenizer, title, year, chat_style, device,
                           layers: list[int]) -> dict[int, np.ndarray]:
    """Last-prompt-token hidden state at every requested layer, from ONE
    forward pass (output_hidden_states returns all layers)."""
    input_ids, attention_mask = build_input(tokenizer, title, year, chat_style, device)
    out = model(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
    return {L: out.hidden_states[L + 1][0, -1, :].float().cpu().numpy() for L in layers}


def load_pool(scored: pd.DataFrame, paper_ids: list) -> pd.DataFrame:
    ids = {str(x) for x in paper_ids}
    return scored[scored["paper_id"].astype(str).isin(ids)].reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 18: layer sweep for activation steering")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--run_dir", required=True)
    parser.add_argument("--data_csv", required=True)
    parser.add_argument("--meta_json", required=True,
                        help="steering_meta.json from the completed Stage 14 run (pool IDs)")
    parser.add_argument("--layers", type=int, nargs="+", required=True,
                        help="Decoder layers to sweep (e.g. Qwen3-32B: 24 40 48 56 63; Mistral: 10 22 28 36)")
    parser.add_argument("--alpha", type=float, default=2.0,
                        help="Fixed steering magnitude (induce direction)")
    parser.add_argument("--n_eval", type=int, default=30,
                        help="Subsample size from Stage 14's eval_high pool")
    parser.add_argument("--max_new_tokens", type=int, default=MAX_NEW_TOKENS)
    parser.add_argument("--target_norm", type=float, default=None,
                        help="Scale every layer's diff-of-means vector to this common L2 norm "
                             "before steering, so alpha*||v|| is constant across layers (a fair "
                             "direction-quality test, not a per-layer magnitude test). If unset, "
                             "falls back to --norm_ref_layer's norm, else the median layer norm.")
    parser.add_argument("--norm_ref_layer", type=int, default=None,
                        help="Layer whose raw vector norm sets the common target norm when "
                             "--target_norm is unset (recommended: the peak layer, 48 Qwen / 22 Mistral)")
    parser.add_argument("--quantize", default="none", choices=["none", "8bit", "4bit"])
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16"])
    parser.add_argument("--chat_style", default=None)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    out_dir = Path(args.out_dir)

    scored = pd.read_csv(Path(args.run_dir) / "scored.tsv", sep="\t")
    scored["citation_count"] = pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0)
    gt_dict = load_ground_truth(args.data_csv)
    meta = json.load(open(args.meta_json))

    vector_correct = load_pool(scored, meta["pool_paper_ids"]["vector_correct"])
    vector_hallucinated = load_pool(scored, meta["pool_paper_ids"]["vector_hallucinated"])
    eval_high_all = load_pool(scored, meta["pool_paper_ids"]["eval_high"])
    n = min(args.n_eval, len(eval_high_all))
    eval_pool = eval_high_all.sample(n=n, random_state=args.seed) if n > 0 else eval_high_all
    eval_pool = eval_pool.reset_index(drop=True)
    print(f"[stage18] pools — vector_correct={len(vector_correct)} "
          f"vector_hallucinated={len(vector_hallucinated)} eval={len(eval_pool)}")

    registry_cfg = detect_model_config(args.model_path)
    chat_style = args.chat_style or (registry_cfg["chat_style"] if registry_cfg else "chatml")
    dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16
    print(f"[stage18] loading model {args.model_path} (chat_style={chat_style!r})")
    model, tokenizer = load_model_and_tokenizer(args.model_path, dtype, args.quantize)
    device = next(model.parameters()).device
    decoder_layers = get_decoder_layers(model)
    n_layers = len(decoder_layers)
    layers = [L for L in args.layers if L < n_layers]
    if len(layers) != len(args.layers):
        dropped = sorted(set(args.layers) - set(layers))
        print(f"[stage18] WARNING: dropping out-of-range layers {dropped} for a {n_layers}-layer model")

    # ── Build a diff-of-means vector at every candidate layer, one pass each ─
    print(f"[stage18] extracting P1 at layers {layers} for vector pools (one forward pass per paper)")
    correct_by_layer: dict[int, list] = {L: [] for L in layers}
    hallu_by_layer: dict[int, list] = {L: [] for L in layers}
    for _, r in vector_correct.iterrows():
        d = extract_p1_multilayer(model, tokenizer, r["title"], r["year"], chat_style, device, layers)
        for L in layers:
            correct_by_layer[L].append(d[L])
    for _, r in vector_hallucinated.iterrows():
        d = extract_p1_multilayer(model, tokenizer, r["title"], r["year"], chat_style, device, layers)
        for L in layers:
            hallu_by_layer[L].append(d[L])

    vectors: dict[int, np.ndarray] = {}
    raw_norms: dict[int, float] = {}
    for L in layers:
        vec = np.stack(correct_by_layer[L]).mean(axis=0) - np.stack(hallu_by_layer[L]).mean(axis=0)
        vectors[L] = vec.astype(np.float32)
        raw_norms[L] = float(np.linalg.norm(vec))
        print(f"[stage18] layer {L}: raw vector norm={raw_norms[L]:.4f}")

    # Normalize every layer's vector to a COMMON norm so the sweep isolates
    # direction quality per layer, not per-layer magnitude. Raw diff-of-means
    # norms vary ~50-100x across layers; steering all of them at one alpha
    # would just inject wildly different magnitudes (deep high-norm layers
    # degenerate into garbage, low-norm early layers do nothing) — which tells
    # you about norm, not about which layer's direction is causally potent.
    if args.target_norm and args.target_norm > 0:
        target_norm = args.target_norm
    elif args.norm_ref_layer is not None and args.norm_ref_layer in raw_norms:
        target_norm = raw_norms[args.norm_ref_layer]
    else:
        target_norm = float(np.median(list(raw_norms.values())))
    print(f"[stage18] scaling all layer vectors to common norm {target_norm:.4f} "
          f"(effective injected magnitude = alpha*{target_norm:.4f})")
    for L in layers:
        if raw_norms[L] > 0:
            vectors[L] = (vectors[L] / raw_norms[L] * target_norm).astype(np.float32)

    # ── Baseline + per-layer induce steering on the same eval pool ──────────
    results_summary: list[dict] = []
    predictions: list[pd.DataFrame] = []

    def record(df: pd.DataFrame, **tags) -> None:
        if not df.empty:
            tagged = df.copy()
            for k, v in tags.items():
                tagged[k] = v
            predictions.append(tagged)
        results_summary.append(summarize_condition(df, **tags))

    depth_pct = {L: round(100.0 * L / (n_layers - 1), 1) for L in layers}

    print("[stage18] baseline (no steering)")
    df = run_condition(model, tokenizer, decoder_layers, layers[0], device, chat_style,
                       eval_pool, gt_dict, args.max_new_tokens, vector=None, alpha=0.0)
    record(df, layer=-1, layer_depth_pct=float("nan"), applied_vector_norm=0.0, raw_vector_norm=0.0,
           condition="baseline", direction="none", alpha=0.0)

    for L in layers:
        print(f"[stage18] induce steering at layer {L} (depth {depth_pct[L]}%), alpha={args.alpha}")
        df = run_condition(model, tokenizer, decoder_layers, L, device, chat_style,
                           eval_pool, gt_dict, args.max_new_tokens,
                           vector=-vectors[L], alpha=args.alpha)
        record(df, layer=L, layer_depth_pct=depth_pct[L],
               applied_vector_norm=round(target_norm, 4), raw_vector_norm=round(raw_norms[L], 4),
               condition="steering", direction="induce_toward_hallucinated", alpha=args.alpha)

    summary_df = pd.DataFrame(results_summary)
    summary_df.to_csv(out_dir / "layer_sweep_results.csv", index=False)
    print(f"[stage18] wrote {out_dir / 'layer_sweep_results.csv'}")

    if predictions:
        pd.concat(predictions, ignore_index=True).to_csv(
            out_dir / "layer_sweep_predictions.tsv", sep="\t", index=False)
        print(f"[stage18] wrote {out_dir / 'layer_sweep_predictions.tsv'}")

    meta_out = {
        "model_path": args.model_path,
        "layers": layers,
        "layer_depth_pct": depth_pct,
        "alpha": args.alpha,
        "n_eval": len(eval_pool),
        "common_target_norm": round(target_norm, 6),
        "effective_injected_magnitude": round(args.alpha * target_norm, 6),
        "raw_vector_norms": {str(L): round(raw_norms[L], 6) for L in layers},
        "eval_pool_paper_ids": eval_pool["paper_id"].astype(str).tolist(),
    }
    with open(out_dir / "layer_sweep_meta.json", "w") as f:
        json.dump(meta_out, f, indent=2)
    print(f"[stage18] wrote {out_dir / 'layer_sweep_meta.json'}")

    print("\n[stage18] === summary ===")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
