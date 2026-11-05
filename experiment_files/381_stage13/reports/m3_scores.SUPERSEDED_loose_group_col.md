# Stage 13 U46: the M3 behaviour scores year_nlr and author_first_nlr (POST-HOC)

Script `~/jlens_work/13_stage13/stage13_m3_scores.py`, run 2026-11-05 01:36. CPU only. **Post-hoc: these scores are not in prereg.json or addenda 1-6; nothing here is confirmatory.**

What was saved (381_stage13.py do_task, M3 task runs, 72 shards): per paper, the teacher-forced score log10(1/rank) at the model OUTPUT of (a) the year tokens after the year prompt (mean over the year's tokens), (b) the first token of the first author's name after the authors prompt. Rank 1 gives 0; rank 10 gives -1.
There is no layer or position dimension (only the output was scored), so the requested per-layer / per-position means cannot be given; the task dimension is one score per prompt (no score was saved for the field prompt).
Per-paper table: `/scratch/zhang.zhiqi2/jlens/381_stage13/summary_m3/m3_scores_perpaper.csv`.
Summary table: `/scratch/zhang.zhiqi2/jlens/381_stage13/summary_m3/m3_scores_summary.csv`.

## 1. Means by cohort group

| score | group | n | mean | share rank 1 | median |
|---|---|---|---|---|---|
| year_nlr | all | 9108 | -0.1525 | 0.086 | -0.1556 |
| year_nlr | control | 2220 | -0.1634 | 0.079 | -0.1690 |
| year_nlr | excluded | 994 | -0.1548 | 0.086 | -0.1556 |
| year_nlr | guard | 214 | -0.1167 | 0.145 | -0.1079 |
| year_nlr | target | 5680 | -0.1491 | 0.086 | -0.1556 |
| author_first_nlr | all | 9108 | -1.1736 | 0.085 | -1.0792 |
| author_first_nlr | control | 2220 | -1.2705 | 0.068 | -1.1761 |
| author_first_nlr | excluded | 994 | -1.2043 | 0.080 | -1.1139 |
| author_first_nlr | guard | 214 | -0.5484 | 0.271 | -0.4771 |
| author_first_nlr | target | 5680 | -1.1539 | 0.085 | -1.0792 |

author_first_nlr missing (no scored first author): 0 papers.

## 2. Means by citation bin, target vs control

| citation bin | year: target | year: control | author: target | author: control | n target / control |
|---|---|---|---|---|---|
| 0-2 | -0.1629 | -0.1820 | -1.1211 | -1.2019 | 304 / 352 |
| 1025-2048 | -0.1495 | -0.1443 | -1.1086 | -1.3191 | 563 / 29 |
| 129-256 | -0.1430 | -0.1492 | -1.1698 | -1.3333 | 595 / 126 |
| 17-32 | -0.1480 | -0.1578 | -1.1884 | -1.3185 | 464 / 234 |
| 2049-4096 | -0.1289 | -0.2200 | -1.0830 | -1.2488 | 271 / 9 |
| 257-512 | -0.1528 | -0.1583 | -1.1668 | -1.4447 | 619 / 105 |
| 3-4 | -0.1582 | -0.1703 | -1.1486 | -1.2022 | 309 / 355 |
| 33-64 | -0.1490 | -0.1496 | -1.2155 | -1.3455 | 510 / 185 |
| 4097+ | -0.1210 | +nan | -0.9459 | +nan | 84 / 0 |
| 5-8 | -0.1588 | -0.1660 | -1.1015 | -1.2026 | 344 / 332 |
| 513-1024 | -0.1466 | -0.1219 | -1.1579 | -1.5465 | 670 / 53 |
| 65-128 | -0.1503 | -0.1577 | -1.1976 | -1.3191 | 550 / 165 |
| 9-16 | -0.1501 | -0.1615 | -1.1541 | -1.2548 | 397 / 275 |

## 3. Target - control within citation bin (Stage 10 estimator; bins with >= 30 papers per group for the cohort, >= 10 for the 1,186-paper Stage 11 sample and its tune / test halves)

| score | papers | estimate | team CI (primary) | paper CI | bins |
|---|---|---|---|---|---|
| year_nlr | all cohort target/control | +0.0081 | [+0.0038, +0.0128] | [+0.0035, +0.0126] | 10 |
| author_first_nlr | all cohort target/control | +0.1286 | [+0.0807, +0.1713] | [+0.0841, +0.1700] | 10 |
| year_nlr | Stage 11 sample (1,186) | +0.0093 | [-0.0010, +0.0194] | [-0.0002, +0.0189] | 10 |
| author_first_nlr | Stage 11 sample (1,186) | +0.1701 | [+0.0767, +0.2582] | [+0.0824, +0.2653] | 10 |
| year_nlr | pairs.parquet tune | +0.0063 | [-0.0074, +0.0209] | [-0.0080, +0.0206] | 10 |
| author_first_nlr | pairs.parquet tune | +0.0982 | [-0.0325, +0.2234] | [-0.0255, +0.2266] | 10 |
| year_nlr | pairs.parquet test | +0.0143 | [-0.0001, +0.0277] | [+0.0018, +0.0284] | 10 |
| author_first_nlr | pairs.parquet test | +0.2600 | [+0.1257, +0.3991] | [+0.1301, +0.3936] | 10 |

## 4. Relations (Spearman, all papers)

- year score vs author score: rho = +0.001 (n = 9108)
- year score vs log citations: rho = +0.109 (n = 9108)
- author score vs log citations: rho = +0.030 (n = 9108)
- year score vs publication year: rho = +0.221 (n = 9108)

## Reading (post-hoc)

- These are output-level behaviour scores under the two M3 prompts; they say how well the model completes the year / first-author token for each title, not where in the layers the information sits.
- Groups (cohort `group`): target = cannot write the authors (R0/R1) but picks the true author list in 4 of 4 multiple-choice orders; control = R0/R1 and at most 1 of 4 right; guard = writes the authors (R2). An author-score difference is therefore related to how the groups were defined (recognition of the author list), and is a description, not new evidence.
- The groups were not defined from the year, so year target - control is the less circular number; it is still post-hoc.
- Teacher-forced output scores, not generation (addendum 4 wording).
