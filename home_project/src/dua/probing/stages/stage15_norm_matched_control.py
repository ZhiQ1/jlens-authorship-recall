"""Stage 15: a norm-matched random-direction control for Stage 14.

Stage 14's shuffled-label control turned out to have 7-8x smaller norm than the
real steering vector -- relabelling averages a real group difference away -- so
it was a weaker perturbation, not a same-magnitude one, and it never ran on
eval_high where the effect is. This builds one genuinely random direction
scaled to the real vector's norm exactly, runs it on both pools at the same
alphas, and regenerates its own baseline so the comparison is self-contained.

Usage
─────
  python -m dua.probing.stages.stage15_norm_matched_control \
      --model_path   Qwen/Qwen3-32B \
      --run_dir      /scratch/$USER/scholar_qwen/run_qwen3_32b \
      --data_csv     data/interim/probing_prompts_9108.csv \
      --layer        48 \
      --meta_json    /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_meta.json \
      --steering_vector_path /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_vector.npy \
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

RANDOM_SEED = 42


def load_pool(scored: pd.DataFrame, paper_ids: list[str]) -> pd.DataFrame:
    ids = set(paper_ids)
    pool = scored[scored["paper_id"].isin(ids)].reset_index(drop=True)
    missing = ids - set(pool["paper_id"])
    if missing:
        print(f"[stage15] WARNING: {len(missing)}/{len(ids)} paper_ids from meta_json "
              f"not found in this run's scored.tsv (dataset drift?) — continuing with {len(pool)}")
    return pool


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 15: norm-matched random-direction control")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--run_dir", required=True)
    parser.add_argument("--data_csv", required=True)
    parser.add_argument("--layer", type=int, required=True)
    parser.add_argument("--meta_json", required=True,
                        help="steering_meta.json from the completed Stage 14 run for this model")
    parser.add_argument("--steering_vector_path", required=True,
                        help="steering_vector.npy from the completed Stage 14 run for this model")
    parser.add_argument("--alphas", type=float, nargs="+", default=[1.0, 2.0])
    parser.add_argument("--max_new_tokens", type=int, default=MAX_NEW_TOKENS)
    parser.add_argument("--quantize", default="none", choices=["none", "8bit", "4bit"])
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16"])
    parser.add_argument("--chat_style", default=None)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    out_dir = Path(args.out_dir)

    print(f"[stage15] loading {args.meta_json}")
    meta = json.load(open(args.meta_json))
    pool_paper_ids = meta["pool_paper_ids"]

    steering_vector = np.load(args.steering_vector_path)
    ref_norm = float(np.linalg.norm(steering_vector))
    print(f"[stage15] reference steering vector: dim={steering_vector.shape[0]} norm={ref_norm:.4f}")

    random_vector = build_random_norm_matched_vector(
        dim=steering_vector.shape[0], target_norm=ref_norm, seed=args.seed
    )
    print(f"[stage15] built random norm-matched control: norm={np.linalg.norm(random_vector):.4f} "
          f"(target {ref_norm:.4f})")

    scored_path = Path(args.run_dir) / "scored.tsv"
    print(f"[stage15] loading {scored_path}")
    scored = pd.read_csv(scored_path, sep="\t")
    scored["citation_count"] = pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0)

    print(f"[stage15] loading ground truth: {args.data_csv}")
    gt_dict = load_ground_truth(args.data_csv)

    eval_low = load_pool(scored, pool_paper_ids["eval_low"])
    eval_high = load_pool(scored, pool_paper_ids["eval_high"])
    print(f"[stage15] eval_low n={len(eval_low)}  eval_high n={len(eval_high)}")

    registry_cfg = detect_model_config(args.model_path)
    chat_style = args.chat_style or (registry_cfg["chat_style"] if registry_cfg else "chatml")
    dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16
    print(f"[stage15] loading model {args.model_path} (chat_style={chat_style!r})")
    model, tokenizer = load_model_and_tokenizer(args.model_path, dtype, args.quantize)
    device = next(model.parameters()).device
    decoder_layers = get_decoder_layers(model)
    if args.layer >= len(decoder_layers):
        raise ValueError(f"--layer {args.layer} out of range for a {len(decoder_layers)}-layer model")

    results_summary: list[dict] = []
    predictions: list[pd.DataFrame] = []

    def record(df: pd.DataFrame, **tags) -> None:
        if not df.empty:
            tagged = df.copy()
            for k, v in tags.items():
                tagged[k] = v
            predictions.append(tagged)
        results_summary.append(summarize_condition(df, **tags))

    for pool_name, pool_df in [("eval_low", eval_low), ("eval_high", eval_high)]:
        print(f"[stage15] === {pool_name}: fresh baseline (no steering) ===")
        df = run_condition(model, tokenizer, decoder_layers, args.layer, device, chat_style,
                            pool_df, gt_dict, args.max_new_tokens, vector=None, alpha=0.0)
        record(df, pool=pool_name, condition="baseline_refresh", direction="none", alpha=0.0)

        for alpha in args.alphas:
            print(f"[stage15] === {pool_name}: random norm-matched control, alpha={alpha} ===")
            df = run_condition(model, tokenizer, decoder_layers, args.layer, device, chat_style,
                                pool_df, gt_dict, args.max_new_tokens,
                                vector=random_vector, alpha=alpha)
            record(df, pool=pool_name, condition="random_norm_matched_control",
                   direction="random", alpha=alpha)

    summary_df = pd.DataFrame(results_summary)
    summary_df.to_csv(out_dir / "steering_results_norm_matched_control.csv", index=False)
    print(f"[stage15] wrote {out_dir / 'steering_results_norm_matched_control.csv'}")

    if predictions:
        pd.concat(predictions, ignore_index=True).to_csv(
            out_dir / "steering_predictions_norm_matched_control.tsv", sep="\t", index=False
        )
        print(f"[stage15] wrote {out_dir / 'steering_predictions_norm_matched_control.tsv'}")

    np.save(out_dir / "random_norm_matched_control_vector.npy", random_vector)
    control_meta = {
        "reference_steering_vector_path": args.steering_vector_path,
        "reference_norm": ref_norm,
        "random_control_norm": float(np.linalg.norm(random_vector)),
        "seed": args.seed,
        "alphas": args.alphas,
        "layer": args.layer,
        "pool_sizes": {"eval_low": len(eval_low), "eval_high": len(eval_high)},
    }
    with open(out_dir / "norm_matched_control_meta.json", "w") as f:
        json.dump(control_meta, f, indent=2)
    print(f"[stage15] wrote {out_dir / 'norm_matched_control_meta.json'}")

    print("\n[stage15] === summary ===")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
