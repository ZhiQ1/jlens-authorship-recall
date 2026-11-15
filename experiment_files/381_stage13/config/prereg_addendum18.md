# Addendum 18 (partial lock 2026-11-14): item 3 only — E1 + X6 replacement at the missing layers L41–L47, L49, L51

Status: ONLY item 3 (restricted to the E1 + X6 layer fill below) is LOCKED by this file (sha256 in prereg_addendum18.md.sha256; lock time and script hashes in addendum18_lock.json). All other items of ~/jlens_work/prereg18_draft.md (readout map, windowed knockout, per-cell patching over position groups, L57–L61 ablation, title-token importance, MLP lookup) are NOT locked and NOT approved. User approval 2026-11-14: "批准补 E1+X6 在 L41–47、L49、L51 的替换……第 3 项先只包含这一条，锁定后提交"; per-cell patching (6.1 GPU-h) not approved.

Known before locking (stated honestly): the E1 / X6 curves at the stored layers (L24, 32, 40, 48, 50, 52, 54, 56, 57–63; e.g. 5-title mean R(L48) 0.821, R(L52) 0.995, R(L40) about 0.30) are published. No output at the new layers exists at lock time: only a CPU tiny test with a random 64-layer model (job 11874986) has been run; no GPU job of this item has been submitted.

## Design
- Intervention: frozen E1 / X6 code (381_stage13.py do_xf_patch → 361_stage11 do_patch; tail recomputed per false title by the Stage 11 freeze rule): the residual stream of ALL post-title positions at layer l is copied from the true-title run into the false-title run; output scored at the model output (no lens).
- Sample: the Stage 11 sample, 1,186 papers (target + control), 24 shards; false titles false_0 … false_4 (false_0 = E1, false_1..4 = X6).
- Layers in one patched batch (15, the same batch shape as the stored runs, so bf16 rounding matches): new L41, L42, L43, L44, L45, L46, L47, L49, L51; overlap L40, L48, L50, L52, L54, L56 (used only for the hard check; published values are kept for these layers).
- Code: ~/jlens_work/13_stage13/stage13_e1x6_extra_20261114.py (sha256 fcbcd61629c8c08615249fbca0d5036588c2268ada1d417f685a277432c36e5d), _gpu.sbatch (dc73dc2b…), analysis stage13_e1x6_extra_analyze_20261114.py (d02e5f2aefc2a0ab329140f77e0a056c20aa0737085479feab8984131873e263), _analyze.sbatch (6a8b9f82…). Output raw: 381_stage13/raw/e1x6_extra_20261114/false_k/; summary: 381_stage13/summary_e1x6_extra_20261114/.
- U0 (600-paper list) is NOT part of this lock (not approved).

## Estimand
- Per name token nlr = log10(1/rank of the true author's token at the output); averaged within paper. For paper set S and false title k: R_k(l) = mean_S(nlr_patched,l − nlr_false) / mean_S(nlr_true − nlr_false). Primary curve: 5-title mean R(l) = mean of R_0..R_4, all 1,186 papers; false_0 version beside it; target, control, target − control.
- CI: 95% percentile, 2,000 multinomial draws over author teams (stage13_cpu.group_folds team ids, numpy default_rng(13), one draw set shared by all layers and titles; identical to the published x6_recovery.csv procedure).

## What will be reported (decision rules)
1. R(l) for every layer L40–L52 (L53 has no data) plus stored L24, 32, 54, 56, 57–63.
2. Half-arrival layer = the first layer l in L40–L52 whose 5-title mean R(l) (all papers) has 95% CI lower bound ≥ 0.5; full-arrival layer = the first layer whose lower bound ≥ 0.9. Steepest single-layer increase R(l) − R(l−1) reported with its CI (same draws).
3. Wording rule for the documents: the current text "information enters the name positions between L40 and L52 (mainly L44–L52)" is replaced by "mainly between L[a] and L[b]", where a = the first layer in L40–L52 whose 5-title mean R(l) has 95% CI lower bound ≥ 0.1 and b = the full-arrival layer (item 2); the half-arrival layer is stated beside it. If no layer in L40–L52 reaches a criterion, that is stated and the old wording is kept.
4. By group (descriptive, no decision rule; groups as in groups_s1113.py: A = R0 strong, B = R0 fail, C = R1 strong, D = R1 fail; only consistent author flags; primary = unwritten authors; groups_core.Engine 2,000 team draws, default_rng(391)): R(l) per group for false_0 and the 5-title mean; contrast A − B per layer. C (32 papers) reported with a low-power note; D (5 papers) descriptive only.

## Hard checks (WARN only — CLAUDE.md item 3: a miss is recorded with value and threshold and the queue continues; only a code crash stops it)
1. Overlap layers L40, 48, 50, 52, 54, 56: per title, share of exactly equal rank_true, rank_false, rank_patch vs the stored rows (361_stage11/raw/patch for false_0; 381_stage13/raw/xf_patch/false_k), threshold ≥ 0.99; max |Δ log10 rank| reported.
2. Per title R_k(l) new − stored, |diff| ≤ 0.005 at overlap layers.
3. 5-title mean from the new rows only: R(L48) vs 0.8211 and R(L52) vs 0.9955 (summary_x6/x6_recovery.csv), |diff| ≤ 0.005.

## Order of work
First shard (false_0, shard 0) alone; read its unit check; then one job per false title (5 jobs, ≤ 45 min each, skip-if-done, killguard exclude); analysis with afterok on all five. Estimated 2.4 GPU-h compute (2.8 GPU-h allocated) — above the 1.5 GPU-h first estimate because the batch keeps 15 layers for exact rounding parity; below 5 GPU-h.
