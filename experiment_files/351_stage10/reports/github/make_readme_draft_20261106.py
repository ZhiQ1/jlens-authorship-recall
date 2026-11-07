"""GitHub README draft (2026-11-06; local only, not pushed): the repo README (2026-10-30) updated to Stages 1-13, post-defence work and
the redo programme. Source tags as <sub>(…)</sub>. Writes README_draft_20261106.md next to this script."""
from pathlib import Path
SRC = Path('/scratch/zhang.zhiqi2/jlens-authorship-recall_update/README.md')
s = SRC.read_text(encoding='utf-8')
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:60]); s = s.replace(a, b)
R = lambda t: f' <sub>({t})</sub>'

rep('''> **Current documents (Stages 1–11, kept up to date; all new results go only into these two):**
> - **Slides:** [Stage 1–11 merged deck](https://claude.ai/artifact/XcgK4YF2dYQxudWfhk8MsD)
> - **Report:** [Stage 1–11 combined experiment report](https://claude.ai/artifact/QB335qoaBWvSdFyfvc2bSe)''',
'''> **Current documents (Stages 1–13 and the post-defence work, kept up to date):**
> - **Report:** [Stage 1–13 experiment report](https://claude.ai/artifact/QB335qoaBWvSdFyfvc2bSe) (v29 prepared 2026-11-06)
> - **Slides:** [Stage 1–13 merged deck](https://claude.ai/artifact/XcgK4YF2dYQxudWfhk8MsD) (v20 prepared 2026-11-06, 82 slides)
> - **Methods handbook:** [Stage 1–13 methods handbook](https://claude.ai/artifact/W7r7xVte3eaNcbo8D8cybo) (2026-11-06)
> - **Downloads (PDF / pptx):** [download page](https://claude.ai/artifact/5Tdt1mQa8xnPiqQEKvjzta)''')

ADD = f'''
**Stages 11–13 in one paragraph.** Patching the tokens after the title recovers 0.82 of the true − false-title gap at L48 and all of it from L52{R('Stage 11 E1, 593 + 593 papers; 361_stage11/summary/E1_recovery.csv')}; blocking attention to the title from L52 on costs nothing{R('Stage 11 E2')}. With all five false titles the knockout claim holds in target, control and all papers (S(L52) +0.022 / +0.042 / +0.028){R('addendum 10 item 2; 381_stage13/reports/b1_x7f_report.md')}. A linear probe at the last title token reads paper-specific name information from L24; scored on every name token (addendum 9), the surname first token gives +0.071 [0.058, 0.085] at L40, above the initial (+0.044){R('381_stage13/reports/e4b_alltok.md')}. Stage 13 finds paper attributes readable at the title early (M2) and a task-independent replacement effect (X1), but no paper-identity level above the L4 text level (M3, X5 retrieval), and X2 subspace patching moves only about 4% of the full replacement{R('381_stage13/reports/x2_report.md')}. Overall: **H2 (paper identity) partly supported but not established; H3 (hidden author knowledge) insufficient evidence.**

**Post-defence (2026-11-05/06).** Group comparisons fixed before the results (addenda 7, 8): on unwritten authors, recognised R0 papers beat unrecognised ones by +0.200 [0.188, 0.213] at the output{R('391_groups/primary.csv, P1')}; the signal rises by +0.059 per multiple-choice order right{R('P3')}; partial recall adds +0.061 for co-authors{R('P2-other')}. A redo programme (addenda 10–13) re-runs the weak points with five false titles, all authors and all name tokens; see the plan document `docs/plan_master_queue_20261106.md` (to be copied in at the next sync).
'''
rep('This does not support claims of full author-identity recovery', ADD.strip() + '\n\nThis does not support claims of full author-identity recovery')

STAGES = f'''
### Stage 12 · Single positions, attention vs MLP, name priors, author-prompt lens
- Key numbers: the colon alone carries at most 0.17 of the gap at L52, all name positions 0.85{R('371_stage12/summary/P1_patch_pos.csv')}; attention at L48 +0.23, MLP at L52–L56 +0.18 to +0.22{R('P2_patch_comp.csv')}; a pure name prior gives target − control +0.047 vs +0.247 with the true title{R('371_stage12/reports/stage12_report.md')}.

### Stage 13 · What do the middle layers hold?
- M2: year, citations and field are readable at the last title token from L16{R('381_stage13/reports/m2_teamci.md')}. M3 / X5: no layer above the L4 text level. X1: replacement effect independent of the question (R 0.99 at L24, 0.92 at L40){R('x1_report.md')}. X3: paraphrase meaning beyond wording at L28–L40, not separable from paper identity. X4: first author decodable at L8 but possibly explained by the title text. X2: H3 passes by rule, H2 not supported, but the author subspace hardly decodes authors (held-out R² ≤ 0.003){R('x2_report.md')}.

### Redo programme (addenda 10–13, 2026-11-05/06)
- Done: X7 with five false titles; all-token probe (addendum 9); CPU items C-1 to C-5 (Stage 7.1 with a title contrast: holds at the output and L62, public J-lens 6-layer mean not significant{R('c13_C1.md')}; Stage 8 CPU proxy: RQ1 +0.130, RQ2 +0.054 multi-layer, L56 RQ2 n.s.{R('c13_C2.md; not the W statistic')}).
- Running (batch 1): X1–X4 for all authors; P1 / P2 with five false titles; E4b minus five false titles. Queued (batch 2, addenda 11–12): name-position probe, groups C / D for E1 / E2, Stage 9 Fit B, F1 split-half, X3 by role, and others. Not done: Stage 8 GPU re-run of W (user decision).
- Cannot be redone: one model; teacher forcing; label pipeline not on the cluster; the 4097+ citation bin has no B / D papers.
'''
rep('\n## Directory Map: Where to Find the Evidence', STAGES + '\n## Directory Map: Where to Find the Evidence')
rep('| Stage 11 | 361_stage11.py; stage11_analyze.py; stage11_keeper.py | 361_stage11/ (raw/ not included) |',
    '| Stage 11 | 361_stage11.py; stage11_analyze.py; stage11_keeper.py | 361_stage11/ (raw/ not included) |\n'
    '| Stage 12 | 371_stage12.py; stage12_*.py | 371_stage12/ (raw/ not included) |\n'
    '| Stage 13 | 381_stage13.py; 13_stage13/stage13_*.py (M1–M5, X1–X7, addenda 9–13) | 381_stage13/ (summaries, reports, config incl. prereg addenda; raw/ not included) |\n'
    '| Group comparisons | 14_groups/*.py (addenda 7, 8; re-runs) | 391_groups/ |')
i = s.index('## Status'); j = s.find('\n## ', i + 5); j = len(s) if j < 0 else j
s = s[:i] + '''## Status

| Status | Content |
|---|---|
| Done, archived | Stages 4–8D, 8E (recomputed 2026-10-30), Stage 9 Fit A, Stages 10–12, Stage 13 M1–M4, X1–X7, post-defence group comparisons and re-runs, addendum 9 all-token probe, addendum 13 CPU items |
| Running (batch 1, addendum 10) | X1–X4 for all authors; P1 / P2 with five false titles; E4b minus five false titles |
| Queued (batch 2, addenda 11–12) | name-position probe; groups C / D for E1 / E2; Stage 9 Fit B + holdout; F1 split-half; X3 by role; E1 batch noise; name-position patchscope; E1t five titles; X4 roles; M3 all tokens; model-generated names |
| Not done | Stage 7.1B (superseded by Stage 10); Stage 8 GPU re-run of W (user decision 2026-11-06) |
| Raw files not in the repo | Stage 10–13 raw/ (regenerable, > 20 MB) |
''' + s[j:]
assert 'minyan' not in s.lower()
out = Path(__file__).parent / 'README_draft_20261106.md'; out.write_text(s, encoding='utf-8'); print('wrote', out, len(s))
