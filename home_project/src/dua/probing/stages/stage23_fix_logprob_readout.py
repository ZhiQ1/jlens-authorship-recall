"""Stage 23: a sensitive readout for the fix null, plus a positive control.

Greedy scoring cannot see a fix that raises p(correct authors) from 2% to 35%,
because argmax never flips. ``fix_readout`` measures the change in mean gold
log-prob under the fix hook instead, against baseline and a norm-matched random
direction. ``positive_control`` establishes that the apparatus can detect
recovery at all: degrade well-attributed papers with title noise, then test
whether the fix hook restores any gold log-prob.

**The E1/E2 readout was invalidated by a contamination artifact found during
development.** Do not cite it without the prompt-only re-run. Nothing in the
camera-ready depends on it.

Usage
─────
  python -m dua.probing.stages.stage23_fix_logprob_readout \
      --model_path   /scratch/$USER/scholar_qwen/models/Qwen3-32B \
      --run_dir      /scratch/$USER/scholar_qwen/run_qwen3_32b \
      --data_csv     data/interim/probing_prompts_9108.csv \
      --meta_json    /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_meta.json \
      --layers       24 40 48 56 --peak_layer 48 \
      --bands        0.65:0.95 0.35:0.65 \
      --mode         both \
      --out_dir      /scratch/$USER/scholar_qwen/steering_qwen3_32b/fix_logprob_readout
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
from stage1_generate import detect_model_config, load_model_and_tokenizer
from stage2_score import load_ground_truth
from stage14_activation_steering import (
    build_input,
    build_random_norm_matched_vector,
    get_decoder_layers,
    make_steering_hook,
)
from stage17_graded_bin_steering import select_band_pool
from stage18_layer_sweep import extract_p1_multilayer, load_pool
from stage19_causal_tracing import locate_title_token_span, teacher_forced_gold_logprob
from stage22_norm_relative_fix import make_norm_relative_hook, order_layers_peak_first, unit

RANDOM_SEED = 42
DEFAULT_ALPHAS = [0.5, 1.0, 2.0]
DEFAULT_FRACS = [0.02, 0.05, 0.1, 0.2]


# ─────────────────────────────────────────────────────────────────────────────
# Gold-log-prob under an arbitrary steering hook (forward-pass only)
# ─────────────────────────────────────────────────────────────────────────────

def make_hook(param: str, signed_vec: np.ndarray, magnitude: float):
    """Return the steering hook for one arm.

    param='additive'  -> stage14 make_steering_hook(vec, alpha=magnitude);
                          `signed_vec` is the full (norm-carrying) signed vector.
    param='normrel'   -> stage22 make_norm_relative_hook(unit, frac=magnitude);
                          `signed_vec` is the signed UNIT direction.
    """
    vec_t = torch.from_numpy(signed_vec.astype(np.float32))
    if param == "additive":
        return make_steering_hook(vec_t, magnitude)
    if param == "normrel":
        return make_norm_relative_hook(vec_t, magnitude)
    raise ValueError(f"unknown param {param!r}")


@torch.no_grad()
def gold_logprob_hooked(model, decoder_layers, embeds, attn, prompt_len, gold_ids,
                        layer_idx: int | None, hook) -> float:
    """Mean per-token gold log-prob, teacher-forced, with `hook` (if given)
    registered at layer `layer_idx` for the forward pass. Delegates the actual
    log-prob math to stage19.teacher_forced_gold_logprob (restore=None) so the
    two stages compute the readout identically; the steering hook stacks with
    that call's (absent) restore hook."""
    handle = None
    if hook is not None:
        handle = decoder_layers[layer_idx].register_forward_hook(hook)
    try:
        return teacher_forced_gold_logprob(model, decoder_layers, embeds, attn,
                                           prompt_len, gold_ids, restore=None)
    finally:
        if handle is not None:
            handle.remove()


# ─────────────────────────────────────────────────────────────────────────────
# Per-layer diff-of-means vectors (fix = correct-mean − hallucinated-mean)
# ─────────────────────────────────────────────────────────────────────────────

def build_layer_vectors(model, tokenizer, chat_style, device, layers,
                        vector_correct, vector_hallucinated, seed):
    """Returns (raw_diff[L], unit_dir[L], rand_full[L], rand_unit[L]) per layer.

    raw_diff  : diff-of-means vector (norm-carrying) — the additive fix vector.
    unit_dir  : its L2-normalised direction — the norm-relative fix direction.
    rand_full : a random vector norm-matched to raw_diff — additive control.
    rand_unit : a random unit vector — norm-relative control.
    Both randoms use one seed per layer (E4 in Stage 24 adds multi-seed spread
    on the generation side; here a single control draw is enough for the
    log-prob readout, which is far less noisy than greedy HR2)."""
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

    raw_diff, unit_dir, rand_full, rand_unit = {}, {}, {}, {}
    rng = np.random.RandomState(seed)
    for L in sorted(layers):
        vec = np.stack(correct_by_layer[L]).mean(axis=0) - np.stack(hallu_by_layer[L]).mean(axis=0)
        raw_diff[L] = vec.astype(np.float32)
        unit_dir[L] = unit(vec)
        rand_full[L] = build_random_norm_matched_vector(vec.shape[0], float(np.linalg.norm(vec)),
                                                        seed=seed + 1000 + L)
        rand_unit[L] = unit(rng.randn(vec.shape[0]).astype(np.float32))
    return raw_diff, unit_dir, rand_full, rand_unit


# ─────────────────────────────────────────────────────────────────────────────
# Aggregation
# ─────────────────────────────────────────────────────────────────────────────

def summarize(values: list[float]) -> dict:
    """Mean/sd/n + fraction positive of a per-paper delta (or recovery) list."""
    a = np.asarray([v for v in values if v == v], dtype=float)  # drop NaN
    if a.size == 0:
        return {"n": 0, "mean": float("nan"), "sd": float("nan"),
                "median": float("nan"), "frac_positive": float("nan")}
    sd = float(a.std(ddof=1)) if a.size > 1 else 0.0
    return {"n": int(a.size), "mean": round(float(a.mean()), 5), "sd": round(sd, 5),
            "median": round(float(np.median(a)), 5),
            "frac_positive": round(float((a > 0).mean()), 4)}


# ─────────────────────────────────────────────────────────────────────────────
# E1 — fix gold-log-prob readout on the HR2-headroom bands
# ─────────────────────────────────────────────────────────────────────────────

def run_fix_readout(model, tokenizer, decoder_layers, chat_style, device, out_dir: Path,
                    scored, meta, gt_dict, args, layers, raw_diff, unit_dir, rand_full,
                    rand_unit, depth_pct, embed_layer):
    """Per (band, layer, param, arm, magnitude): mean gold-log-prob under the
    steering hook, paired per-paper against the no-hook baseline. Streamed."""
    arms_additive = [("fix", "+vector"), ("induce", "-vector"), ("control", "random")]
    per_paper_path = out_dir / "fix_readout_per_paper.tsv"
    summary_rows: list[dict] = []
    pp_header_written = False

    for lo, hi in args.bands:
        band_tag = f"hr2_{lo}_{hi}"
        pool = select_band_pool(scored, meta, lo, hi, args.n_eval, args.seed)
        print(f"[stage23] fix_readout band ({lo},{hi}]: n={len(pool)}")
        if pool.empty:
            continue

        # Precompute per-paper baseline gold log-prob (no hook) once.
        base_lp: dict = {}
        seqs: dict = {}
        for _, row in pool.iterrows():
            pid = row["paper_id"]
            gt = gt_dict.get(pid)
            if gt is None:
                continue
            gold_ids = tokenizer.encode(str(gt["gt_authors"]), add_special_tokens=False)[: args.max_gold_tokens]
            if not gold_ids:
                continue
            prompt_ids, _ = build_input(tokenizer, row["title"], row["year"], chat_style, device)
            prompt_len = prompt_ids.shape[1]
            gold_t = torch.tensor([gold_ids], dtype=torch.long, device=device)
            seq_ids = torch.cat([prompt_ids, gold_t], dim=1)
            attn = torch.ones_like(seq_ids)
            embeds = embed_layer(seq_ids)
            lp = gold_logprob_hooked(model, decoder_layers, embeds, attn, prompt_len, gold_ids,
                                     None, None)
            base_lp[pid] = lp
            seqs[pid] = (embeds, attn, prompt_len, gold_ids)
        print(f"[stage23]   baseline gold log-prob computed for {len(base_lp)} papers")

        for L in layers:
            for param, grid in (("additive", args.alphas), ("normrel", args.fracs)):
                vec_for = {"fix": raw_diff[L] if param == "additive" else unit_dir[L],
                           "control": rand_full[L] if param == "additive" else rand_unit[L]}
                vec_for["induce"] = -vec_for["fix"]
                for arm, _desc in arms_additive:
                    for mag in grid:
                        deltas = []
                        for pid, (embeds, attn, plen, gold_ids) in seqs.items():
                            hook = make_hook(param, vec_for[arm], mag)
                            lp = gold_logprob_hooked(model, decoder_layers, embeds, attn, plen,
                                                     gold_ids, L, hook)
                            d = lp - base_lp[pid]
                            deltas.append(d)
                            row = {"band": band_tag, "layer": L, "param": param, "arm": arm,
                                   "magnitude": mag, "paper_id": pid,
                                   "baseline_logprob": round(base_lp[pid], 5),
                                   "steered_logprob": round(lp, 5), "delta_logprob": round(d, 5)}
                            pd.DataFrame([row]).to_csv(per_paper_path, sep="\t", index=False,
                                                       mode="a", header=not pp_header_written)
                            pp_header_written = True
                        s = summarize(deltas)
                        summary_rows.append({"band": band_tag, "layer": L,
                                             "layer_depth_pct": depth_pct[L], "param": param,
                                             "arm": arm, "magnitude": mag, **{f"delta_{k}": v
                                             for k, v in s.items()}})
                        print(f"[stage23]   {band_tag} L{L} {param} {arm} mag={mag}: "
                              f"mean Δlogprob={s['mean']} (n={s['n']}, frac+={s['frac_positive']})")
                        pd.DataFrame(summary_rows).to_csv(out_dir / "fix_readout_summary.csv", index=False)
    print(f"[stage23] wrote {out_dir / 'fix_readout_summary.csv'} and {per_paper_path}")


# ─────────────────────────────────────────────────────────────────────────────
# E2 — positive control: noise-degrade eval_high, then steer to recover
# ─────────────────────────────────────────────────────────────────────────────

def run_positive_control(model, tokenizer, decoder_layers, chat_style, device, out_dir: Path,
                         scored, meta, gt_dict, args, layers, raw_diff, unit_dir, rand_full,
                         rand_unit, depth_pct, embed_layer):
    """Corrupt title-token embeddings (Stage 19 protocol), then apply the fix
    steering hook on the corrupted forward and measure gold-log-prob recovery.
    recovery = (restored − corrupt) / (clean − corrupt). Compares fix vs a
    norm-matched random direction — the apparatus has detection power iff fix
    recovers more than the random control."""
    eval_all = load_pool(scored, meta["pool_paper_ids"]["eval_high"])
    n = min(args.n_eval, len(eval_all))
    eval_pool = (eval_all.sample(n=n, random_state=args.seed) if n > 0 else eval_all).reset_index(drop=True)
    print(f"[stage23] positive_control eval_high pool: {len(eval_all)} available, using {len(eval_pool)}")

    emb_std = float(embed_layer.weight.float().std().item())
    sigma = args.noise_scale * emb_std
    print(f"[stage23] emb std={emb_std:.5f}  noise sigma={sigma:.5f} ({args.noise_scale}x)  "
          f"n_noise={args.n_noise}")

    per_paper_path = out_dir / "positive_control_per_paper.tsv"
    summary_rows: list[dict] = []
    pp_header_written = False
    n_skip_locate = 0
    n_skip_gap = 0

    # recov[(L,param,arm,mag)] -> list of per-paper mean recoveries
    recov: dict = {}

    for pi, (_, row) in enumerate(eval_pool.iterrows()):
        pid = row["paper_id"]
        gt = gt_dict.get(pid)
        if gt is None:
            continue
        gold_ids = tokenizer.encode(str(gt["gt_authors"]), add_special_tokens=False)[: args.max_gold_tokens]
        if not gold_ids:
            continue
        prompt_ids, _ = build_input(tokenizer, row["title"], row["year"], chat_style, device)
        span = locate_title_token_span(tokenizer, prompt_ids, str(row["title"]))
        if span is None:
            n_skip_locate += 1
            continue
        prompt_len = prompt_ids.shape[1]
        gold_t = torch.tensor([gold_ids], dtype=torch.long, device=device)
        seq_ids = torch.cat([prompt_ids, gold_t], dim=1)
        attn = torch.ones_like(seq_ids)
        base_embeds = embed_layer(seq_ids)

        clean_lp = gold_logprob_hooked(model, decoder_layers, base_embeds, attn, prompt_len,
                                       gold_ids, None, None)

        # accumulators per condition for this paper (averaged over noise draws)
        paper_recov: dict = {}
        used_draws = 0
        for s in range(args.n_noise):
            g = torch.Generator().manual_seed(args.seed + 1000 * pi + s)
            noise = torch.randn(len(span), base_embeds.shape[-1], generator=g).to(
                device=device, dtype=base_embeds.dtype) * sigma
            noised = base_embeds.clone()
            noised[0, span, :] = noised[0, span, :] + noise

            corrupt_lp = gold_logprob_hooked(model, decoder_layers, noised, attn, prompt_len,
                                             gold_ids, None, None)
            gap = clean_lp - corrupt_lp
            if gap < args.min_gap:
                continue  # this draw didn't degrade; uninformative
            used_draws += 1
            for L in layers:
                for param, grid in (("additive", args.alphas), ("normrel", args.fracs)):
                    vec_for = {"fix": raw_diff[L] if param == "additive" else unit_dir[L],
                               "control": rand_full[L] if param == "additive" else rand_unit[L]}
                    for arm in ("fix", "control"):
                        for mag in grid:
                            hook = make_hook(param, vec_for[arm], mag)
                            restored_lp = gold_logprob_hooked(model, decoder_layers, noised, attn,
                                                              prompt_len, gold_ids, L, hook)
                            r = (restored_lp - corrupt_lp) / gap
                            paper_recov.setdefault((L, param, arm, mag), []).append(r)

        if used_draws == 0:
            n_skip_gap += 1
            continue

        for key, vals in paper_recov.items():
            L, param, arm, mag = key
            mean_r = float(np.mean(vals))
            recov.setdefault(key, []).append(mean_r)
            rec_row = {"paper_id": pid, "layer": L, "param": param, "arm": arm, "magnitude": mag,
                       "clean_logprob": round(clean_lp, 5), "n_noise_used": used_draws,
                       "recovery": round(mean_r, 5)}
            pd.DataFrame([rec_row]).to_csv(per_paper_path, sep="\t", index=False, mode="a",
                                           header=not pp_header_written)
            pp_header_written = True
        if (pi + 1) % 5 == 0 or pi == len(eval_pool) - 1:
            print(f"[stage23]   traced {pi + 1}/{len(eval_pool)} "
                  f"(skip_locate {n_skip_locate}, skip_gap {n_skip_gap})")

    for key, vals in sorted(recov.items()):
        L, param, arm, mag = key
        s = summarize(vals)
        summary_rows.append({"layer": L, "layer_depth_pct": depth_pct[L], "param": param,
                             "arm": arm, "magnitude": mag,
                             **{f"recovery_{k}": v for k, v in s.items()}})
    summ_df = pd.DataFrame(summary_rows)
    summ_df.to_csv(out_dir / "positive_control_summary.csv", index=False)
    print(f"[stage23] wrote {out_dir / 'positive_control_summary.csv'} and {per_paper_path}")
    if not summ_df.empty:
        print("\n[stage23] === positive-control recovery (fix should beat control if apparatus has power) ===")
        print(summ_df.to_string(index=False))


# ─────────────────────────────────────────────────────────────────────────────

def parse_bands(band_strs):
    out = []
    for s in band_strs:
        lo, hi = s.split(":")
        out.append((float(lo), float(hi)))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 23: fix gold-log-prob readout + positive control")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--run_dir", required=True)
    parser.add_argument("--data_csv", required=True)
    parser.add_argument("--meta_json", required=True,
                        help="steering_meta.json from a completed Stage 14 run (pools + disjointness)")
    parser.add_argument("--layers", type=int, nargs="+", required=True,
                        help="Non-final decoder layers (Qwen 24 40 48 56; Mistral 10 22 28 36)")
    parser.add_argument("--peak_layer", type=int, default=None, help="run/report first")
    parser.add_argument("--mode", choices=["fix_readout", "positive_control", "both"], default="both")
    parser.add_argument("--bands", nargs="+", default=["0.65:0.95", "0.35:0.65"],
                        help="HR2 headroom bands lo:hi for the fix readout (E1)")
    parser.add_argument("--alphas", type=float, nargs="+", default=DEFAULT_ALPHAS,
                        help="additive-parametrization magnitudes")
    parser.add_argument("--fracs", type=float, nargs="+", default=DEFAULT_FRACS,
                        help="norm-relative-parametrization magnitudes")
    parser.add_argument("--n_eval", type=int, default=40)
    parser.add_argument("--n_noise", type=int, default=5, help="positive-control noise draws/paper")
    parser.add_argument("--noise_scale", type=float, default=3.0,
                        help="positive-control noise sigma = scale * emb-std; Qwen3-32B needs 8")
    parser.add_argument("--min_gap", type=float, default=0.05,
                        help="min clean−corrupt gold log-prob gap (nats) for a noise draw to count")
    parser.add_argument("--max_gold_tokens", type=int, default=64)
    parser.add_argument("--quantize", default="none", choices=["none", "8bit", "4bit"])
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16"])
    parser.add_argument("--chat_style", default=None)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--out_dir", required=True)
    args = parser.parse_args()
    args.bands = parse_bands(args.bands)

    os.makedirs(args.out_dir, exist_ok=True)
    out_dir = Path(args.out_dir)

    scored = pd.read_csv(Path(args.run_dir) / "scored.tsv", sep="\t")
    scored["citation_count"] = pd.to_numeric(scored["citation_count"], errors="coerce").fillna(0)
    scored["hr2"] = pd.to_numeric(scored["hr2"], errors="coerce")
    gt_dict = load_ground_truth(args.data_csv)
    meta = json.load(open(args.meta_json))

    registry_cfg = detect_model_config(args.model_path)
    chat_style = args.chat_style or (registry_cfg["chat_style"] if registry_cfg else "chatml")
    dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16
    print(f"[stage23] loading model {args.model_path} (chat_style={chat_style!r})")
    model, tokenizer = load_model_and_tokenizer(args.model_path, dtype, args.quantize)
    device = next(model.parameters()).device
    decoder_layers = get_decoder_layers(model)
    n_layers = len(decoder_layers)
    layers = [L for L in args.layers if L < n_layers]
    if len(layers) != len(args.layers):
        dropped = sorted(set(args.layers) - set(layers))
        print(f"[stage23] WARNING: dropping out-of-range layers {dropped} for a {n_layers}-layer model")
    if n_layers - 1 in layers:
        print(f"[stage23] WARNING: final layer {n_layers - 1} is in the sweep set — last-layer "
              "steering degenerates to a per-token logit nudge; exclude it.")
    layers = order_layers_peak_first(layers, args.peak_layer)
    depth_pct = {L: round(100.0 * L / (n_layers - 1), 1) for L in layers}
    embed_layer = model.get_input_embeddings()

    vector_correct = load_pool(scored, meta["pool_paper_ids"]["vector_correct"])
    vector_hallucinated = load_pool(scored, meta["pool_paper_ids"]["vector_hallucinated"])
    print(f"[stage23] building per-layer diff-of-means vectors at {sorted(layers)} "
          f"(correct={len(vector_correct)}, hallucinated={len(vector_hallucinated)})")
    raw_diff, unit_dir, rand_full, rand_unit = build_layer_vectors(
        model, tokenizer, chat_style, device, layers, vector_correct, vector_hallucinated, args.seed)
    for L in sorted(layers):
        print(f"[stage23]   layer {L}: raw diff-of-means norm={np.linalg.norm(raw_diff[L]):.4f}")

    meta_out = {
        "model_path": args.model_path, "layers": sorted(layers), "layer_order": layers,
        "peak_layer": args.peak_layer, "layer_depth_pct": depth_pct, "mode": args.mode,
        "bands": args.bands, "alphas": args.alphas, "fracs": args.fracs,
        "n_eval": args.n_eval, "n_noise": args.n_noise, "noise_scale": args.noise_scale,
        "min_gap": args.min_gap, "max_gold_tokens": args.max_gold_tokens,
        "readout": "teacher_forced_mean_gold_logprob (forward-pass only, no generation)",
        "raw_diff_of_means_norm_by_layer": {L: round(float(np.linalg.norm(raw_diff[L])), 6)
                                            for L in sorted(layers)},
    }
    with open(out_dir / "fix_logprob_readout_meta.json", "w") as f:
        json.dump(meta_out, f, indent=2)
    print(f"[stage23] wrote {out_dir / 'fix_logprob_readout_meta.json'}")

    if args.mode in ("fix_readout", "both"):
        run_fix_readout(model, tokenizer, decoder_layers, chat_style, device, out_dir, scored,
                        meta, gt_dict, args, layers, raw_diff, unit_dir, rand_full, rand_unit,
                        depth_pct, embed_layer)
    if args.mode in ("positive_control", "both"):
        run_positive_control(model, tokenizer, decoder_layers, chat_style, device, out_dir, scored,
                             meta, gt_dict, args, layers, raw_diff, unit_dir, rand_full, rand_unit,
                             depth_pct, embed_layer)

    print(f"\n[stage23] done — outputs in {out_dir}")


if __name__ == "__main__":
    main()
