"""Stage 19: ROME-style causal tracing at the P1 boundary.

A second, independent localization signal, so Stage 21 can ask whether either
localization curve predicts editing efficacy (Hase et al. 2023). Teacher-force
the gold authors and record the clean gold log-prob; corrupt the title token
embeddings with Gaussian noise; then restore the clean P1 state at one layer
and measure recovery. P1-only, because that is where the steering vector is
built and applied. Forward passes only, so it is cheap.

Usage
─────
  python -m dua.probing.stages.stage19_causal_tracing \
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
from stage14_activation_steering import build_input, get_decoder_layers

RANDOM_SEED = 42


def locate_title_token_span(tokenizer, input_ids: torch.Tensor, title: str) -> list[int] | None:
    """Token indices in input_ids whose decoded characters overlap the title.

    Works for both string-templated prompts and pre-tokenised (mistral3) ones,
    because it operates purely on the token ids: it decodes the full sequence,
    finds the title substring, then maps that character span back to token
    indices via cumulative prefix-decode lengths. Returns None if the title
    can't be located (caller skips the paper)."""
    ids = input_ids[0].tolist()
    full = tokenizer.decode(ids)
    cstart = full.find(title)
    if cstart < 0:
        # Fallback: some tokenizers normalise curly quotes / whitespace; try a
        # loosened match on the longest title prefix that survives a round-trip.
        probe = title.strip()[: max(8, len(title) // 2)]
        cstart = full.find(probe)
        if cstart < 0:
            return None
        cend = cstart + len(probe)
    else:
        cend = cstart + len(title)

    spans: list[tuple[int, int]] = []
    prev = ""
    for i in range(len(ids)):
        dec = tokenizer.decode(ids[: i + 1])
        spans.append((len(prev), len(dec)))
        prev = dec
    tok_idx = [i for i, (s, e) in enumerate(spans) if e > cstart and s < cend]
    return tok_idx or None


@torch.no_grad()
def teacher_forced_gold_logprob(
    model, decoder_layers, embeds: torch.Tensor, attention_mask: torch.Tensor,
    prompt_len: int, gold_ids: list[int],
    restore: tuple[int, int, torch.Tensor] | None = None,
) -> float:
    """Mean per-token log-prob of the gold answer tokens, teacher-forced.

    embeds : [1, T, D] input embeddings for [prompt + gold] (already noised if
             this is a corrupt/restore run).
    restore: optional (layer_idx, position, clean_vec) — overwrite that layer's
             output at `position` with clean_vec (the causal-tracing patch)."""
    handle = None
    if restore is not None:
        L, pos, cvec = restore

        def hook(module, inp, out):
            hidden = out[0] if isinstance(out, tuple) else out
            hidden[:, pos, :] = cvec.to(device=hidden.device, dtype=hidden.dtype)
            if isinstance(out, tuple):
                return (hidden,) + tuple(out[1:])
            return hidden

        handle = decoder_layers[L].register_forward_hook(hook)
    try:
        out = model(inputs_embeds=embeds, attention_mask=attention_mask)
        logits = out.logits.float()
    finally:
        if handle is not None:
            handle.remove()

    logprobs = torch.log_softmax(logits, dim=-1)
    # Position (prompt_len-1 + i) predicts the i-th gold token.
    total = 0.0
    for i, tid in enumerate(gold_ids):
        total += logprobs[0, prompt_len - 1 + i, tid].item()
    return total / max(len(gold_ids), 1)


def load_pool(scored: pd.DataFrame, paper_ids: list) -> pd.DataFrame:
    ids = {str(x) for x in paper_ids}
    return scored[scored["paper_id"].astype(str).isin(ids)].reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 19: causal-tracing localization")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--run_dir", required=True)
    parser.add_argument("--data_csv", required=True)
    parser.add_argument("--meta_json", required=True,
                        help="steering_meta.json from a completed Stage 14 run (eval_high pool IDs)")
    parser.add_argument("--layers", type=int, nargs="+", required=True,
                        help="Decoder layers to trace (match Stage 18: Qwen 24 40 48 56 63; Mistral 10 22 28 36)")
    parser.add_argument("--n_eval", type=int, default=40,
                        help="Subsample of the eval_high pool to trace")
    parser.add_argument("--n_noise", type=int, default=10,
                        help="Noise samples per paper (Meng default ~10)")
    parser.add_argument("--noise_scale", type=float, default=3.0,
                        help="Noise sigma = noise_scale * embedding-weight std (Meng default 3x)")
    parser.add_argument("--min_gap", type=float, default=0.05,
                        help="Min clean-minus-corrupted gold log-prob gap (nats) for a paper to count")
    parser.add_argument("--max_gold_tokens", type=int, default=64,
                        help="Cap the teacher-forced gold answer length (bounds cost)")
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

    eval_all = load_pool(scored, meta["pool_paper_ids"]["eval_high"])
    n = min(args.n_eval, len(eval_all))
    eval_pool = eval_all.sample(n=n, random_state=args.seed) if n > 0 else eval_all
    eval_pool = eval_pool.reset_index(drop=True)
    print(f"[stage19] eval_high pool: {len(eval_all)} available, tracing {len(eval_pool)}")

    registry_cfg = detect_model_config(args.model_path)
    chat_style = args.chat_style or (registry_cfg["chat_style"] if registry_cfg else "chatml")
    dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16
    print(f"[stage19] loading model {args.model_path} (chat_style={chat_style!r})")
    model, tokenizer = load_model_and_tokenizer(args.model_path, dtype, args.quantize)
    device = next(model.parameters()).device
    decoder_layers = get_decoder_layers(model)
    n_layers = len(decoder_layers)
    layers = [L for L in args.layers if L < n_layers]
    if len(layers) != len(args.layers):
        dropped = sorted(set(args.layers) - set(layers))
        print(f"[stage19] WARNING: dropping out-of-range layers {dropped} for a {n_layers}-layer model")

    embed_layer = model.get_input_embeddings()
    emb_std = float(embed_layer.weight.float().std().item())
    sigma = args.noise_scale * emb_std
    print(f"[stage19] embedding-weight std={emb_std:.5f}  noise sigma={sigma:.5f} "
          f"({args.noise_scale}x)  n_noise={args.n_noise}")

    depth_pct = {L: round(100.0 * L / (n_layers - 1), 1) for L in layers}
    per_paper_rows: list[dict] = []
    n_skipped_locate = 0
    n_skipped_gap = 0

    for pi, (_, row) in enumerate(eval_pool.iterrows()):
        pid = row["paper_id"]
        gt = gt_dict.get(pid)
        if gt is None:
            continue
        gold_str = str(gt["gt_authors"])
        gold_ids = tokenizer.encode(gold_str, add_special_tokens=False)[: args.max_gold_tokens]
        if not gold_ids:
            continue

        prompt_ids, _ = build_input(tokenizer, row["title"], row["year"], chat_style, device)
        span = locate_title_token_span(tokenizer, prompt_ids, str(row["title"]))
        if span is None:
            n_skipped_locate += 1
            print(f"[stage19]   [{pi}] pid={pid}: could not locate title span — skipping")
            continue

        prompt_len = prompt_ids.shape[1]
        gold_t = torch.tensor([gold_ids], dtype=torch.long, device=device)
        seq_ids = torch.cat([prompt_ids, gold_t], dim=1)
        attn = torch.ones_like(seq_ids)
        base_embeds = embed_layer(seq_ids)  # [1, T, D]
        p1_pos = prompt_len - 1

        # ── CLEAN: gold log-prob + cache clean P1 hidden per candidate layer ──
        with torch.no_grad():
            clean_out = model(inputs_embeds=base_embeds, attention_mask=attn,
                              output_hidden_states=True)
        clean_logprobs = torch.log_softmax(clean_out.logits.float(), dim=-1)
        clean_lp = float(np.mean([
            clean_logprobs[0, prompt_len - 1 + i, tid].item() for i, tid in enumerate(gold_ids)
        ]))
        clean_hidden = {L: clean_out.hidden_states[L + 1][0, p1_pos, :].detach().clone()
                        for L in layers}
        del clean_out, clean_logprobs

        # ── Per noise sample: corrupted + per-layer restore ─────────────────
        recov_by_layer = {L: [] for L in layers}
        corrupt_lps = []
        for s in range(args.n_noise):
            g = torch.Generator().manual_seed(args.seed + 1000 * pi + s)
            noise = torch.randn(len(span), base_embeds.shape[-1], generator=g).to(
                device=device, dtype=base_embeds.dtype) * sigma
            noised = base_embeds.clone()
            noised[0, span, :] = noised[0, span, :] + noise

            corrupt_lp = teacher_forced_gold_logprob(
                model, decoder_layers, noised, attn, prompt_len, gold_ids)
            gap = clean_lp - corrupt_lp
            corrupt_lps.append(corrupt_lp)
            if gap < args.min_gap:
                continue  # this noise draw didn't hurt; uninformative for recovery
            for L in layers:
                restored_lp = teacher_forced_gold_logprob(
                    model, decoder_layers, noised, attn, prompt_len, gold_ids,
                    restore=(L, p1_pos, clean_hidden[L]))
                recov_by_layer[L].append((restored_lp - corrupt_lp) / gap)

        mean_corrupt = float(np.mean(corrupt_lps)) if corrupt_lps else float("nan")
        if clean_lp - mean_corrupt < args.min_gap or all(len(v) == 0 for v in recov_by_layer.values()):
            n_skipped_gap += 1
            print(f"[stage19]   [{pi}] pid={pid}: corruption did not degrade "
                  f"(clean={clean_lp:.3f} corrupt={mean_corrupt:.3f}) — skipping")
            continue

        rec = {"paper_id": pid, "citation_count": row["citation_count"],
               "clean_logprob": round(clean_lp, 5), "mean_corrupt_logprob": round(mean_corrupt, 5),
               "n_title_tokens": len(span), "n_gold_tokens": len(gold_ids)}
        for L in layers:
            rec[f"recovery_L{L}"] = round(float(np.mean(recov_by_layer[L])), 5) if recov_by_layer[L] else float("nan")
        per_paper_rows.append(rec)
        if (pi + 1) % 5 == 0 or pi == len(eval_pool) - 1:
            print(f"[stage19]   traced {pi + 1}/{len(eval_pool)} "
                  f"(kept {len(per_paper_rows)}, skip_locate {n_skipped_locate}, skip_gap {n_skipped_gap})")

    if not per_paper_rows:
        raise RuntimeError("[stage19] no traceable papers — check pool / noise_scale / min_gap")

    per_paper = pd.DataFrame(per_paper_rows)
    per_paper.to_csv(out_dir / "causal_tracing_per_paper.tsv", sep="\t", index=False)
    print(f"[stage19] wrote {out_dir / 'causal_tracing_per_paper.tsv'}")

    # ── Per-layer localization curve (mean recovery + bootstrap CI over papers) ─
    rng = np.random.RandomState(args.seed)
    summary_rows = []
    for L in layers:
        vals = per_paper[f"recovery_L{L}"].dropna().to_numpy()
        if len(vals) == 0:
            continue
        boots = [rng.choice(vals, size=len(vals), replace=True).mean() for _ in range(2000)]
        summary_rows.append({
            "layer": L,
            "layer_depth_pct": depth_pct[L],
            "n_papers": len(vals),
            "mean_recovery": round(float(vals.mean()), 5),
            "median_recovery": round(float(np.median(vals)), 5),
            "ci_lo": round(float(np.percentile(boots, 2.5)), 5),
            "ci_hi": round(float(np.percentile(boots, 97.5)), 5),
        })
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(out_dir / "causal_tracing_results.csv", index=False)
    print(f"[stage19] wrote {out_dir / 'causal_tracing_results.csv'}")

    meta_out = {
        "model_path": args.model_path,
        "layers": layers,
        "layer_depth_pct": depth_pct,
        "n_eval_requested": args.n_eval,
        "n_traced_kept": len(per_paper),
        "n_skipped_locate": n_skipped_locate,
        "n_skipped_gap": n_skipped_gap,
        "n_noise": args.n_noise,
        "noise_scale": args.noise_scale,
        "embedding_std": round(emb_std, 6),
        "noise_sigma": round(sigma, 6),
        "min_gap": args.min_gap,
        "max_gold_tokens": args.max_gold_tokens,
        "eval_pool_paper_ids": eval_pool["paper_id"].astype(str).tolist(),
    }
    with open(out_dir / "causal_tracing_meta.json", "w") as f:
        json.dump(meta_out, f, indent=2)
    print(f"[stage19] wrote {out_dir / 'causal_tracing_meta.json'}")

    print("\n[stage19] === causal-tracing localization curve ===")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
