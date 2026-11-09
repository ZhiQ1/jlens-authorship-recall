# jlens master queue (plan document)

Status as of 2026-11-07 18:30 EST (internal update; not yet on the downloads page). Rules of every redo item were fixed and locked (sha256) before its results; reproducing the published numbers is a hard check. Sources: `~/jlens_work/PROGRESS.md`, `381_stage13/config/prereg_addendum*.json`, `391_groups/config/`.

| group | item | batch | status | addendum / rule | result / note |
|---|---|---|---|---|---|
| Stage 1–12 | Stage 1–12 (cohort, protocol, lenses, Stages 4–11, Stage 12 P1/P2/N1/N2/F1/F2) | before defence | **done** | frozen protocols; Stage 10 analysis_plan | report Parts 1–4; handbook C–E |
| Stage 1–12 | Stage 7.1B terminal readout | before defence | **not done** | — | stopped at 1,166 / 15,519; superseded by Stage 10; job 11637611 cancelled 2026-11-05 (user) |
| Stage 1–12 | Stage 9 Fit A | before defence | **done** | Stage 9 protocol | used as fitA lens in Stage 10 |
| Stage 13 (prereg.json) | M1, M2, M2b, M2c, M3 | before defence | **done** | prereg.json; addenda 1, 2 | report Part 4; handbook F |
| Stage 13 (prereg.json) | M4 = Stage 12 F1 / F2 | before defence | **done** | prereg.json | report Part 4 (Stage 12) |
| Stage 13 (prereg.json) | X1, X3, X4, X5, X6, X7 | before defence | **done** | prereg.json; addenda 2–5 | report Part 4 |
| Stage 13 (prereg.json) | X5 cross-task top-1 retrieval curve | post-defence CPU | **done** | prereg.json X5 | 381_stage13/reports/x5_retrieval.md; report Part 5 |
| Stage 13 (prereg.json) | M5 (CPU part: name-position true/false discrimination, probe true vs false run) | post-defence CPU | **done** | none (post hoc) | 381_stage13/reports/m5_report.md; report Part 5 |
| Stage 13 (prereg.json) | X2 subspace patching | post-defence GPU | **done** | addendum 6 | 381_stage13/reports/x2_report.md; report Part 4 X2 (H3 passes by rule, downgraded) |
| Post-defence | Group comparisons A/B/C/D (P1, P2-first, P2-other, P3) | post-defence CPU | **done** | addenda 7, 8 | 391_groups/primary.csv; report Part 5 |
| Post-defence | Re-runs R2 × strong (204) and R0 × uncertain (600): E1, E2, P1/P2 | post-defence GPU | **done** | addendum 8 | 391_groups/reports/rerun_report.md, e1_num_den.md |
| Post-defence | P1/P2 numerator / denominator by group | post-defence CPU | **done** | addendum 8 (analysis) | 391_groups/summary_rerun/p1_p2_num_den_B_minus_A.csv |
| Post-defence | CPU leftovers M3 scores, N2 by layer, paper vs team CIs (V42) | post-defence CPU | **done** | none (post hoc) | 381_stage13/reports/m3_scores.md, v42_paper_vs_team.md; 371_stage12/reports/n2_layers.md |
| Post-defence | All-token title-position probe by role (+ permutation controls) | post-defence GPU + CPU | **done** | addendum 9 | 381_stage13/reports/e4b_alltok.md, alltok_deviations.md; report Part 4 |
| Batch 1 | 1 X1–X4 for all authors (incl. new S_auth) | batch 1 | **done** | addendum 10 item 1 | 381_stage13/reports/b1_xall_report.md (hard check PASS; conclusions unchanged); report Part 4 M3/X1/X4 box + Part 5 #pd-b1-xall |
| Batch 1 | 2 X7 with five false titles | batch 1 | **done** | addendum 10 item 2 | 381_stage13/reports/b1_x7f_report.md; report X7 (all three groups pass) |
| Batch 1 | 3 P1 / P2 with five false titles | batch 1 | **running** | addendum 10 item 3 | 187 / 194 units done, last chain job 11714726 pending (b1_p12f_gpu_v2.sbatch); analysis → 391_groups/reports/b1_p12f_report.md; placeholder #pd-b1-p12f |
| Batch 1 | 4 E4b and all-token probe minus five false titles (per-donor exclusion) | batch 1 | **done** | addendum 10 item 4; deviation D1 | 381_stage13/reports/b1_e4b5_report.md (hard check E4b L40 +0.0609 PASS); report #alltok-results + #pd-b1-e4b5 |
| CPU items | C-1 Stages 4–7 with a title contrast | CPU | **done** | addendum 13 | 381_stage13/reports/c13_C1.md; report Stage 7.1 |
| CPU items | C-2 Stage 8 CPU proxy | CPU | **done** | addendum 13 | 381_stage13/reports/c13_C2.md; report Stage 8 |
| CPU items | C-3 E4b / all-token probe without the title-reuse exclusion | CPU | **done (sensitivity only)** | addendum 13 | 381_stage13/reports/c13_C3.md |
| CPU items | C-3b same for the five-false-title version | CPU | **done (sensitivity only)** | addendum 13 | 381_stage13/reports/c13_C3b.md (hard check PASS; includes leakage, not a conclusion) |
| CPU items | C-4 M1 with false_1..false_4 | CPU | **done** | addendum 13 | 381_stage13/reports/c13_C4.md |
| CPU items | C-5 Stage 10 extras at every stored layer | CPU | **done** | addendum 13 | 381_stage13/reports/c13_C5.md |
| CPU items | Strict number check: register the ~1,024 uncovered conclusion-like numbers (report 249, handbook 381, talk docs 151, notes 113, others 130) | CPU | **queued** | user 2026-11-07 | advisor + its PPT slides done first (claims_defs_v5) |
| CPU items | D13-1 deviation record: Stage 8 W GPU re-run triggered by C-2 but not run | CPU | **in progress** | addendum 13 C-2 | int6 vs locked 7-layer check first |
| Batch 2 | A name-position probe (direct H3 test) | batch 2 | **code ready, queued (auto)** | addendum 11 A | after batch 1; code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1 |
| Batch 2 | B groups C and D completed for E1 / E2 | batch 2 | **code ready, queued (auto)** | addendum 11 B | after batch 1; code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1 |
| Batch 2 | 2-1 Stage 9 Fit B and holdout | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1; deviation D12 (prereg_addendum12_deviations.json) |
| Batch 2 | 2-2 F1 author-lens split-half | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1; deviation D12 (prereg_addendum12_deviations.json) |
| Batch 2 | 2-3 X3 by token role | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1 |
| Batch 2 | 2-4 E1 batch rounding noise | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1 |
| Batch 2 | 2-7 Patchscope at the name positions (M5 GPU part) | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1; source = year-free X4 prompt (deviation, b2_groupA_handoff.md) |
| Batch 2 | 2-8 E1t with five false titles | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1 |
| Batch 2 | 2-9 X4 role split, remaining layers | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1 |
| Batch 2 | 2-10 M3 all-token score | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1 |
| Batch 2 | 2-11 model-generated names (user item) | batch 2 | **code ready, queued (auto)** | addendum 12 | code + tiny + hard-check unit tests done; 13_stage13/b2_orch starts it after batch 1; deviation D12 (prereg_addendum12_deviations.json) |
| Batch 3 | 3-1 Stage 10 L41–L47 and L49 (6,841 papers, logit + public J-lens) | batch 3 | **code ready, queued (after batch 2)** | addendum 14 | starts after batch 2; hard check = L24 / L48 reproduction |
| Batch 3 | 3-2 Stage 10 L0–L23 | batch 3 | **code ready, queued (after batch 2)** | addendum 14 | after 3-1 |
| Batch 3 | 3-3 Stage 7.1B fast path | batch 3 | **stopped (option a)** | addendum 14; deviation D14-1 (draft, awaiting user confirmation) | original hard check 79.8% < 99%; cause bf16 rounding by forward-length class; revised equivalence criterion (locked before results) not met: paper-level Welch [−0.0207, +0.0324] vs ±0.02; fp32 reference (C2) running for the limitation note only; 381_stage13/b3_33_*/ |
| Batch 3 | 3-4 Stage 8 GPU re-run of the original W | batch 3 | **not done** | addendum 13 C-2 rule | user decision 2026-11-06 (b); CPU proxy C-2 reported instead; 3-5 depends on it (not done) — addendum 14 |
| Not done by choice | V20 (V100 path) | — | **not done** | — | not applicable |
| Cannot be redone | One model; teacher forcing; label pipeline (elm code, run.json); 4097+ bin has no B / D papers | — | **limitation** | — | report §8 and Part 5 "不能补做的局限" |

Counts: done 20, not done 3, running 1, done (sensitivity only) 2, code ready, queued (auto) 11, code ready, queued (after batch 2) 2, stopped (option a) 1, limitation 1

## 2026-11-08 状态更新（v30 同步时写）
- 第一批：全部完成（P1/P2 五个假标题为主结果，false_0 版并列；已写入报告 v30）。
- 第二批：C/D 组补全完成（R4，已写入 v30）；名字位置 probe、2-1 Fit B、2-2 F1 对半、2-3/2-4/2-8/2-10、2-7/2-9 运行中；2-11 停止 → 2-11b（补充 15，已锁定 sha256 8b903d2f…）只跑第 0 片，等用户看成本后决定其余 47 片。
- M2 五个假标题重做（CPU，用户 2026-11-08 批准）：进行中，先做复现 false_0 的硬检查。
- 第三批：3-1、3-2 排队（第二批结束后自动开始）；3-3 停止（D14-1 已锁定）；3-4、3-5 不做（D13-1）。
- 没有计划：Stage 10 的 L25–L31、L33–L39（局限 L01）；M5 B 部分和 E4b X1 对照流程的 5 个假标题版（局限 L05）。
