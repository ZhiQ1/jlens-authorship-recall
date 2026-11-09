"""Sync 2026-11-08 e (round e, LOCAL only). 1) user wording for the old "C 略晚（36 篇）" sentence (report Stage 10 R1 section + scope table; it occurs nowhere else);
2) "约 79% 本应剔除" qualified with the recomputed shares (381_stage13/e4b_standardisation_check/v5x0_leak_share.py/.json: surname 4,402 / 5,580 = 78.89%;
given name 2,894 / 6,824 = 42.4%; initial 4,567 / 6,360 = 71.8%). Fresh backups *.before_20261108e; K regenerated, handbook + process page rebuilt; manifest "round e"."""
import json, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; PY = sys.executable
REP = R / 'stage1_11/stage1_11_report.html'; NOTES = R / 'talk/src/export/notes_zh.json'; ADV = R / 'advisor/index.html'; PROCMD = R / 'process_report/draft_zh.md'
AUD = J / 'audit_20261105/scoring_audit.html'; ADD = R / 'pages_20261106b/methods_addendum/index.html'; READ = R / 'github/README_draft_20261106b.md'
S13 = R / 'talk_docs/stage13_script_zh_en.html'; PRD = R / 'talk_docs/progress_report_for_advisor_zh.html'; F13 = R / 'methods/parts/F_stage13.html'; K = R / 'methods/parts/K_post_defence.html'
HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, NOTES, ADV, PROCMD, AUD, ADD, READ, S13, PRD, F13, K]
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + '.before_20261108e').exists(), p
lk = json.loads((J / '381_stage13/e4b_standardisation_check/v5x0_leak_share.json').read_text())
sf, gf, ini = lk['surname_first'], lk['given_first'], lk['initial']
assert (sf['numerator'], sf['denominator'], sf['v5x0_papers']) == (4402, 5580, 1395) and abs(sf['share'] - 0.789) < 0.0005 and sf['matches_stored_dropped_k']
S = {p: p.read_text(encoding='utf-8') for p in EDIT}; NJ = json.loads(S[NOTES]); LOG = []
def R_(old, new, files, n):
    tot = 0
    for p in files:
        if isinstance(p, tuple): t = NJ[p[1]]['text']
        else: t = S[p]
        c = t.count(old)
        if not c: continue
        t = t.replace(old, new); tot += c
        if isinstance(p, tuple): NJ[p[1]]['text'] = t
        else: S[p] = t
        LOG.append((('notes_zh.json #' + p[1]) if isinstance(p, tuple) else str(p).replace(str(R) + '/', ''), old, new, c))
    assert tot == n, (old[:60], tot, n)
CW = '补全前（C 组 36 篇）曾观察到 C 略晚；补全到 462 篇后（档内可比 258 篇），C 与 A 的时间点相同、信号更大（分母 C − A +0.075 [+0.024, +0.130]），原观察未被重现'
R_('也就是说，R1 论文的标题信息被读取得略晚一点，但完成时间相同。', CW + '<span class="src">（391_groups/reports/b2_cd_report.md Contrasts 表；补全前 36 篇：361_stage11/summary_r0r1/stage11_curves_by_recall.csv）</span>。', [REP], 1)
R_('“略晚”在补全后的同一引用档比较中没有得到确认（见第五部分 C / D 组补全）。', '', [REP], 1)
R_('<td>同样 L52 完成；36 篇中 L40–48 略慢，补全到 462 篇后同一引用档内时间点与 A 相同（补充 11 B）</td>',
   '<td>同样 L52 完成；' + CW + '<span class="src">（391_groups/reports/b2_cd_report.md）</span></td>', [REP], 1)
ZH_OLD = 'false_1..4 中约 79% 本应剔除'
ZH_NEW = ('false_1..4 中约 79% 本应剔除（姓的 1,395 篇：4,402 / 5,580；名 42%、首字母 72%；381_stage13/e4b_standardisation_check/v5x0_leak_share.json）')
R_(ZH_OLD, ZH_NEW, [REP, ADV, PROCMD, AUD, ADD, S13, PRD, F13, ('N', '72')], 11)
EN_OLD = 'about 79% of false_1..4 should have been excluded'
EN_NEW = 'about 79% of false_1..4 should have been excluded (surname set, 1,395 papers: 4,402 / 5,580; given name 42%, initial 72%; v5x0_leak_share.json)'
R_(EN_OLD, EN_NEW, [READ, S13], 2)
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); import re
exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
S[K] = S[K][:S[K].index(lead) + len(lead)] + makeK(S[REP]) + '\n</section>'; LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + '.before_20261108e'))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round e', '', 'Script `sync_20261107/apply_20261108e.py` (backups `*.before_20261108e`). Leak share recomputed by `381_stage13/e4b_standardisation_check/v5x0_leak_share.py` (json/md beside it): surname 4,402 / 5,580 = 78.89% (target 78.35%, control 79.86%; matches stored dropped_k); given name 2,894 / 6,824 = 42.4%; initial 4,567 / 6,360 = 71.8%. "约 79%" kept and qualified as the surname set.', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| e{i} | {cut(f, 70)} | {cut(o)} | {cut(n) or "(deleted)"} | {c} |' for i, (f, o, n, c) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round e:', len(LOG))
