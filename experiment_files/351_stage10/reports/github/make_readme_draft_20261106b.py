"""GitHub README draft 2026-11-06 b (local only, not pushed): README_draft_20261106.md + batch-1 results (user-confirmed wording, short) and the
progress table rewritten as one line per item (what, conclusion, status, source file). Writes README_draft_20261106b.md; the input is not changed."""
from pathlib import Path
D = Path(__file__).parent
s = (D / 'README_draft_20261106.md').read_text(encoding='utf-8')
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:60]); s = s.replace(a, b)
R = lambda t: f' <sub>({t})</sub>'

rep('(v29 prepared 2026-11-06)', '(v29 prepared 2026-11-06, batch-1 results added)')
rep('''- Running (batch 1): X1–X4 for all authors; P1 / P2 with five false titles; E4b minus five false titles. Queued (batch 2, addenda 11–12): name-position probe, groups C / D for E1 / E2, Stage 9 Fit B, F1 split-half, X3 by role, and others. Not done: Stage 8 GPU re-run of W (user decision).''',
f'''- Batch 1 (addendum 10), done: X1–X4 re-scored on all authors and all name tokens — conclusions unchanged (X1 task-independent, small L48 author − year +0.024 [0.019, 0.030]; X3 keeps about 90%; X4 from L8; X2 with an all-author subspace moves 0.032, held-out R² ≤ 0.009, H3 still insufficient){R('381_stage13/reports/b1_xall_report.md')}. E4b minus five false titles (per-donor exclusion, 4,654 papers): surname first token at L40 +0.076 [0.068, 0.083], surname − initial +0.033 [0.023, 0.042]; surname target − control positive from L24 (L40 +0.030, L56 +0.058){R('b1_e4b5_report.md')}. C-3b (no title-reuse exclusion; includes leakage, sensitivity only){R('c13_C3b.md')}.
- Batch 1, running: P1 / P2 with five false titles (116 / 194 units done).
- Batch 2 (addenda 11–12): code, tiny tests and hard-check unit tests done; starts automatically after batch 1; deviations D12-1..D12-3{R('381_stage13/config/prereg_addendum12_deviations.json')}. Batch 3 (addendum 14: Stage 10 L41–L47, L49; L0–L23; Stage 7.1B fast path): code in progress. Not done: Stage 8 GPU re-run of W (user decision).''')

i = s.index('## Status\n'); j = s.index('| Raw files not in the repo |', i); j = s.index('\n', j) + 1
STATUS = '''## Status

One line per item: what it is, the conclusion, the status, and the result file (paths relative to `experiment_files/`).

| Item | What | Conclusion | Status | Source |
|---|---|---|---|---|
| Stages 4–8D, 8E | small-sample signal and replication | true title helps; Stage 8 frozen endpoint +2.41 pp | done (8E recomputed 2026-10-30) | 351_stage8/recompute_2026-10-30/ |
| Stage 9 Fit A | Jacobian lens fit A (Stage 9 protocol) | used as the fitA lens in Stage 10 | done | 351_stage9/ |
| Stages 10–12 | full-cohort readout, intervention, positions / components | read early (L44–L52), spoken late (L57–L61) | done | 351_stage10/, 361_stage11/, 371_stage12/ |
| Stage 13 M1–M4, X1–X7 | what the middle layers hold | H2 partly supported, not established; H3 insufficient | done | 381_stage13/reports/ |
| Group comparisons (addenda 7, 8) | A/B/C/D, re-runs | recognised R0 +0.200 [0.188, 0.213] at the output | done | 391_groups/primary.csv |
| Addendum 9 | all-token title-position probe | surname first token L40 +0.071 [0.058, 0.085] | done | 381_stage13/reports/e4b_alltok.md |
| Addendum 13 C-1..C-5 | CPU redo items | Stage 7.1 holds at output / L62; Stage 8 CPU proxy RQ1 +0.130, RQ2 +0.054 | done | 381_stage13/reports/c13_C1.md–c13_C5.md |
| Addendum 13 C-3b | no-exclusion sensitivity, five false titles | includes leakage, not a conclusion | done (sensitivity only) | 381_stage13/reports/c13_C3b.md |
| Batch 1 item 1 | X1–X4 for all authors | conclusions unchanged | done (hard check PASS) | 381_stage13/reports/b1_xall_report.md |
| Batch 1 item 2 | X7 with five false titles | all three groups pass (S(L52) +0.022 / +0.042 / +0.028) | done | 381_stage13/reports/b1_x7f_report.md |
| Batch 1 item 3 | P1 / P2 with five false titles | — | running (116 / 194 units) | 391_groups/reports/b1_p12f_report.md (when done) |
| Batch 1 item 4 | E4b minus five false titles (per-donor exclusion) | surname L40 +0.076 [0.068, 0.083] | done (hard check PASS) | 381_stage13/reports/b1_e4b5_report.md |
| Batch 2 (addenda 11, 12) | name-position probe; groups C / D for E1 / E2; Stage 9 Fit B + holdout; F1 split-half; X3 by role; E1 batch noise; name-position patchscope; E1t five titles; X4 roles; M3 all tokens; model-generated names | — | code ready, queued (starts automatically after batch 1) | 381_stage13/config/prereg_addendum11.json, prereg_addendum12.json |
| Batch 3 (addendum 14) | 3-1 Stage 10 L41–L47, L49; 3-2 L0–L23; 3-3 Stage 7.1B fast path | — | code in progress | 381_stage13/config/prereg_addendum14.json |
| Not done | Stage 7.1B (superseded by Stage 10); Stage 8 GPU re-run of W (3-4, 3-5; user decision 2026-11-06) | — | not done | — |

Raw files not in the repo: Stage 10–13 raw/ (regenerable, > 20 MB).
'''
s = s[:i] + STATUS + s[j:]
assert 'minyan' not in s.lower()
(D / 'README_draft_20261106b.md').write_text(s, encoding='utf-8'); print('wrote README_draft_20261106b.md')
