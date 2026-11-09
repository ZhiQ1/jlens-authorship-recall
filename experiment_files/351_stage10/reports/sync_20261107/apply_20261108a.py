"""Round e (user approved 2026-11-08; NO publishing). Reads the CURRENT files; backups *.before_20261108a.* are fresh copies of the current
state (asserted not to exist before), never used as input.
1 wording B -> version 3 (for_user_2026-11-07.md section f, verbatim; numbers re-read from summary_b1_e4b5/perdonor_by_run_layer.csv),
  zh + en, all 14 places; pre-registered item titles '减 5 个假标题(平均)' kept, first occurrence per document gets '（实际每篇可用假标题个数见正文）'.
2 version labels for addendum-9 numbers that had none (pre-registered V0, 1,395 papers).
3 RQ1 lower bound 0.109 -> 0.108 (c2_followup_proxy.csv aa_all int6 rq1_team_lo 0.108476).
Log: sync_20261107/apply_log_20261108a.json."""
import filecmp, json, re, shutil
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); R = J / '351_stage10/reports'
REP = R / 'stage1_11/stage1_11_report.html'; DECK = R / 'merged_deck/stage1_11_deck.html'; NOTES = R / 'talk/src/export/notes_zh.json'
PARTS = {p.name: p for p in sorted((R / 'methods/parts').glob('*.html')) if '.before_' not in p.name and p.name not in ('K_post_defence.html', 'F_stage13.orig.html')}
TD = {p.stem: p for p in (R / 'talk_docs').glob('*.html') if '.before_' not in p.name}
ADV = R / 'advisor/index.html'; PROC = R / 'process_report/draft_zh.md'; AUD = J / 'audit_20261105/scoring_audit.html'
ADD = R / 'pages_20261106b/methods_addendum/index.html'; READ = R / 'github/README_draft_20261106b.md'
FILES = [REP, DECK, *PARTS.values(), *TD.values(), ADV, PROC, AUD, ADD, READ]
for p in FILES + [NOTES]:
    b = p.with_name(p.stem + '.before_20261108a' + p.suffix)
    if b.exists(): assert filecmp.cmp(b, p, shallow=False), ('backup exists and differs from the current file', b)
    else: shutil.copy2(p, b)
S = {p: p.read_text(encoding='utf-8') for p in FILES}
NJ = json.loads(NOTES.read_text(encoding='utf-8'))
LOG = []
def rel(p): return 'notes_zh.json' if p == 'NOTES' else str(p).replace(str(R) + '/', '')
def R_(old, new, files=None, n_min=1, why='', regex=False):
    tot = 0
    for p in (files if files is not None else FILES + ['NOTES']):
        items = [(k, v) for k, v in NJ.items()] if p == 'NOTES' else [(None, None)]
        for k, v in items:
            t = v['text'] if p == 'NOTES' else S[p]
            c = len(re.findall(old, t, flags=re.S)) if regex else t.count(old)
            if not c: continue
            t2 = re.sub(old, new, t, flags=re.S) if regex else t.replace(old, new)
            if p == 'NOTES': v['text'] = t2
            else: S[p] = t2
            tot += c; LOG.append((why, rel(p) + (' #' + k if k else ''), ('(regex) ' if regex else '') + old, new if isinstance(new, str) else '(computed)', c))
    assert tot >= n_min, ('rule did not apply', why, old[:80]); return tot

# ---------------- numbers for wording B v3 (asserted against the source)
d = pd.read_csv(J / '381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv')
def v(ver, run, L):
    x = d[(d.version == ver) & (d.run == run) & (d.layer == L)].iloc[0]
    f = lambda z: f'{z:+.3f}'.replace('-', '−'); g = lambda z: (f'{z:.3f}' if z >= 0 else f'{z:+.3f}').replace('-', '−')
    lo, hi = x.tc_lo, x.tc_hi
    ci = f'[{g(lo)}, {g(hi)}]' if lo >= 0 else f'[{f(lo)}, {f(hi)}]'
    return f'{f(x.tc)} {ci}', int(x.n)
CHK = {('V0', 'given_first', 24): '+0.051 [0.007, 0.095]', ('V0', 'given_first', 40): '+0.049 [0.005, 0.095]', ('V0', 'given_first', 48): '+0.073 [0.027, 0.122]',
       ('V0', 'surname_first', 24): '−0.002 [−0.037, +0.036]', ('V0', 'surname_first', 40): '+0.012 [−0.026, +0.048]', ('V0', 'surname_first', 48): '+0.016 [−0.025, +0.056]',
       ('V0', 'initial', 24): '+0.033 [0.005, 0.059]', ('V0', 'initial', 40): '+0.031 [−0.001, +0.062]', ('V0', 'initial', 48): '+0.056 [0.025, 0.089]',
       ('Vpd', 'given_first', 24): '+0.037 [0.012, 0.062]', ('Vpd', 'given_first', 40): '+0.048 [0.021, 0.076]', ('Vpd', 'given_first', 48): '+0.051 [0.023, 0.081]',
       ('Vpd', 'surname_first', 24): '+0.019 [0.001, 0.038]', ('Vpd', 'surname_first', 40): '+0.030 [0.013, 0.048]', ('Vpd', 'surname_first', 48): '+0.042 [0.025, 0.060]',
       ('Vpd', 'initial', 24): '+0.026 [0.012, 0.040]', ('Vpd', 'initial', 40): '+0.014 [−0.002, +0.030]', ('Vpd', 'initial', 48): '+0.031 [0.014, 0.048]',
       ('V5x0', 'given_first', 40): '+0.047 [0.012, 0.081]', ('V5x0', 'surname_first', 40): '+0.024 [−0.006, +0.052]', ('V5x0', 'surname_first', 48): '+0.031 [0.001, 0.059]',
       ('V5x0', 'initial', 40): '+0.021 [−0.002, +0.043]'}
for (ver, run, L), want in CHK.items():
    got, _ = v(ver, run, L); assert got == want, (ver, run, L, got, want)
NN = {(ver, run): v(ver, run, 40)[1] for ver in ('V0', 'Vpd', 'V5x0') for run in ('given_first', 'surname_first', 'initial')}
assert (NN['V0', 'given_first'], NN['V0', 'surname_first'], NN['V0', 'initial']) == (1706, 1395, 1590)
assert (NN['Vpd', 'given_first'], NN['Vpd', 'surname_first'], NN['Vpd', 'initial']) == (3046, 4654, 4812)
fu = (Path('/home/zhang.zhiqi2/jlens_work/for_user_2026-11-07.md')).read_text(encoding='utf-8')
sec = fu[fu.index('## f. 措辞 B 第 3 版'):]
q = [l[2:].strip() for l in sec.splitlines() if l.startswith('> ')]
assert len(q) == 5 and q[0].startswith('标题位置 probe 的 target − control') and q[4].startswith('结论：'), q[:1]
for want in CHK.values():
    assert want in ' '.join(q), want              # every number of the user's text equals the CSV value
BZ = q[0] + ''.join(q[1:4]) + q[4]               # user's text, verbatim (①②③ + conclusion)
BE = ('Title-position probe target − control (within citation bin) has three versions: '
      '① pre-registered (false_0 only; false_0 is the only false title checked for title reuse, a clean single control; given name 1,706, surname 1,395, initial 1,590 papers): '
      'given-name first token L24 +0.051 [0.007, 0.095], L40 +0.049 [0.005, 0.095], L48 +0.073 [0.027, 0.122]; surname L24 −0.002 [−0.037, +0.036], L40 +0.012 [−0.026, +0.048], L48 +0.016 [−0.025, +0.056]; '
      'initial L24 +0.033 [0.005, 0.059], L40 +0.031 [−0.001, +0.062], L48 +0.056 [0.025, 0.089] (identical to the published addendum-9 values, e4b_alltok.md). '
      '② per-donor exclusion (post-hoc deviation D1; about 1.5 usable false titles per paper; given name 3,046, surname 4,654, initial 4,812 papers): '
      'given name L24 +0.037 [0.012, 0.062], L40 +0.048 [0.021, 0.076], L48 +0.051 [0.023, 0.081]; surname L24 +0.019 [0.001, 0.038], L40 +0.030 [0.013, 0.048], L48 +0.042 [0.025, 0.060]; '
      'initial L24 +0.026 [0.012, 0.040], L40 +0.014 [−0.002, +0.030], L48 +0.031 [0.014, 0.048]. '
      '③ "mean of 5 false titles" (sensitivity reference only: same papers as ①, excluded by false_0 only; about 79% of false_1..4 should have been excluded, so it contains leakage; given name 1,706, surname 1,395, initial 1,590 papers): '
      'given name L40 +0.047 [0.012, 0.081]; surname L40 +0.024 [−0.006, +0.052], L48 +0.031 [0.001, 0.059]; initial L40 +0.021 [−0.002, +0.043]. '
      'Conclusion: in the pre-registered version the given-name first token is positive at L24–L48 and the surname is not significant at L24–L48 (L40 +0.012 [−0.026, +0.048]); '
      'in the post-hoc per-donor version the surname is positive from L24 (L40 +0.030 [0.013, 0.048]). The given-name signal is consistent across the three versions; '
      'the surname evidence is weak and comes only from the post-hoc version. The initial is positive at some layers with an inconsistent pattern (no multi-layer correction); no conclusion is drawn.')
TAGZ = '381_stage13/summary_b1_e4b5/perdonor_by_run_layer.csv（version = V0 / Vpd / V5x0，列 tc / tc_lo / tc_hi；引用档内 target − control，团队整群 bootstrap 2,000 次 95% CI）；381_stage13/reports/e4b_alltok.md；b1_e4b5_report.md'
TAGE = 'summary_b1_e4b5/perdonor_by_run_layer.csv, versions V0 / Vpd / V5x0, columns tc / tc_lo / tc_hi; within-bin target − control, team-cluster bootstrap 2,000, 95% CI; e4b_alltok.md; b1_e4b5_report.md'
json.dump({'BZ': BZ, 'BE': BE}, open(R / 'sync_20261107/B_text_v3_20261108.json', 'w'), ensure_ascii=False, indent=1)

# ---------------- 1 wording B v3 (zh) — old sentence + its tag, in each tag style
OLDB = r'(?:认得出的论文在标题位置携带更多名字信息，)?按逐个假标题排除、5 个假标题平均，名的第一个 token 从 L16 起、姓从 L24 起 target−control 为正（姓 L40 \+0\.030 \[0\.013, 0\.048\]）；首字母不显著（L40 \+0\.014 \[−0\.002, \+0\.030\]）。只用 false_0、样本较小时姓在 L56 前不显著，此前的说法已被取代'
def newb(style):
    tag = {'src': f'<span class="src">（{TAGZ}）</span>', 'hb': f'<span class="src">{TAGZ}</span>', 'inline': f'<span style="color:#8a8f98;font-size:.8em">（{TAGZ}）</span>',
           'md': f'【{TAGZ}】', 'note': f'〔{TAGZ}〕'}[style]
    return lambda m: BZ[:-1] + tag + '。' if style != 'hb' else BZ + tag
TAILS = {'src': r'<span class="src">（[^<]*）</span>', 'hb': r'。<span class="src">[^<]*</span>', 'inline': r'<span style="[^"]*">（[^<]*）</span>', 'md': r'【[^】]*】', 'note': r'〔[^〕]*〕'}
R_(OLDB + TAILS['src'] + '。?', newb('src'), files=[REP], n_min=3, regex=True, why='1 wording B v3 (report ×3)')
R_(OLDB + TAILS['src'] + '。?', newb('src'), files=[TD['progress_report_for_advisor_zh'], TD['stage13_script_zh_en']], n_min=2, regex=True, why='1 wording B v3 (talk docs)')
R_(OLDB + TAILS['hb'], newb('hb'), files=[PARTS['F_stage13.html']], regex=True, why='1 wording B v3 (handbook F)')
R_(OLDB + TAILS['inline'] + '。?', newb('inline'), files=[ADV, AUD, ADD], n_min=3, regex=True, why='1 wording B v3 (update boxes)')
R_(OLDB + TAILS['md'] + '。?', newb('md'), files=[PROC], regex=True, why='1 wording B v3 (process report)')
R_(OLDB + TAILS['note'] + '。?', newb('note'), files=['NOTES'], regex=True, why='1 wording B v3 (deck note 72)')
# en
OLDE = ('target − control positive from L16 for the given-name first token and from L24 for the surname (L40 +0.030 [0.013, 0.048]); initial not significant (L40 +0.014 [−0.002, +0.030]); '
        'with false_0 only the surname is not significant before L56 (earlier statement superseded)')
R_(OLDE, BE[:-1], files=[READ, TD['stage13_script_zh_en']], n_min=2, why='1 wording B v3 (en: README b, Stage 13 script)')
OLDD = ('<li><b>Target − control (five false titles, per-donor exclusion): </b>given-name first token positive from L16, surname from L24 (L40 +0.030 [0.013, 0.048]); initial not significant (L40 +0.014 [−0.002, +0.030]); '
        'with false_0 only the surname is not significant before L56 — earlier statement superseded<span class="src">(within bin; b1_e4b5_report.md, per-donor)</span></li>')
DECKB = ('<li><b>Target − control, three versions: </b>pre-registered (false_0; 1,706 / 1,395 papers): given name + at L24–L48, surname n.s. (L40 +0.012 [−0.026, +0.048]); '
         'per-donor (post hoc, D1; 4,654 papers): surname + from L24 (L40 +0.030 [0.013, 0.048]); 5-title mean (leaky, sensitivity only): surname L40 +0.024 [−0.006, +0.052] → given name consistent, surname evidence weak (post hoc only)'
         '<span class="src">(within bin; perdonor_by_run_layer.csv V0 / Vpd / V5x0)</span></li>')
R_(OLDD, DECKB, files=[DECK], why='1 wording B v3 (deck slide 72, compact en; full text in note 72)')
# item titles: first occurrence per document gets the note
NOTE_ZH = '（实际每篇可用假标题个数见正文）'
for p in [REP, ADV, PROC, AUD, ADD, TD['progress_report_for_advisor_zh'], PARTS['B_global2.html']]:
    m = re.search(r'减 5 个假标题(?:平均)?', S[p])
    if m and not S[p][m.end():m.end() + len(NOTE_ZH)] == NOTE_ZH:
        S[p] = S[p][:m.end()] + NOTE_ZH + S[p][m.end():]; LOG.append(('1 item-title note (first occurrence)', rel(p), m.group(0), m.group(0) + NOTE_ZH, 1))
for p in [READ]:
    m = re.search(r'minus five false titles', S[p])
    if m: S[p] = S[p][:m.end()] + ' (actual usable false titles per paper: see text)' + S[p][m.end():]; LOG.append(('1 item-title note (first occurrence, en)', rel(p), m.group(0), '+ (actual usable false titles per paper: see text)', 1))

# ---------------- 2 version labels for addendum-9 (V0) numbers without one
R_('（目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md）', '（预注册版 V0：只减 false_0，目标 + 对照 1,395 篇，剔除标题复用，团队聚类 95% CI；381_stage13/reports/e4b_alltok.md）', n_min=5, why='2 V0 label (addendum-9 sentence)')
R_('(1,395 papers; e4b_alltok.md)', '(pre-registered V0: false_0 only, 1,395 papers; e4b_alltok.md)', n_min=2, why='2 V0 label (en)')
R_('surname first token L40 +0.071 [0.058, 0.085] |', 'surname first token L40 +0.071 [0.058, 0.085] (pre-registered V0, false_0 only, 1,395 papers) |', files=[READ], why='2 V0 label (README table)')
R_('Addendum 9 shows surname_first L40 +0.071 and given_first +0.124', 'Addendum 9 (pre-registered version V0, false_0 only; 1,395 / 1,706 papers) shows surname_first L40 +0.071 and given_first +0.124', files=[AUD], why='2 V0 label (audit)')

# ---------------- 3 RQ1 lower bound
px = pd.read_csv(J / '381_stage13/c13_C2_followup/c2_followup_proxy.csv'); lo = px[(px.version == 'aa_all') & (px.endpoint == 'int6')].rq1_team_lo.iloc[0]
assert f'{lo:.3f}' == '0.108', lo
R_('+0.130 [0.109, 0.153]', '+0.130 [0.108, 0.153]', n_min=4, why='3 RQ1 lower bound (report #p1-s8, deck slide 19 + note, handbook #s19-s8d)')

for p, s in S.items():
    assert not re.search('minyan', s, re.I), p
    p.write_text(s, encoding='utf-8')
NOTES.write_text(json.dumps(NJ, ensure_ascii=False, indent=1))
json.dump(LOG, open(R / 'sync_20261107/apply_log_20261108a.json', 'w'), ensure_ascii=False, indent=1)
for l in LOG: print(l[0], '|', l[1], '|', l[4])
