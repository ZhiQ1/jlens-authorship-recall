# Stage 13 fold audit: team folds (group_folds) vs the original runs (2026-10-30)

User request: check every script that uses the team-fold function (especially E4b, M2b, M2c, X1, X3). Do the folds match
the original runs? Make all of them read archived fold files, and list any mismatch with the change in point estimates.

## Cause of the instability
`stage13_cpu.group_folds()` orders equal-size teams with `pd.Series.value_counts()`. Under numpy 1.26.4 that is an
unstable quicksort, and numpy uses its AVX-512 sort (x86-simd-sort) on CPUs that have AVX-512.
- **Fold assignment:** depends only on whether the node has AVX-512. Without AVX-512 (Intel E5-2680 v4 Broadwell c06xx/c3155,
  AMD EPYC 7702 d0139), all 8 nodes tested give one assignment. With AVX-512 (Xeon Platinum 8276 cascadelake d0027, and d0026
  in the earlier tiny test), the assignment is different: 6,713 of 9,108 papers, 7,113 of 9,108 false_0 rows and 586 of
  1,178 pairs papers get another fold.
- **Team ids (cluster ids):** do NOT depend on the CPU. Union-find roots are pure Python, and the bootstraps number teams in
  order of appearance with `pd.factorize`. The team partition was identical on every node, AVX-512 included. So every
  team-cluster bootstrap that uses only team ids is reproducible anywhere: cluster_ci, X1/X4 (via pairs.parquet), X4
  rolesplit, X4 textbase, X6, X7, and the M3 bootstrap.

## Paper sets
Only 3 distinct group_folds inputs exist:
- **own9108:** 9,108 papers, k=5, seed=13. The Stage 11 titlepos order, the cohort papers.parquet order and the M3 cache order are the same order.
- **donor9108_false0:** the 9,108 false_0 rows. The input is the donor ids, k=5, seed=13.
- **pairs1178:** 1,178 X1/X3/X4 pairs, k=2, seed=1314. Only the team ids are used.

## Method
1. Script `13_stage13/stage13_foldaudit_variants.py` recomputes all 5 call patterns with the unpatched function on 10 nodes:
   this node c0622, plus each original-run node via `--nodelist`, plus a cascadelake node.
   - Jobs: 11511921–11511930 and 11512064.
   - Output: `foldaudit_2026-10-30/variants/<node>.npz`.
2. Script `stage13_foldaudit_fingerprint.py` checks the variants against fingerprints saved in the original outputs:
   - M2: `folds_group.npz`, which was already shown to reproduce all 176 M2 point estimates.
   - E4b (group and train-std runs): the per-paper title-reuse `dropped` flag, which is a function of the folds.
     It gives 0 mismatches of 9,108 with the archived folds and 2,872 with the AVX-512 folds, so the fingerprint can tell the two apart.
   - Team partitions: the team columns in pairs.parquet and x4_textbase*_perpaper.csv.

## Table

| script | paper set | original job / node (CPU) | folds identical to original? | max point-estimate diff | flips | now reads archive? |
|---|---|---|---|---|---|---|
| stage13_cpu.py m2 (SPLIT=group), M2 true | own9108 | 11443403 / d0139 (EPYC 7702) | yes (= folds_group.npz; 176/176 estimates reproduced by 11503585) | 0 | 0 | yes (group_folds → archive) |
| stage13_cpu.py m2, M2 false_0 | donor9108_false0 | 11443403 / d0139 | yes | 0 | 0 | yes |
| stage13_m2b.py (group) | own9108 | 11443403 / d0139 | yes (same job and folds as M2 true) | 0 | 0 | yes |
| stage13_m2c.py (group) | own9108 | 11443403 / d0139 | yes | 0 | 0 | yes |
| stage13_m2_teamci.py | own9108 + donor9108 | 11503585 / c0607 (Broadwell) | yes (reads folds_group.npz itself) | 0 (1e-16) | 0 | yes (its own folds_group.npz) |
| stage13_m2_teamci.py **tiny 11501115** | own9108 + donor9108 | 11501115 / **d0026 (cascadelake, AVX-512)** | **NO** | **0.0061** (year-only recognised AUROC 0.5613 vs 0.5552); lo 0.0085, hi 0.0068 | 0 (excl. 0 / above chance) | n/a (test run, already marked BAD; redone as 11503471) |
| stage13_e4b_group.py (E4b + X1 controls, group split) | own9108 (k=5) | 11443587 / c0685 (Broadwell) | yes (node recompute identical; dropped-flag fingerprint 0/9,108) | 0 | 0 | yes |
| stage13_e4b_trainstd.py | own9108 | 11500917 / c0602 (Broadwell); tiny 11500538 / c0610 | yes (node recompute identical; fingerprint 0/9,108) | 0 | 0 | yes |
| stage13_m3_analyze.py (folds + team bootstrap) | own9108 (M3 cache order) | 11472899 / c0613 (Broadwell) | yes | 0 | 0 | yes |
| stage13_x4_textbase2.py (folds + team) | own9108 | 11475517 / c0621 (Broadwell) | yes | 0 | 0 | yes |
| stage13_x4_textbase.py (team only) | own9108 | run inside 11474830 / c0640 | team partition CPU-independent; matches saved per-paper team | 0 | 0 | yes |
| stage13_cluster_ci.py (team only) | own9108 | 11443686 / c0606, 11443696 / c3155 | yes (both nodes recomputed) | 0 | 0 | yes |
| stage13_x6_analyze.py (team only) | own9108 | 11461197 / d0064 | team partition CPU-independent (node recompute 11511927 still queued) | 0 | 0 | yes |
| stage13_x7_analyze.py (team only) | own9108 | 11470524 / c0609 | team partition CPU-independent (node recompute 11511928 still queued) | 0 | 0 | yes |
| 381_stage13.py freeze → config/pairs.parquet (team → tune/test split; X1, X3, X4) | pairs1178 (k=2) | (freeze step) | team partition identical on all nodes = pairs.parquet; folds not used | 0 | 0 | frozen script not edited. It imports stage13_cpu, so it now gets the archive (folds_pairs1178_k2s1314.npz). |
| stage13_x1x4_analyze.py, stage13_x4_rolesplit.py (X1, X4) | pairs1178 | 11472859 / c0659, 11472901 / c0592 | read team and split from saved pairs.parquet / per-paper csv; no group_folds call | 0 | 0 | n/a (already read saved files) |
| X3 (stage13_para_nli.py, stage13_judge2.py, stage13_x3_neighbour_j2.py) | — | — | no folds, no team ids | — | — | n/a |
| stage13_split_compare.py | — | 11443607 / d0110 | only reads csvs | — | — | n/a |
| 10_stage10/stage10_extra_r0r1.py, 12_stage12/stage12_cpu.py (frozen) | — | — | paper folds `default_rng(11).integers` (deterministic); team folds are injected by the e4b scripts | — | — | not edited (frozen) |

**Conclusion:** every original analysis ran on a node without AVX-512, and its folds equal today's folds on c0622 and the archive.
The one mismatch is the d0026 tiny test 11501115, which was already discarded. No analysis needed a rerun, so nothing was rerun.
A rerun on an AVX-512 node before this fix would have moved point estimates by up to about 0.006 (M2 tiny evidence) without flipping any conclusion.

## Freeze
- Archive: `summary_cpu_teamci/folds_own9108_k5s13.npz`, `folds_donor9108_false0_k5s13.npz`, `folds_pairs1178_k2s1314.npz`.
  - Each file holds the exact input ids, the row paper_id, fold, team, k and seed.
  - sha256 values are in `summary_cpu_teamci/README.md`. `folds_group.npz` is unchanged.
- `13_stage13/stage13_cpu.py` (backup `stage13_cpu.before_foldsfreeze_2026-10-30.py`): `group_folds()` now calls `_archived_folds()` first.
  - Archive found: when the input id set plus k and seed equal an archive file, it returns the archived fold and team per id (any input order works).
  - Near miss: when the input has the same row count and ≥ 90% id overlap with an archive file, but not the exact ids, it raises a clear `ValueError`.
  - No archive: otherwise it computes as before and prints a WARNING to stderr (tiny tests on subsets).
  - `JLENS_FOLDS_ARCHIVE=off` forces computing.
  - Tested: all 4 call patterns return the archived arrays bit for bit; a shuffled order maps correctly; a 500-paper subset computes with the warning; a set with one wrong id raises.
- No other script needed an edit: they all call `stage13_cpu.group_folds`.
