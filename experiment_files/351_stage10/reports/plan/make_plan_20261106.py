"""Master queue / plan document (2026-11-06): every experiment item with batch, status, addendum and where the result is.
Writes plan_master_queue_20261106.{md,html,pdf}. Status as of 2026-11-06 ~04:10 EST (PROGRESS.md entries up to 03:45 + squeue)."""
import html, sys
from pathlib import Path
D = Path(__file__).parent
R13 = '381_stage13/reports/'
ROWS = [  # (group, item, batch, status, addendum / rule, result or note)
 ('Stage 1–12', 'Stage 1–12 (cohort, protocol, lenses, Stages 4–11, Stage 12 P1/P2/N1/N2/F1/F2)', 'before defence', 'done', 'frozen protocols; Stage 10 analysis_plan', 'report Parts 1–4; handbook C–E'),
 ('Stage 1–12', 'Stage 7.1B terminal readout', 'before defence', 'not done', '—', 'stopped at 1,166 / 15,519; superseded by Stage 10; job 11637611 cancelled 2026-11-05 (user)'),
 ('Stage 1–12', 'Stage 9 Fit A', 'before defence', 'done', 'Stage 9 protocol', 'used as fitA lens in Stage 10'),
 ('Stage 13 (prereg.json)', 'M1, M2, M2b, M2c, M3', 'before defence', 'done', 'prereg.json; addenda 1, 2', 'report Part 4; handbook F'),
 ('Stage 13 (prereg.json)', 'M4 = Stage 12 F1 / F2', 'before defence', 'done', 'prereg.json', 'report Part 4 (Stage 12)'),
 ('Stage 13 (prereg.json)', 'X1, X3, X4, X5, X6, X7', 'before defence', 'done', 'prereg.json; addenda 2–5', 'report Part 4'),
 ('Stage 13 (prereg.json)', 'X5 cross-task top-1 retrieval curve', 'post-defence CPU', 'done', 'prereg.json X5', R13 + 'x5_retrieval.md; report Part 5'),
 ('Stage 13 (prereg.json)', 'M5 (CPU part: name-position true/false discrimination, probe true vs false run)', 'post-defence CPU', 'done', 'none (post hoc)', R13 + 'm5_report.md; report Part 5'),
 ('Stage 13 (prereg.json)', 'X2 subspace patching', 'post-defence GPU', 'done', 'addendum 6', R13 + 'x2_report.md; report Part 4 X2 (H3 passes by rule, downgraded)'),
 ('Post-defence', 'Group comparisons A/B/C/D (P1, P2-first, P2-other, P3)', 'post-defence CPU', 'done', 'addenda 7, 8', '391_groups/primary.csv; report Part 5'),
 ('Post-defence', 'Re-runs R2 × strong (204) and R0 × uncertain (600): E1, E2, P1/P2', 'post-defence GPU', 'done', 'addendum 8', '391_groups/reports/rerun_report.md, e1_num_den.md'),
 ('Post-defence', 'P1/P2 numerator / denominator by group', 'post-defence CPU', 'done', 'addendum 8 (analysis)', '391_groups/summary_rerun/p1_p2_num_den_B_minus_A.csv'),
 ('Post-defence', 'CPU leftovers M3 scores, N2 by layer, paper vs team CIs (V42)', 'post-defence CPU', 'done', 'none (post hoc)', R13 + 'm3_scores.md, v42_paper_vs_team.md; 371_stage12/reports/n2_layers.md'),
 ('Post-defence', 'All-token title-position probe by role (+ permutation controls)', 'post-defence GPU + CPU', 'done', 'addendum 9', R13 + 'e4b_alltok.md, alltok_deviations.md; report Part 4'),
 ('Batch 1', '1 X1–X4 for all authors (incl. new S_auth)', 'batch 1', 'running', 'addendum 10 item 1', 'GPU 21/96 units at 03:45; jobs 11667759, 11667761 pending; placeholder in report Part 5'),
 ('Batch 1', '2 X7 with five false titles', 'batch 1', 'done', 'addendum 10 item 2', R13 + 'b1_x7f_report.md; report X7 (all three groups pass)'),
 ('Batch 1', '3 P1 / P2 with five false titles', 'batch 1', 'running', 'addendum 10 item 3', 'chain 11665128 (AUTO); placeholder in report Part 5'),
 ('Batch 1', '4 E4b and all-token probe minus five false titles (per-donor exclusion)', 'batch 1', 'running', 'addendum 10 item 4; deviation D1', 'probe array 11663811, reports 11667411 / 11663812; placeholder in report'),
 ('CPU items', 'C-1 Stages 4–7 with a title contrast', 'CPU', 'done', 'addendum 13', R13 + 'c13_C1.md; report Stage 7.1'),
 ('CPU items', 'C-2 Stage 8 CPU proxy', 'CPU', 'done', 'addendum 13', R13 + 'c13_C2.md; report Stage 8'),
 ('CPU items', 'C-3 E4b / all-token probe without the title-reuse exclusion', 'CPU', 'done (sensitivity only)', 'addendum 13', R13 + 'c13_C3.md'),
 ('CPU items', 'C-3b same for the five-false-title version', 'CPU', 'queued', 'addendum 13', 'after batch 1 item 4'),
 ('CPU items', 'C-4 M1 with false_1..false_4', 'CPU', 'done', 'addendum 13', R13 + 'c13_C4.md'),
 ('CPU items', 'C-5 Stage 10 extras at every stored layer', 'CPU', 'done', 'addendum 13', R13 + 'c13_C5.md'),
 ('Batch 2', 'A name-position probe (direct H3 test)', 'batch 2', 'queued', 'addendum 11 A', 'after batch 1'),
 ('Batch 2', 'B groups C and D completed for E1 / E2', 'batch 2', 'queued', 'addendum 11 B', 'after batch 1'),
 ('Batch 2', '2-1 Stage 9 Fit B and holdout', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-2 F1 author-lens split-half', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-3 X3 by token role', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-4 E1 batch rounding noise', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-7 Patchscope at the name positions (M5 GPU part)', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-8 E1t with five false titles', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-9 X4 role split, remaining layers', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-10 M3 all-token score', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 2', '2-11 model-generated names (user item)', 'batch 2', 'queued', 'addendum 12', ''),
 ('Batch 3', '3-4 Stage 8 GPU re-run of the original W', 'batch 3', 'not done', 'addendum 13 C-2 rule', 'user decision 2026-11-06 (b); CPU proxy reported instead'),
 ('Batch 3', 'further batch-3 items (PROGRESS.md 2026-11-05 22:30: item 9 CPU substitute first; item 10 on 6,841 papers, logit + public, L41–L47, L49)', 'batch 3', 'not written', 'no addendum on disk yet', ''),
 ('Not done by choice', 'V20 (V100 path)', '—', 'not done', '—', 'not applicable'),
 ('Cannot be redone', 'One model; teacher forcing; label pipeline (elm code, run.json); 4097+ bin has no B / D papers', '—', 'limitation', '—', 'report §8 and Part 5 "不能补做的局限"'),
]


def md():
    L = ['# jlens master queue (plan document)', '', 'Status as of 2026-11-06 ~04:10 EST. Rules of every redo item were fixed and locked (sha256) before its results; reproducing the published numbers is a hard check. Sources: `~/jlens_work/PROGRESS.md`, `381_stage13/config/prereg_addendum*.json`, `391_groups/config/`.', '',
         '| group | item | batch | status | addendum / rule | result / note |', '|---|---|---|---|---|---|']
    L += [f'| {g} | {i} | {b} | **{s}** | {a} | {r} |' for g, i, b, s, a, r in ROWS]
    from collections import Counter
    c = Counter(s for _, _, _, s, _, _ in ROWS)
    L += ['', 'Counts: ' + ', '.join(f'{k} {v}' for k, v in c.items())]
    return '\n'.join(L) + '\n'


def page():
    color = {'done': '#2F7D3B', 'running': '#B45309', 'queued': '#1D6FB8', 'not done': '#6B7280', 'not written': '#6B7280', 'limitation': '#B42318', 'done (sensitivity only)': '#2F7D3B'}
    tr = ''.join(f'<tr><td>{html.escape(g)}</td><td>{html.escape(i)}</td><td>{html.escape(b)}</td><td><span class="st" style="background:{color.get(s, "#555")}">{html.escape(s)}</span></td><td>{html.escape(a)}</td><td>{html.escape(r)}</td></tr>' for g, i, b, s, a, r in ROWS)
    return f'''<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Master queue</title>
<style>:root{{--bg:#F7F7F4;--ink:#1F2937;--pen:#5B6474;--line:#E3E6EA;--card:#fff}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#13171d;--ink:#E7EAF0;--pen:#A3ADBD;--line:#2D3645;--card:#1B2230}}}}
:root[data-theme="dark"]{{--bg:#13171d;--ink:#E7EAF0;--pen:#A3ADBD;--line:#2D3645;--card:#1B2230}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.55 "Noto Sans SC",system-ui,sans-serif;padding:0 16px}}
.wrap{{max-width:1100px;margin:0 auto;padding:28px 0}} h1{{font-size:26px;margin:0 0 6px}} p{{color:var(--pen)}}
.tw{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;background:var(--card);font-size:13.5px}}
th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}} th{{color:var(--pen)}}
.st{{color:#fff;border-radius:4px;padding:0 6px;font-weight:700;white-space:nowrap}}
@media print{{body{{background:#fff}} table{{font-size:9pt}} tr{{break-inside:avoid}}}}</style></head><body><div class="wrap">
<h1>jlens 计划总表（master queue）</h1><p>截至 2026-11-06 约 04:10 EST。每个重做项目的规则都在看结果前写定并锁定（sha256）；复现已发表数字是硬检查。来源：~/jlens_work/PROGRESS.md、381_stage13/config/prereg_addendum*.json、391_groups/config/。</p>
<div class="tw"><table><thead><tr><th>组</th><th>项目</th><th>批次</th><th>状态</th><th>补充 / 规则</th><th>结果 / 备注</th></tr></thead><tbody>{tr}</tbody></table></div></div></body></html>'''


if __name__ == '__main__':
    (D / 'plan_master_queue_20261106.md').write_text(md(), encoding='utf-8')
    (D / 'plan_master_queue_20261106.html').write_text(page(), encoding='utf-8')
    if '--pdf' in sys.argv:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(); pg = b.new_page()
            pg.goto((D / 'plan_master_queue_20261106.html').as_uri(), wait_until='networkidle'); pg.emulate_media(media='print')
            out = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/downloads/plan_master_queue_20261106_A4.pdf')
            pg.pdf(path=str(out), format='A4', landscape=True, print_background=True, margin=dict(top='12mm', bottom='12mm', left='10mm', right='10mm')); b.close()
            print('pdf', out)
    print('ok')
