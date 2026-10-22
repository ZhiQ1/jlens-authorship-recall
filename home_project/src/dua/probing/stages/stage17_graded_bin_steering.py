"""Stage 17: bidirectional steering within one HR2 band, with an alpha search.

Stage 14's fix test ran on eval_low, which sits at the HR2 ceiling, so its null
is ambiguous -- a floor effect and a real "cannot inject unlearned knowledge"
effect look identical. It also tested fix and induce on different populations.
This steers one band both ways on the *same* pool, removing that confound, and
searches alpha by the specificity margin over a norm-matched control rather
than by raw HR2 change.

Also extracts a teacher-forced contrastive vector while the model is loaded.
That vector is a candidate for comparison only, never the primary steering
vector: it puts ground-truth answer tokens into the activations it is built
from, reintroducing the leakage the disjointness design prevents.

Usage
─────
  python -m dua.probing.stages.stage17_graded_bin_steering \
      --model_path   /scratch/$USER/scholar_qwen/models/Qwen3-32B \
      --run_dir      /scratch/$USER/scholar_qwen/run_qwen3_32b \
      --data_csv     data/interim/probing_prompts_9108.csv \
      --layer        48 \
      --meta_json    /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_meta.json \
      --steering_vector_path /scratch/$USER/scholar_qwen/steering_qwen3_32b/steering_vector.npy \
      --hr2_lo 0.35 --hr2_hi 0.65 \
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
from dua.probing.scholar_utils import NameMatcher
from stage1_generate import build_prompt, detect_model_config, load_model_and_tokenizer
from stage2_score import load_ground_truth
from stage14_activation_steering import (
    MAX_NEW_TOKENS,
    build_input,
    build_random_norm_matched_vector,
    get_decoder_layers,
    run_condition,
    summarize_condition,
)

RANDOM_SEED = 42


# ─────────────────────────────────────────────────────────────────────────────
# Teacher-forced contrastive vector (candidate-only; see module docstring)
# ─────────────────────────────────────────────────────────────────────────────

@torch.no_grad()
def extract_answer_conditioned(model, tokenizer, title, year, chat_style, device,
                                layer: int, answer_text: str) -> np.ndarray:
    """Layer-L hidden state at the LAST answer token of a teacher-forced
    forward pass over (prompt + answer_text)."""
    input_ids, _ = build_input(tokenizer, title, year, chat_style, device)
    ans_ids = tokenizer.encode(answer_text, add_special_tokens=False)
    if not ans_ids:
        ans_ids = tokenizer.encode(".", add_special_tokens=False)
    ans = torch.tensor([ans_ids], dtype=torch.long, device=device)
    full = torch.cat([input_ids, ans], dim=1)
    mask = torch.ones_like(full)
    out = model(input_ids=full, attention_mask=mask, output_hidden_states=True)
    return out.hidden_states[layer + 1][0, -1, :].float().cpu().numpy()


def build_author_pool(gt_dict: dict, matcher: NameMatcher) -> list[str]:
    names: set[str] = set()
    for g in gt_dict.values():
        for n in matcher.splitter.split(g.get("gt_authors", "") or ""):
            n = n.strip()
            if n:
                names.add(n)
    return sorted(names)


def fabricate_authors(true_names: list[str], author_pool: list[str], rng: np.random.RandomState) -> str:
    """Length-matched plausible-but-false author list: names sampled from
    OTHER papers, excluding this paper's true authors."""
    k = max(1, len(true_names))
    true_set = set(true_names)
    picks: list[str] = []
    attempts = 0
    while len(picks) < k and attempts < 100 * k:
        cand = author_pool[rng.randint(len(author_pool))]
        if cand not in true_set and cand not in picks:
            picks.append(cand)
        attempts += 1
    if not picks:  # degenerate corpus fallback
        picks = [author_pool[rng.randint(len(author_pool))]]
    return "; ".join(picks)


def build_teacher_forced_vector(model, tokenizer, layer, device, chat_style,
                                 papers: pd.DataFrame, gt_dict: dict, matcher: NameMatcher,
                                 seed: int) -> tuple[np.ndarray, int]:
    author_pool = build_author_pool(gt_dict, matcher)
    rng = np.random.RandomState(seed)
    diffs = []
    for _, row in papers.iterrows():
        gt = gt_dict.get(row["paper_id"])
        if gt is None:
            continue
        true_names = [n.strip() for n in matcher.splitter.split(gt.get("gt_authors", "") or "") if n.strip()]
        if not true_names:
            continue
        wrong_text = fabricate_authors(true_names, author_pool, rng)
        a_correct = extract_answer_conditioned(model, tokenizer, row["title"], row["year"],
                                               chat_style, device, layer, gt["gt_authors"])
        a_wrong = extract_answer_conditioned(model, tokenizer, row["title"], row["year"],
                                             chat_style, device, layer, wrong_text)
        diffs.append(a_correct - a_wrong)
    if not diffs:
        raise RuntimeError("No papers with usable ground-truth authors for the teacher-forced vector")
    return np.stack(diffs).mean(axis=0).astype(np.float32), len(diffs)


def load_or_build_teacher_forced_vector(out_dir: Path, builder) -> tuple[np.ndarray, bool]:
    """Load teacher_forced_vector.npy if present, else build + write it
    atomically (so concurrent per-band jobs can't corrupt it; the vector is
    deterministic, so a last-writer-wins rename is harmless)."""
    tf_path = out_dir / "teacher_forced_vector.npy"
    if tf_path.exists():
        print(f"[stage17] loading existing teacher-forced vector {tf_path}")
        return np.load(tf_path), False
    vec = builder()
    tmp = out_dir / f".teacher_forced_{os.getpid()}.npy"
    np.save(tmp, vec)
    os.replace(tmp, tf_path)
    print(f"[stage17] wrote {tf_path}")
    return vec, True


# ─────────────────────────────────────────────────────────────────────────────
# Band eval-pool selection
# ─────────────────────────────────────────────────────────────────────────────

def excluded_ids(meta: dict) -> set:
    exclude: set = set()
    for ids in meta["pool_paper_ids"].values():
        exclude.update(str(x) for x in ids)
    return exclude


def select_band_pool(scored: pd.DataFrame, meta: dict, hr2_lo: float, hr2_hi: float,
                     n_eval: int, seed: int) -> pd.DataFrame:
    exclude = excluded_ids(meta)
    cand = scored[(scored["hr2"] > hr2_lo) & (scored["hr2"] <= hr2_hi)].copy()
    cand = cand[~cand["paper_id"].astype(str).isin(exclude)]
    print(f"[stage17] band ({hr2_lo}, {hr2_hi}]: {len(cand)} candidate papers "
          f"disjoint from Stage 14 pools")
    n = min(n_eval, len(cand))
    if n < n_eval:
        print(f"[stage17] WARNING: only {n} papers available in this band (requested {n_eval})")
    pool = cand.sample(n=n, random_state=seed) if n > 0 else cand
    overlap = set(pool["paper_id"].astype(str)) & exclude
    if overlap:
        raise AssertionError(f"band pool overlaps Stage 14 pools on {len(overlap)} ids — bug")
    return pool.reset_index(drop=True)


def hallucination_rate(df: pd.DataFrame) -> float:
    if df.empty:
        return float("nan")
    return round(100.0 * float((df["hr2"] > 0.5).mean()), 2)


def alpha_search_should_stop(gaps: list[float], margin: float, patience: int) -> bool:
    """Stop the adaptive-alpha search once the specificity gap (real minus
    control hallucination rate, pp) has shrunk by at least `margin` pp for
    `patience` consecutive steps. Counts only the trailing run of shrinking
    steps, so a single upward blip resets the counter — the margin
    requirement keeps sampling noise from triggering an early stop."""
    if len(gaps) <= patience:
        return False
    consec = 0
    for i in range(len(gaps) - 1, 0, -1):
        if gaps[i] <= gaps[i - 1] - margin:
            consec += 1
            if consec >= patience:
                return True
        else:
            break
    return False


# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 17: graded-bin bidirectional steering + adaptive alpha")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--run_dir", required=True)
    parser.add_argument("--data_csv", required=True)
    parser.add_argument("--layer", type=int, required=True)
    parser.add_argument("--meta_json", required=True,
                        help="steering_meta.json from the completed Stage 14 run (pool IDs)")
    parser.add_argument("--steering_vector_path", required=True,
                        help="steering_vector.npy from Stage 14 (overridable to Stage 16's "
                             "lda_vector.npy / probe_direction.npy)")
    parser.add_argument("--hr2_lo", type=float, required=True, help="band lower bound (exclusive)")
    parser.add_argument("--hr2_hi", type=float, required=True, help="band upper bound (inclusive)")
    parser.add_argument("--n_eval", type=int, default=50)
    parser.add_argument("--alpha_start", type=float, default=1.0)
    parser.add_argument("--alpha_step", type=float, default=1.0)
    parser.add_argument("--alpha_cap", type=float, default=4.0)
    parser.add_argument("--alpha_grid", type=str, default=None,
                        help="comma-separated explicit alpha list (e.g. "
                             "'0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2'). When set, bypasses the "
                             "adaptive search entirely and runs induce(real)+induce(norm-matched "
                             "control)+fix(real) at EVERY listed alpha with NO early-stop. Used for "
                             "the sub-alpha-1 confirmatory sweep (--alpha_start/step/cap ignored).")
    parser.add_argument("--alpha_min_gap_margin", type=float, default=3.0,
                        help="min pp the specificity gap must shrink by to count as shrinking")
    parser.add_argument("--alpha_patience", type=int, default=2,
                        help="consecutive shrinking steps before stopping the alpha search")
    parser.add_argument("--include_teacher_forced_steering", action="store_true",
                        help="also steer (induce) with the teacher-forced vector at the best alpha "
                             "(off by default to protect the 2h budget)")
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
    scored["hr2"] = pd.to_numeric(scored["hr2"], errors="coerce")
    gt_dict = load_ground_truth(args.data_csv)
    meta = json.load(open(args.meta_json))

    steering_vector = np.load(args.steering_vector_path).astype(np.float32)
    ref_norm = float(np.linalg.norm(steering_vector))
    random_vector = build_random_norm_matched_vector(steering_vector.shape[0], ref_norm, seed=args.seed)
    print(f"[stage17] steering vector norm={ref_norm:.4f}  random control norm="
          f"{np.linalg.norm(random_vector):.4f}")

    pool = select_band_pool(scored, meta, args.hr2_lo, args.hr2_hi, args.n_eval, args.seed)
    if pool.empty:
        print(f"[stage17] band ({args.hr2_lo}, {args.hr2_hi}] is exhausted for this model: no papers "
              "remain after excluding Stage 14's pools. This happens for the lowest bands because "
              "Stage 14's well-attributed pools (ranked by HR2 ascending) already consume the "
              "low/mid-HR2 papers. Nothing to run for this band; "
              "exiting cleanly.")
        return

    # ── Model ────────────────────────────────────────────────────────────────
    registry_cfg = detect_model_config(args.model_path)
    chat_style = args.chat_style or (registry_cfg["chat_style"] if registry_cfg else "chatml")
    dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16
    print(f"[stage17] loading model {args.model_path} (chat_style={chat_style!r})")
    model, tokenizer = load_model_and_tokenizer(args.model_path, dtype, args.quantize)
    device = next(model.parameters()).device
    decoder_layers = get_decoder_layers(model)
    if args.layer >= len(decoder_layers):
        raise ValueError(f"--layer {args.layer} out of range for a {len(decoder_layers)}-layer model")

    # ── Teacher-forced vector (always built once; piggybacks the model load) ─
    matcher = NameMatcher()
    vector_pool_ids = (list(meta["pool_paper_ids"]["vector_correct"])
                       + list(meta["pool_paper_ids"]["vector_hallucinated"]))
    vector_papers = scored[scored["paper_id"].astype(str).isin({str(x) for x in vector_pool_ids})]
    tf_vec, tf_built = load_or_build_teacher_forced_vector(
        out_dir,
        lambda: build_teacher_forced_vector(model, tokenizer, args.layer, device, chat_style,
                                            vector_papers, gt_dict, matcher, args.seed)[0],
    )
    print(f"[stage17] teacher-forced vector norm={np.linalg.norm(tf_vec):.4f} "
          f"({'built' if tf_built else 'loaded'})")

    # ── Run conditions ────────────────────────────────────────────────────────
    results_summary: list[dict] = []
    predictions: list[pd.DataFrame] = []

    def record(df: pd.DataFrame, **tags) -> None:
        if not df.empty:
            tagged = df.copy()
            for k, v in tags.items():
                tagged[k] = v
            predictions.append(tagged)
        results_summary.append(summarize_condition(df, **tags))

    def steer(vec, alpha):
        return run_condition(model, tokenizer, decoder_layers, args.layer, device, chat_style,
                             pool, gt_dict, args.max_new_tokens, vector=vec, alpha=alpha)

    print(f"[stage17] === band {band_tag}, n={len(pool)}: baseline ===")
    df = steer(None, 0.0)
    base_hr = hallucination_rate(df)
    record(df, pool=band_tag, condition="baseline", direction="none", alpha=0.0, vector="none")
    print(f"[stage17] baseline hallucination rate = {base_hr}%")

    # Alpha schedule: either an explicit grid (confirmatory sweep, no early-stop)
    # or the adaptive search. In both cases the induce arm (real + norm-matched
    # control) runs at every scheduled alpha; the fix arm reuses alphas_visited.
    alpha_grid = None
    if args.alpha_grid:
        alpha_grid = [round(float(a), 6) for a in args.alpha_grid.split(",") if a.strip()]
        print(f"[stage17] explicit alpha grid (adaptive search disabled, no early-stop): {alpha_grid}")

    alphas_visited: list[float] = []
    gap_trajectory: list[dict] = []
    best_alpha, best_gap = None, float("-inf")

    def run_induce(alpha: float) -> float:
        nonlocal best_alpha, best_gap
        print(f"[stage17] induce alpha={alpha}: real (−vector)")
        df_real = steer(-steering_vector, alpha)
        record(df_real, pool=band_tag, condition="steering", direction="induce_toward_hallucinated",
               alpha=alpha, vector="real")
        print(f"[stage17] induce alpha={alpha}: norm-matched random control (−)")
        df_ctrl = steer(-random_vector, alpha)
        record(df_ctrl, pool=band_tag, condition="random_norm_matched_control",
               direction="induce_toward_hallucinated", alpha=alpha, vector="random")

        hr_real, hr_ctrl = hallucination_rate(df_real), hallucination_rate(df_ctrl)
        gap = hr_real - hr_ctrl
        alphas_visited.append(alpha)
        gap_trajectory.append({"alpha": alpha, "hr_real": hr_real, "hr_control": hr_ctrl,
                               "specificity_gap_pp": round(gap, 2)})
        print(f"[stage17] alpha={alpha}: real={hr_real}%  control={hr_ctrl}%  gap={gap:.2f}pp")
        if gap > best_gap:
            best_gap, best_alpha = gap, alpha
        return gap

    if alpha_grid is not None:
        for alpha in alpha_grid:
            run_induce(alpha)
    else:
        alpha = args.alpha_start
        while alpha <= args.alpha_cap + 1e-9:
            run_induce(alpha)
            if alpha_search_should_stop([g["specificity_gap_pp"] for g in gap_trajectory],
                                        args.alpha_min_gap_margin, args.alpha_patience):
                print(f"[stage17] specificity gap shrank for {args.alpha_patience} consecutive "
                      "steps — stopping alpha search")
                break
            alpha = round(alpha + args.alpha_step, 6)

    # Fix (+vector) direction on the SAME pool, at the alphas visited.
    for a in alphas_visited:
        print(f"[stage17] fix alpha={a}: real (+vector, toward well-attributed)")
        df_fix = steer(steering_vector, a)
        record(df_fix, pool=band_tag, condition="steering", direction="fix_toward_cited",
               alpha=a, vector="real")

    # Optional teacher-forced steering (induce), best alpha only.
    if args.include_teacher_forced_steering and best_alpha is not None:
        print(f"[stage17] teacher-forced induce steering at best alpha={best_alpha}")
        df_tf = steer(-tf_vec, best_alpha)
        record(df_tf, pool=band_tag, condition="teacher_forced_steering",
               direction="induce_toward_hallucinated", alpha=best_alpha, vector="teacher_forced")

    # ── Write outputs ────────────────────────────────────────────────────────
    summary_df = pd.DataFrame(results_summary)
    summary_df.to_csv(out_dir / f"graded_steering_results_{band_tag}.csv", index=False)
    print(f"[stage17] wrote {out_dir / f'graded_steering_results_{band_tag}.csv'}")

    if predictions:
        pd.concat(predictions, ignore_index=True).to_csv(
            out_dir / f"graded_steering_predictions_{band_tag}.tsv", sep="\t", index=False)
        print(f"[stage17] wrote {out_dir / f'graded_steering_predictions_{band_tag}.tsv'}")

    np.save(out_dir / f"random_norm_matched_control_vector_{band_tag}.npy", random_vector)
    meta_out = {
        "model_path": args.model_path,
        "layer": args.layer,
        "band": {"hr2_lo": args.hr2_lo, "hr2_hi": args.hr2_hi},
        "n_eval": len(pool),
        "baseline_hallucination_rate_pct": base_hr,
        "steering_vector_path": args.steering_vector_path,
        "steering_vector_norm": ref_norm,
        "random_control_norm": float(np.linalg.norm(random_vector)),
        "teacher_forced_vector_norm": float(np.linalg.norm(tf_vec)),
        "teacher_forced_built_this_run": tf_built,
        "alpha_schedule_mode": "grid" if alpha_grid is not None else "adaptive",
        "alpha_grid": alpha_grid,
        "adaptive_alpha": {
            "start": args.alpha_start, "step": args.alpha_step, "cap": args.alpha_cap,
            "min_gap_margin_pp": args.alpha_min_gap_margin, "patience": args.alpha_patience,
            "alphas_visited": alphas_visited,
            "gap_trajectory": gap_trajectory,
            "best_alpha": best_alpha,
            "best_specificity_gap_pp": round(best_gap, 2) if best_alpha is not None else None,
        },
        "eval_pool_paper_ids": pool["paper_id"].astype(str).tolist(),
    }
    with open(out_dir / f"graded_steering_meta_{band_tag}.json", "w") as f:
        json.dump(meta_out, f, indent=2)
    print(f"[stage17] wrote {out_dir / f'graded_steering_meta_{band_tag}.json'}")

    print("\n[stage17] === summary ===")
    print(summary_df.to_string(index=False))
    print(f"\n[stage17] best alpha (max specificity gap) = {best_alpha} "
          f"({best_gap:.2f}pp over control)" if best_alpha is not None else "[stage17] no alpha visited")


if __name__ == "__main__":
    main()
