"""2026-11-07 ~02:20 user decisions D, B, F (F1 NOT applied: see verify output), applied to all current local documents.
D  '100% from L52' -> '99.6% from L52' (report §1 en, deck slide 50); keys & shelves script 'L48 恢复 0.83' / 'recovers 0.83 at L48' -> 0.82.
B  the target - control sentence on the all-token probe (old 'mainly initials and given names' + wording a) -> the user's new sentence (zh / en),
   numbers recomputed here from 381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv (version Vpd).
F2-F4  hypothesis table: H3 cell / deck subtitle 'decodes nothing' -> 'can hardly decode authors (held-out R² ≤ 0.009)', all-author X2 refit
   (0.032, ~7% of full patching; summary_b1_xall/x2_verdict_new__all.csv), table date -> 第 29 版 2026-11-07.
Backups *.before_20261107b.* (report: *.before_20261107c.html, since .before_20261107b.html is the input of apply_20261107b.py)."""
import json, re, shutil, sys
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
FP = R / 'methods/parts/F_stage13.html'; ADV = R / 'advisor/index.html'; PROC = R / 'process_report/draft_zh.md'
ADD = R / 'pages_20261106b/methods_addendum/index.html'; AUD = J / 'audit_20261105/scoring_audit.html'
TPR = R / 'talk_docs/progress_report_for_advisor_zh.html'; T13 = R / 'talk_docs/stage13_script_zh_en.html'; TKS = R / 'talk_docs/keys_and_shelves_script_zh_en.html'
READ = R / 'github/README_draft_20261106b.md'
FILES = [REP, DECK, FP, ADV, PROC, ADD, AUD, TPR, T13, TKS, READ]
def bkp(p, tag='before_20261107b'):
    if p == REP: tag = 'before_20261107c'
    b = p.with_name(p.stem + '.' + tag + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b
S = {p: bkp(p).read_text(encoding='utf-8') for p in FILES}
NJ = json.loads(bkp(NOTES).read_text(encoding='utf-8'))
LOG = []
def rep(p, a, b, n=1, why=''):
    if p == 'NOTES':
        c = sum(v['text'].count(a) for v in NJ.values()); assert c == n, ('notes', c, a[:50])
        for v in NJ.values(): v['text'] = v['text'].replace(a, b)
    else:
        c = S[p].count(a); assert c == n, (p.name, c, a[:60]); S[p] = S[p].replace(a, b)
    LOG.append((why, str(p), a[:120], b[:160], n))
def resub(p, rx, fn, n, why):
    if p == 'NOTES':
        c = 0
        for v in NJ.values(): v['text'], k = re.subn(rx, fn, v['text'], flags=re.S); c += k
    else:
        S[p], c = re.subn(rx, fn, S[p], flags=re.S)
    assert c == n, (str(p)[-40:], c, why); LOG.append((why, str(p), rx[:80], '(regex)', c))

# ---------------- numbers for B, from the source
d = pd.read_csv(J / '381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv'); d = d[d.version == 'Vpd']
def first_pos(run):
    x = d[d.run == run].sort_values('layer')
    for L in x[x.tc_lo > 0].layer:
        if (x[x.layer >= L].tc_lo > 0).all(): return int(L), x.set_index('layer')
gL, gx = first_pos('given_first'); sL, sx = first_pos('surname_first'); ix = d[d.run == 'initial'].set_index('layer')
assert (gL, sL) == (16, 24) and ix.loc[40, 'tc_lo'] < 0 < ix.loc[40, 'tc_hi']
f3 = lambda v: f'{v:+.3f}'.replace('-', '−'); u3 = lambda v: f'{v:.3f}'.replace('-', '−')
s40 = f'+{sx.loc[40, "tc"]:.3f} [{u3(sx.loc[40, "tc_lo"])}, {u3(sx.loc[40, "tc_hi"])}]'
i40 = f'{f3(ix.loc[40, "tc"])} [{f3(ix.loc[40, "tc_lo"])}, {f3(ix.loc[40, "tc_hi"])}]'
assert s40 == '+0.030 [0.013, 0.048]' and i40 == '+0.014 [−0.002, +0.030]', (s40, i40)
BZ = (f'按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L{gL} 起、姓从 L{sL} 起 target−control 为正（姓 L40 {s40}）；首字母不显著（L40 {i40}）。'
      '只用 false_0、样本较小时姓在 L56 前不显著，此前的说法已被取代。')
BE = (f'With per-donor exclusion and the mean of five false titles, target − control is positive from L{gL} for the given-name first token and from L{sL} for the surname '
      f'(surname L40 {s40}); the initial is not significant (L40 {i40}). With false_0 only (fewer papers) the surname is not significant before L56; the earlier statement is superseded.')
TAGZ = (f'381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv，version=Vpd，列 tc / tc_lo / tc_hi（引用档内 target−control，团队聚类 bootstrap 2,000 次 95% CI）：'
        f'given_first L{gL} {f3(gx.loc[gL, "tc"])} [{f3(gx.loc[gL, "tc_lo"])}, {f3(gx.loc[gL, "tc_hi"])}] 起各层都 > 0；surname_first L{sL} {f3(sx.loc[sL, "tc"])} [{f3(sx.loc[sL, "tc_lo"])}, {f3(sx.loc[sL, "tc_hi"])}] 起各层都 > 0；'
        f'initial L40 {i40}；false_0 版本（V0，1,395 篇）姓 L16–L52 CI 含 0；b1_e4b5_report.md “Per-donor exclusion” 节 target − control 表')
TAGS = 'b1_e4b5_report.md，per-donor target − control；summary_b1_e4b5/perdonor_by_run_layer.csv Vpd'
json.dump({'BZ': BZ, 'BE': BE, 'TAGZ': TAGZ}, open(Path(__file__).parent / 'B_text_20261107.json', 'w'), ensure_ascii=False, indent=1)

# ---------------- D
rep(REP, 'recovers 0.825 at L48 and 100% from L52', 'recovers 0.825 at L48 and 99.6% from L52', why='D report §1 en')
rep(DECK, '80–87% at L48, 100% from L52', '80–87% at L48, 99.6% from L52', why='D deck slide 50')
rep(TKS, 'L48 恢复 0.83，', 'L48 恢复 0.82，', why='D keys & shelves zh')
rep(TKS, 'recovers 0.83 at L48', 'recovers 0.82 at L48', why='D keys & shelves en')

# ---------------- B
OLD_MAIN = r'这一差别主要来自首字母和名（L24–L32 起为正，\+0\.02 到 \+0\.09(?:<span class="src">(?:(?!</span>).)*</span>|〔[^〕]*〕)?）；'
WA = r'按逐个假标题排除、5 个假标题平均，姓的第一个 token 的 target − control 从 L24 起为正.*?前不显著(?P<p1>。?)(?P<tag><span class="src">（[^<]*）</span>|<span class="src">[^<]*</span>|<span style="[^"]*">（[^<]*）</span>|【[^】]*】|〔[^〕]*〕)?(?P<p2>。?)'
def wa_sub(style):
    def f(m):
        t = m.group('tag') or ''
        if style == 'html_src': new = '<span class="src">（' + TAGZ + '）</span>'
        elif style == 'hb_src': new = '<span class="src">' + TAGZ + '</span>'
        elif style == 'inline': new = '<span style="color:#8a8f98;font-size:.8em">（' + TAGZ + '）</span>'
        elif style == 'md': new = '【' + TAGZ + '】'
        elif style == 'note': new = '〔' + TAGZ + '〕'
        elif style == 'short': new = '<span class="src">（' + TAGS + '）</span>'
        return BZ[:-1] + new + '。' if style != 'hb_src' else BZ + new
    return f
resub(REP, OLD_MAIN, '', 1, 'B delete 主要来自首字母和名 (report)')
resub(FP, r'这一差别主要来自首字母和名（L24–L32 起为正，\+0\.02 到 \+0\.09）；', '', 1, 'B delete (handbook F)')
resub('NOTES', OLD_MAIN, '', 1, 'B delete (notes 72)')
resub(REP, WA, wa_sub('html_src'), 3, 'B new sentence (report ×3: #alltok-results text, box, #pd-b1-e4b5)')
resub(FP, WA, wa_sub('hb_src'), 1, 'B new sentence (handbook F)')
resub('NOTES', WA, wa_sub('note'), 1, 'B new sentence (notes)')
for p in (ADV, ADD, AUD): resub(p, WA, wa_sub('inline'), 1, 'B new sentence (update box)')
resub(PROC, WA, wa_sub('md'), 1, 'B new sentence (process report)')
for p in (TPR, T13): resub(p, WA, wa_sub('short'), 1, 'B new sentence (talk doc)')
EN_OLD = 'surname target − control positive from L24 (L40 +0.030, L56 +0.058)'
EN_NEW = (f'target − control positive from L{gL} for the given-name first token and from L{sL} for the surname (L40 {s40}); initial not significant (L40 {i40}); '
          'with false_0 only the surname is not significant before L56 (earlier statement superseded)')
rep(T13, EN_OLD, EN_NEW, why='B en (Stage 13 script)'); rep(READ, EN_OLD, EN_NEW, why='B en (README b)')
# deck slide 72 bullet (the pptx gets the same text from deck_v20b_new_20261107.py)
OLDB = ('<li><b>Target − control: </b>mainly initials and given names (positive from L24–L32); surname first token, five false titles with per-donor exclusion: positive from L24 (L40 +0.030, L56 +0.058)'
        '<span class="src">(within bin; b1_e4b5_report.md, per-donor)</span>; with false_0 only (fewer papers) not significant before L56</li>')
NEWB = (f'<li><b>Target − control (five false titles, per-donor exclusion): </b>given-name first token positive from L{gL}, surname from L{sL} (L40 {s40}); initial not significant (L40 {i40}); '
        'with false_0 only the surname is not significant before L56 — earlier statement superseded<span class="src">(within bin; b1_e4b5_report.md, per-donor)</span></li>')
rep(DECK, OLDB, NEWB, why='B deck slide 72')

# ---------------- F2-F4 hypothesis table (report table + handbook F summary + deck slide 65)
V = pd.read_csv(J / '381_stage13/summary_b1_xall/x2_verdict_new__all.csv').iloc[0]
Vo = pd.read_csv(J / '381_stage13/summary_b1_xall/x2_verdict_old__all.csv').iloc[0]
r2 = pd.read_csv(J / '381_stage13/summary_b1_xall/fit_authall_sanity.csv')
share = V.auth_R_S / V.auth_R_full; r2max = r2.filter(like='r2').max().max() if r2.filter(like='r2').shape[1] else None
assert abs(V.auth_R_S - 0.032) < 0.0005 and abs(Vo.auth_R_S - 0.016) < 0.0005 and 0.065 < share < 0.075, (V.auth_R_S, share)
print('X2 all-author R_auth', V.auth_R_S, 'old', Vo.auth_R_S, 'R_full', V.auth_R_full, 'share', share, 'r2 cols max', r2max)
H3Z_OLD = 'X2 按规则通过但子空间无解码能力，证据仍不足'
H3Z_NEW = 'X2 按规则通过，但作者子空间几乎解码不出作者（留出 R² ≤ 0.009；用全部作者重新拟合后搬动 0.032，约为完整替换的 7%），证据仍不足'
rep(REP, H3Z_OLD, H3Z_NEW, why='F2/F3 report table H3 cell')
rep(FP, H3Z_OLD, H3Z_NEW, why='F2/F3 handbook F H3 summary')
rep(REP, '<th>目前结果（2026-11-05）</th>', '<th>目前结果（第 29 版，2026-11-07）</th>', why='F4 report table date')
rep(DECK, 'H3 passes by rule but the author subspace decodes nothing → still insufficient', 'H3 passes by rule but the author subspace can hardly decode authors (held-out R² ≤ 0.009) → still insufficient', why='F2 deck slide 65 subtitle')
rep(DECK, 'Hypotheses H1–H3 × readouts M1–M3 and current results (report v28, 2026-11-05)', 'Hypotheses H1–H3 × readouts M1–M3 and current results (report v29, 2026-11-07)', why='F4 deck slide 65 caption')

for p, s in S.items():
    assert not re.search('minyan', s, re.I), p
    if s != bkp(p).read_text(encoding='utf-8'): p.write_text(s, encoding='utf-8')
NOTES.write_text(json.dumps(NJ, ensure_ascii=False, indent=1))
json.dump(LOG, open(Path(__file__).parent / 'apply_log_20261107c.json', 'w'), ensure_ascii=False, indent=1)
for l in LOG: print(l[0], '|', Path(l[1]).name, '|', l[4])
