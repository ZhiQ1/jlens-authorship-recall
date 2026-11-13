"""Round p (2026-11-12, LOCAL only), gaps from the round-o check (out_20261112_154253/wording_v30/):
(a) process report §5 item 4: addendum-9 all-token version by role as main (same wording as report §6.11), old first-token in "（旧版只打首 token：…）";
(b) deck-note footer on E4b (notes 24, 25, 28, 31, 39, 40, 59, 73) rewritten so it no longer contradicts the all-token main numbers (all old-number main sentences were switched in round n);
(c) C15 all-author sentence in the talk-doc progress report and the Stage 13 script (zh + en); (d) report overview "事后、探索性" -> "事后，探索性".
Backups *.before_20261112p. Process page rebuilt; K regenerated (report changed). Manifest "round p"."""
import json, re, shutil, subprocess, sys
from pathlib import Path
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'; PY = sys.executable
REP = R / 'stage1_11/stage1_11_report.html'; NOTES = R / 'talk/src/export/notes_zh.json'; PROCMD = R / 'process_report/draft_zh.md'
PRD = R / 'talk_docs/progress_report_for_advisor_zh.html'; S13 = R / 'talk_docs/stage13_script_zh_en.html'; K = R / 'methods/parts/K_post_defence.html'
HB = R / 'methods/methods_handbook.html'; PROCH = R / 'process_report/index.html'
EDIT = [REP, NOTES, PROCMD, PRD, S13, K]
for p in EDIT + [HB, PROCH]: assert not Path(str(p) + '.before_20261112p').exists(), p
S = {p: p.read_text(encoding='utf-8') for p in EDIT}; NJ = json.loads(S[NOTES]); LOG = []
def R_(old, new, files, n=None):
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
    assert tot >= 1 and (n is None or tot == n), (old[:70], tot, n)
NK = [('N', k) for k in NJ]
ROLE = '全部作者、全部名字 token、按角色（补充 9，预注册版 V0，只减 false_0）L24 / L40 / L56：名的第一个 token +0.098 / +0.124 / +0.163，姓的第一个 token +0.058 / +0.071 / +0.098，首字母 +0.021 / +0.044 / +0.054'
assert ROLE in S[REP]
R_('标题位置 probe 少量信号（E4b，target + control 1,395 篇：L24 +0.050、L40 +0.061、L56 +0.075），只打首 token。', '标题位置 probe 少量信号（' + ROLE + '；旧版只打首 token：E4b，target + control 1,395 篇：L24 +0.050、L40 +0.061、L56 +0.075）。', [PROCMD], 1)
R_('注意：这个 probe 只给每位作者名字的第一个 token 打分（73% 的名字以首字母开头，多数时候是首字母）；给全部名字 token 打分、按首字母 / 名 / 姓分开的版本（补充 9）已完成，见 Stage 13 部分的补充 9 页：L40 姓的第一个 token +0.071 [0.058, 0.085]',
   '注意：旧版 E4b 只给每位作者名字的第一个 token 打分（73% 的名字以首字母开头，多数时候是首字母）；上面的主数字是给全部名字 token 打分、按首字母 / 名 / 姓分开的版本（补充 9，见 Stage 13 部分的补充 9 页）：L40 姓的第一个 token +0.071 [0.058, 0.085]、名的第一个 token +0.124 [0.108, 0.142]、首字母 +0.044 [0.030, 0.057]', NK, 8)
ADD = '全作者版本同样从 L8 起可解码（测试集 +0.048 [0.039, 0.058]，按调参集选层、测试集确认）'
R_('X4 先解码出第一作者（L8）再解码年份（L40），和 H2 预测的顺序相反；', 'X4 先解码出第一作者（L8）再解码年份（L40），和 H2 预测的顺序相反（' + ADD + '）；', [PRD], 1)
R_('另外 X4 最早解码出的是第一作者（L8），年份要到 L40，', '另外 X4 最早解码出的是第一作者（L8；' + ADD + '），年份要到 L40，', [S13], 1)
R_('a probe reads a little of the first author from L8 (+0.046)', 'a probe reads a little of the first author from L8 (+0.046; the all-author version is also decodable from L8, test +0.048 [0.039, 0.058], tune-selected and confirmed on test)', [S13], 1)
R_('事后、探索性的', '事后，探索性的', [REP], 1)
src = (R / 'sync_20261107/apply_20261108c.py').read_text(encoding='utf-8'); exec(src[src.index('def makeK(rep_html):'):src.index('Kold = RAW[')])
lead = '与《Stage 1–13 实验报告》第 30 版第五部分内容相同（图号、表号沿用报告）。</p>\n'
kk = makeK(S[REP])
for x in ['np', 'f1', 'gn', 'ps']: kk = kk.replace(f'id="pd-b2-{x}"', f'id="k-b2-{x}"')
S[K] = S[K][:S[K].index(lead) + len(lead)] + kk + '\n</section>'; LOG.append(('methods/parts/K_post_defence.html', '(part 5)', '(regenerated from the report)', 1))
S[NOTES] = json.dumps(NJ, ensure_ascii=False, indent=1); json.loads(S[NOTES])
for p in EDIT + [HB, PROCH]: shutil.copy2(p, Path(str(p) + '.before_20261112p'))
for p in EDIT:
    if S[p] != p.read_text(encoding='utf-8'): p.write_text(S[p], encoding='utf-8')
subprocess.run([PY, str(R / 'methods/build_methods.py')], check=True, cwd=str(R / 'methods'))
subprocess.run([PY, str(R / 'process_report/build_process_report.py')], check=True, cwd=str(R / 'process_report'))
cut = lambda s, n=150: (s if len(s) <= n else s[:n] + '…').replace('|', '\\|').replace('\n', ' ')
md = ['', '## round p', '', 'Script `sync_20261107/apply_20261112p.py` (backups `*.before_20261112p`; gaps from out_20261112_154253/wording_v30/).', '',
      '| # | file | before | after | count |', '|---|---|---|---|---|'] + [f'| p{i} | {cut(f, 70)} | {cut(o)} | {cut(n)} | {k} |' for i, (f, o, n, k) in enumerate(LOG, 1)]
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write('\n'.join(md) + '\n')
print('round p:', len(LOG))
