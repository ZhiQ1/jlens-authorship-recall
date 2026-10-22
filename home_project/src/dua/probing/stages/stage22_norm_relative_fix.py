"""Stage 22: a norm-relative fine sweep of the fix direction.

Every earlier fix run started at additive alpha = 1 with a push scaled to a
common norm across layers, which left alpha in (0,1) untested and confounded
the cross-layer comparison. Here the perturbation is a fraction of each token's
own residual norm, so sweeping that fraction is the fine alpha sweep in
norm-aware units. Arms stop early once output stops being valid text, and the
tripping point is recorded but flagged non-meaningful. Output is streamed, so a
wall-clock kill keeps everything computed so far.

Usage
─────
  python -m dua.probing.stages.stage22_norm_relative_fix \
      --model_path   /scratch/$USER/scholar_qwen/models/Qwen3-32B \
      --run_dir      /scratch/$USER/scholar_qwen/run_qwen3_32b \
      --data_csv     data/interim/probing_prompts_9108.csv \
      --meta_json    /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_meta.json \
      --layers       24 40 48 56 --peak_layer 48 \
      --bands        0.65:0.95 0.35:0.65 \
      --out_dir      /scratch/$USER/scholar_qwen/steering_qwen3_32b/norm_relative_fix
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(__file__))
from dua.probing.scholar_utils import score_authors
from stage1_generate import detect_model_config, load_model_and_tokenizer
from stage2_score import clean_generated_text, load_ground_truth
from stage14_activation_steering import (
    MAX_NEW_TOKENS,
    _MATCHER,
    build_input,
    generate_text,
    get_decoder_layers,
    is_degenerate,
    repetition_metrics,
    summarize_condition,
)
from stage17_graded_bin_steering import select_band_pool
from stage18_layer_sweep import extract_p1_multilayer, load_pool

RANDOM_SEED = 42
DEFAULT_FRACS = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8]

# Fixed column order for the streamed results CSV (tags + summarize_condition metrics).
SUMMARY_FIELDS = [
    "layer", "layer_depth_pct", "residual_norm", "raw_vector_norm",
    "condition", "direction", "frac", "flagged_degenerate",
    "n", "mean_hr2", "hallucination_rate_pct", "mean_output_tokens",
    "pct_degenerate", "pct_dup_names", "mean_type_token_ratio",
]


# ─────────────────────────────────────────────────────────────────────────────
# Norm-relative steering hook
# ─────────────────────────────────────────────────────────────────────────────

def make_norm_relative_hook(unit_vector: torch.Tensor, frac: float):
    """Add `frac * ||hidden_pos|| * unit_vector` to every token position.

    `unit_vector` must already be L2-normalised and SIGNED (fix: +dir,
    induce: -dir, control: random unit). The delta scales with each position's
    own residual norm and each layer's own scale — unlike the fixed additive
    push in stage14.make_steering_hook.
    """
    unit = None  # resolved lazily to hidden's device/dtype

    def hook(module, inputs, output):
        nonlocal unit
        hidden = output[0] if isinstance(output, tuple) else output
        if unit is None or unit.device != hidden.device or unit.dtype != hidden.dtype:
            unit = unit_vector.to(device=hidden.device, dtype=hidden.dtype)
        norm = hidden.norm(dim=-1, keepdim=True)          # (batch, seq, 1)
        hidden = hidden + frac * norm * unit               # unit broadcasts over (batch, seq)
        if isinstance(output, tuple):
            return (hidden,) + tuple(output[1:])
        return hidden

    return hook


# ─────────────────────────────────────────────────────────────────────────────
# Per-paper generation with the norm-relative hook (same path as Stages 14-21)
# ─────────────────────────────────────────────────────────────────────────────

def run_condition_normrel(model, tokenizer, decoder_layers, layer_idx: int, device,
                          chat_style: str, papers: pd.DataFrame, gt_dict: dict,
                          max_new_tokens: int, unit_vector: np.ndarray | None,
                          frac: float) -> pd.DataFrame:
    """Same per-row output schema as stage14.run_condition, using the
    norm-relative hook. One paper per model.generate call. `unit_vector` is the
    SIGNED unit direction (None for baseline)."""
    handle = None
    if unit_vector is not None and frac != 0.0:
        vec_t = torch.from_numpy(unit_vector.astype(np.float32))
        hook = make_norm_relative_hook(vec_t, frac)
        handle = decoder_layers[layer_idx].register_forward_hook(hook)
    rows = []
    try:
        for _, row in papers.iterrows():
            pid = row["paper_id"]
            gt = gt_dict.get(pid)
            if gt is None:
                continue
            raw_text = generate_text(
                model, tokenizer, row["title"], row["year"], chat_style, device, max_new_tokens
            )
            cleaned = clean_generated_text(raw_text)
            metrics = score_authors(gt["gt_authors"], cleaned, _MATCHER)
            rows.append({
                "paper_id": pid,
                "citation_count": row["citation_count"],
                "generated_text": raw_text,
                "hr2": metrics["hr2"],
                "n_output_tokens": len(tokenizer.encode(raw_text, add_special_tokens=False)),
                "degenerate": is_degenerate(raw_text),
                **repetition_metrics(raw_text),
            })
    finally:
        if handle is not None:
            handle.remove()
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Residual norm + degeneracy helpers
# ─────────────────────────────────────────────────────────────────────────────

@torch.no_grad()
def mean_residual_norms(model, tokenizer, papers: pd.DataFrame, chat_style: str,
                        device, layers: list[int]) -> dict[int, float]:
    """Mean per-position residual-stream L2 norm at each layer, averaged over
    prompt positions and papers. Used to (a) answer 'was additive alpha=1 an
    overshoot?' and (b) map frozen Stage 20 additive points onto the frac axis."""
    sums = {L: 0.0 for L in layers}
    n = 0
    for _, r in papers.iterrows():
        input_ids, attention_mask = build_input(tokenizer, r["title"], r["year"], chat_style, device)
        out = model(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
        for L in layers:
            h = out.hidden_states[L + 1][0]                     # (seq, dim)
            sums[L] += float(h.norm(dim=-1).mean().item())
        n += 1
    return {L: round(sums[L] / max(n, 1), 4) for L in layers}


def is_degenerate_summary(summ: dict, baseline_tokens: float, degen_pct: float,
                          ttr_min: float, token_mult: float) -> bool:
    """Has this condition's generation stopped being valid text? (design rule)"""
    if summ.get("n", 0) == 0:
        return False
    if summ["pct_degenerate"] >= degen_pct:
        return True
    if summ["mean_type_token_ratio"] < ttr_min:
        return True
    # baseline_tokens == baseline_tokens guards against NaN (empty baseline).
    if baseline_tokens and baseline_tokens == baseline_tokens \
            and summ["mean_output_tokens"] >= token_mult * baseline_tokens:
        return True
    return False


# ─────────────────────────────────────────────────────────────────────────────

def parse_bands(band_strs: list[str]) -> list[tuple[float, float]]:
    bands = []
    for s in band_strs:
        lo, hi = s.split(":")
        bands.append((float(lo), float(hi)))
    return bands


def unit(vec: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(vec))
    return (vec / n).astype(np.float32) if n > 0 else vec.astype(np.float32)


def order_layers_peak_first(layers: list[int], peak: int | None) -> list[int]:
    """Peak layer first (most decision-relevant if the job is cut off), then the
    rest ascending."""
    if peak is not None and peak in layers:
        return [peak] + [L for L in sorted(layers) if L != peak]
    return sorted(layers)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 22: norm-relative fine fix sweep")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--run_dir", required=True)
    parser.add_argument("--data_csv", required=True)
    parser.add_argument("--meta_json", required=True,
                        help="steering_meta.json from the completed Stage 14 run (vector pool IDs)")
    parser.add_argument("--layers", type=int, nargs="+", required=True,
                        help="Non-final decoder layers to sweep (Qwen 24 40 48 56; Mistral 10 22 28 36)")
    parser.add_argument("--peak_layer", type=int, default=None,
                        help="Probe-peak layer (48 Qwen / 22 Mistral) — run first + highlighted in meta")
    parser.add_argument("--bands", nargs="+", default=["0.65:0.95", "0.35:0.65"],
                        help="HR2 headroom bands as lo:hi (open-lo, closed-hi). Primary first.")
    parser.add_argument("--fracs", type=float, nargs="+", default=DEFAULT_FRACS,
                        help="Norm-relative fractions, ascending (dense-low + high tail)")
    parser.add_argument("--n_eval", type=int, default=30)
    parser.add_argument("--max_new_tokens", type=int, default=MAX_NEW_TOKENS)
    parser.add_argument("--degen_pct", type=float, default=50.0)
    parser.add_argument("--ttr_min", type=float, default=0.6)
    parser.add_argument("--token_mult", type=float, default=2.0)
    parser.add_argument("--quantize", default="none", choices=["none", "8bit", "4bit"])
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16"])
    parser.add_argument("--chat_style", default=None)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    out_dir = Path(args.out_dir)
    bands = parse_bands(args.bands)
    fracs = sorted(args.fracs)  # ascending, so degeneracy early-stop is well-defined

    scored = pd.read_csv(Path(args.run_dir) / "scored.tsv", sep="\t")
    scored["citation_count"] = pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0)
    gt_dict = load_ground_truth(args.data_csv)
    meta = json.load(open(args.meta_json))

    vector_correct = load_pool(scored, meta["pool_paper_ids"]["vector_correct"])
    vector_hallucinated = load_pool(scored, meta["pool_paper_ids"]["vector_hallucinated"])

    registry_cfg = detect_model_config(args.model_path)
    chat_style = args.chat_style or (registry_cfg["chat_style"] if registry_cfg else "chatml")
    dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16
    print(f"[stage22] loading model {args.model_path} (chat_style={chat_style!r})")
    model, tokenizer = load_model_and_tokenizer(args.model_path, dtype, args.quantize)
    device = next(model.parameters()).device
    decoder_layers = get_decoder_layers(model)
    n_layers = len(decoder_layers)
    layers = [L for L in args.layers if L < n_layers]
    if len(layers) != len(args.layers):
        dropped = sorted(set(args.layers) - set(layers))
        print(f"[stage22] WARNING: dropping out-of-range layers {dropped} for a {n_layers}-layer model")
    if n_layers - 1 in layers:
        print(f"[stage22] WARNING: final layer {n_layers - 1} is in the sweep set — last-layer "
              "steering degenerates to a per-token logit nudge; exclude it.")
    layers = order_layers_peak_first(layers, args.peak_layer)
    print(f"[stage22] layer order (peak first): {layers}")

    # ── Build per-layer diff-of-means (fix = correct-mean − hallucinated-mean) ──
    print(f"[stage22] extracting P1 at layers {sorted(layers)} for vector pools "
          f"(correct={len(vector_correct)}, hallucinated={len(vector_hallucinated)})")
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

    unit_fix = {}
    raw_norms = {}
    unit_rand = {}
    rng = np.random.RandomState(args.seed)
    dim = None
    for L in sorted(layers):
        vec = np.stack(correct_by_layer[L]).mean(axis=0) - np.stack(hallu_by_layer[L]).mean(axis=0)
        raw_norms[L] = round(float(np.linalg.norm(vec)), 6)
        unit_fix[L] = unit(vec)
        dim = unit_fix[L].shape[0]
        unit_rand[L] = unit(rng.randn(dim).astype(np.float32))
        print(f"[stage22] layer {L}: raw diff-of-means norm={raw_norms[L]}")

    depth_pct = {L: round(100.0 * L / (n_layers - 1), 1) for L in layers}

    # ── Sweep, per band (primary band first) ────────────────────────────────
    for lo, hi in bands:
        band_tag = f"hr2_{lo}_{hi}"
        eval_pool = select_band_pool(scored, meta, lo, hi, args.n_eval, args.seed)
        print(f"[stage22] band ({lo},{hi}] eval pool n={len(eval_pool)}")
        if eval_pool.empty:
            print(f"[stage22] band ({lo},{hi}] empty after disjointness exclusion — skipping")
            continue

        resid_norms = mean_residual_norms(model, tokenizer, eval_pool, chat_style, device, layers)
        print(f"[stage22] mean residual norms per layer: {resid_norms}")

        # Meta written UP FRONT so it survives a wall-clock kill mid-sweep.
        meta_out = {
            "model_path": args.model_path,
            "layers": sorted(layers),
            "layer_order_run": layers,
            "peak_layer": args.peak_layer,
            "layer_depth_pct": depth_pct,
            "fracs": fracs,
            "hr2_band": [lo, hi],
            "n_eval": len(eval_pool),
            "generation": "per_paper",
            "max_new_tokens": args.max_new_tokens,
            "mean_residual_norm_by_layer": resid_norms,
            "raw_diff_of_means_norm_by_layer": raw_norms,
            "degeneracy_rule": {"degen_pct": args.degen_pct, "ttr_min": args.ttr_min,
                                "token_mult": args.token_mult},
            "eval_pool_paper_ids": list(eval_pool["paper_id"].astype(str)),
            "note": ("delta = frac * ||hidden_pos|| * signed_unit_dir; frozen Stage 20 "
                     "additive alpha maps here via frac ~= alpha*target_norm/residual_norm "
                     "(per layer). Results are streamed; a partial file is valid."),
        }
        with open(out_dir / f"norm_relative_fix_meta_{band_tag}.json", "w") as f:
            json.dump(meta_out, f, indent=2)
        print(f"[stage22] wrote meta {out_dir / f'norm_relative_fix_meta_{band_tag}.json'}")

        # Streamed outputs: flush after every condition so a kill keeps them.
        res_path = out_dir / f"norm_relative_fix_results_{band_tag}.csv"
        pred_path = out_dir / f"norm_relative_fix_predictions_{band_tag}.tsv"
        res_f = open(res_path, "w", newline="")
        writer = csv.DictWriter(res_f, fieldnames=SUMMARY_FIELDS, extrasaction="ignore")
        writer.writeheader()
        res_f.flush()
        pred_state = {"header_written": False}

        def write_row(df: pd.DataFrame, tags: dict) -> dict:
            summ = summarize_condition(df, **tags)
            writer.writerow({k: summ.get(k, "") for k in SUMMARY_FIELDS})
            res_f.flush()
            if not df.empty:
                tagged = df.copy()
                for k, v in tags.items():
                    tagged[k] = v
                tagged.to_csv(pred_path, sep="\t", index=False, mode="a",
                              header=not pred_state["header_written"])
                pred_state["header_written"] = True
            return summ

        try:
            # Baseline (no steering) — runs first, always retained.
            print(f"[stage22] baseline (no steering), band ({lo},{hi}]")
            base_df = run_condition_normrel(model, tokenizer, decoder_layers, layers[0], device,
                                            chat_style, eval_pool, gt_dict, args.max_new_tokens,
                                            unit_vector=None, frac=0.0)
            base_summ = write_row(base_df, dict(
                layer=-1, layer_depth_pct=float("nan"), residual_norm=float("nan"),
                raw_vector_norm=0.0, condition="baseline", direction="none", frac=0.0,
                flagged_degenerate=False))
            baseline_tokens = base_summ["mean_output_tokens"]

            # Per layer (peak first) × arm (fix first), frac ascending w/ early-stop.
            for L in layers:
                arms = [
                    ("fix", "toward_cited", unit_fix[L]),
                    ("induce", "toward_hallucinated", -unit_fix[L]),
                    ("control_norm_matched", "toward_cited", unit_rand[L]),
                ]
                for condition, direction, signed_unit in arms:
                    for frac in fracs:
                        print(f"[stage22] {condition} L{L} (depth {depth_pct[L]}%) frac={frac}")
                        df = run_condition_normrel(
                            model, tokenizer, decoder_layers, L, device, chat_style,
                            eval_pool, gt_dict, args.max_new_tokens,
                            unit_vector=signed_unit, frac=frac)
                        probe = summarize_condition(df, layer=L)
                        flagged = is_degenerate_summary(probe, baseline_tokens, args.degen_pct,
                                                        args.ttr_min, args.token_mult)
                        write_row(df, dict(
                            layer=L, layer_depth_pct=depth_pct[L], residual_norm=resid_norms[L],
                            raw_vector_norm=raw_norms[L], condition=condition, direction=direction,
                            frac=frac, flagged_degenerate=flagged))
                        if flagged:
                            print(f"[stage22]   -> degeneracy tripped at frac={frac} "
                                  f"(hr%={probe['hallucination_rate_pct']}, "
                                  f"ttr={probe['mean_type_token_ratio']}, "
                                  f"tok={probe['mean_output_tokens']}); stopping this arm.")
                            break
        finally:
            res_f.close()
        print(f"[stage22] band ({lo},{hi}] done — wrote {res_path} and {pred_path}")


if __name__ == "__main__":
    main()
