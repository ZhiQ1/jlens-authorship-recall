
# ================= v22t run part (appended to build22t_head.py by make_build.sh) =================
O67 = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/order_v67.json'))
RM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map.json')); V2V = {int(a): b for a, b in RM['v66_to_v67'].items()}
R68 = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map_v68.json'))
P67_68 = {int(a): b for a, b in R68['v67_to_v68'].items()}; NEW68 = set(R68['new'].values())
N68 = len(P67_68) + len(NEW68)
P68_67 = {b: a for a, b in P67_68.items()}
O68 = []                      # per v68 page: ('old', v66 page) | ('new', v68 page)
for pos in range(1, N68 + 1):
    if pos in NEW68: O68.append(('new', pos)); continue
    e = O67[P68_67[pos] - 1]
    O68.append(('old', e[1]) if e[0] == 'old' else ('new', pos))
# ---- v22s slide -> v66 page (from the build notes); pptx-only / continuation slides follow the slide before them
S2H = {}
for i, s in enumerate(SL, 1):
    n = s.notes_slide.notes_text_frame.text if s.has_notes_slide else ''
    pg = re.findall(r'HTML deck v6\d page (\d+)', n)
    if pg: S2H[i] = int(pg[0])
GROUP = {}                    # v66 page -> [v22s slides]
cur = None
for i in range(1, NS + 1):
    if i in S2H and (cur is None or S2H[i] != cur or not GROUP.get(cur)):
        cur = S2H[i]
    GROUP.setdefault(cur, []).append(i)
assert sorted(sum(GROUP.values(), [])) == list(range(1, NS + 1))
# ---- the v22t order
order = []                    # ('q', v22s slide) | ('h', v67 page)
for pos, e in enumerate(O68, 1):
    if e[0] == 'old':
        for k in GROUP[e[1]]: order.append(('q', k))
    else:
        order.append(('h', pos))
assert len([e for e in order if e[0] == 'q']) == NS
POS = {e: i + 1 for i, e in enumerate(order)}
QPOS = {k: POS[('q', k)] for k in range(1, NS + 1)}
for pos, e in enumerate(O68, 1):
    H67[pos] = POS[('h', pos)] if e[0] == 'new' else QPOS[GROUP[e[1]][0]]
def q2t(n): return QPOS.get(n, n)

# ---- mechanism-map pages: the map goes in as one picture (Chromium screenshot of the HTML map), other items native
MAPD = W9 + 'maps68b/'
MAPS = {int(a): b for a, b in json.load(open(MAPD + 'maps.json')).items()} if os.path.exists(MAPD + 'maps.json') else {}
_load0 = load
def load(h, mode):
    d = _load0(h, mode)
    if d is None or mode != 'full' or h not in MAPS: return d
    b = MAPS[h]
    def inside(x, y): return b['x'] - 2 <= x <= b['x'] + b['w'] + 2 and b['y'] - 2 <= y <= b['y'] + b['h'] + 2
    def ctr(it):
        if it['k'] == 'poly': xs = [q[0] for q in it['pts']]; ys = [q[1] for q in it['pts']]; return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        return it['x'] + it.get('w', 0) / 2, it['y'] + it.get('h', 0) / 2
    KEEP = ('askl', 'soln', 'covna', 'covso', 'covtg', 'lead')
    def keep(it):
        c = (it.get('cls') or '').split()
        if any(k in c for k in KEEP): return True
        t0 = ''.join(r.get('t', '') for r in it.get('runs') or []).lstrip()
        return t0.startswith('Now asking') or t0.startswith('So (')
    SVGTXT = ('Read early, said late: where each step happens', 'x: the prompt as Qwen3 tokens', 'Step 1:')
    LEG = {'settled', 'locked', 'fairly solid', 'descriptive', 'exploratory', 'pending'}
    def clipped(it):          # map-svg text that falls outside the svg viewport: clipped (invisible) in the HTML page
        if it['k'] != 'text' or it['x'] > b['x'] + b['w'] or it['x'] + it['w'] < b['x']: return False
        if not (b['y'] - 70 <= it['y'] <= b['y'] + b['h'] + 40): return False
        t0 = ''.join(r.get('t', '') for r in it.get('runs') or []).strip()
        return t0.startswith(SVGTXT) or (t0 in LEG and it['h'] <= 14)
    d = dict(d); d['items'] = [it for it in d['items'] if keep(it) or not (inside(*ctr(it)) or clipped(it))]
    d['maths'] = [m if not inside(m[0] + m[2] / 2, m[1] + m[3] / 2) else [m[0], m[1], m[2], m[3], False] for m in d['maths']]
    return d
# ---- new native slides
NEW = {}
for e in order:
    if e[0] != 'h': continue
    ns = prs.slides.add_slide(BGREF.slide_layout)
    for ph in list(ns.placeholders): ph._element.getparent().remove(ph._element)
    nb_ = bg_and_number(ns); full_page(ns, e[1]); NEW[e[1]] = ns
    if e[1] in MAPS:
        b = MAPS[e[1]]; d0 = _load0(e[1], 'full'); top, bot = b['y'], b['y'] + b['h']
        for it in d0['items']:
            if it['k'] != 'text' or it['x'] > b['x'] + b['w'] or it['x'] + it['w'] < b['x']: continue
            t0 = ''.join(r.get('t', '') for r in it.get('runs') or []).lstrip()
            if not (t0.startswith('Now asking') or t0.startswith('So (') or any(k in (it.get('cls') or '').split() for k in ('askl', 'soln', 'covna', 'covso'))): continue
            ib = it['y'] + it['h']
            if it['y'] < b['y'] + b['h'] / 2 and ib > b['y'] - 2: top = max(top, ib + 4)        # text just above, reaching into the map
            if it['y'] >= b['y'] + b['h'] / 2 and it['y'] < b['y'] + b['h'] + 2: bot = min(bot, it['y'] - 4)   # text just below
        sc = min(1.0, (bot - top) / b['h']); w2, h2 = b['w'] * sc, b['h'] * sc
        add_pic(ns, MAPD + 'map_%03d.png' % e[1], b['x'] + (b['w'] - w2) / 2, top, w2, h2); LOG.setdefault('map_pics', []).append([e[1], round(sc, 3)])
    el_ = nb_._element; el_.getparent().remove(el_); ns.shapes._spTree.append(el_)
    ns.notes_slide.notes_text_frame.text = PFX + 'Native page built from HTML deck v68 page %d.' % e[1]

# ---- coverage lines (Now asking / So / evidence tag) added in v67: mirror where the pptx slide lacks them
def slide_text(s): return ' '.join(x.text_frame.text for x in s.shapes if x.has_text_frame)
def has_feat(s, feat):
    t = slide_text(s)
    if feat == 'covna': return 'Now asking' in t
    if feat == 'covso': return re.search(r'(^|\s)So\b\s*(\((section|this slide)\))?\s*[:：]', t) is not None
    if feat == 'covtg': return re.search(r'\b(settled|locked|descriptive|exploratory|supported|not supported|caveat|marginal)\b', t, re.I) is not None and ('Evidence' in t or re.search(r'locked ·|settled|exploratory|descriptive', t) is not None)
COVK = ('covna', 'covso', 'covtg')
PLACED = {}
for pos, e in enumerate(O68, 1):
    if e[0] != 'old': continue
    d = load(pos, 'full')
    if d is None: continue
    ks = GROUP[e[1]]; k = ks[0]; s = SL[k - 1]
    feats = {}
    for it in d['items']:
        c = (it.get('cls') or '')
        f = next((x for x in COVK if x in c.split()), None)
        if f: feats.setdefault(f, []).append(it)
    if not feats: continue
    occ = None; placed = None
    for f, its in feats.items():
        # several slides in the group (continuations): any of them already having it counts
        if any(has_feat(SL[j - 1], f) for j in ks):
            LOG['cov_skip'].append([k, f, 'already on the slide']); continue
        if occ is None:
            occ = ink_map(k); placed = np.zeros_like(occ)
        xs = [it['x'] for it in its]; ys = [it['y'] for it in its]
        bx, by = min(xs), min(ys); bw = max(it['x'] + it['w'] for it in its) - bx; bh = max(it['y'] + it['h'] for it in its) - by
        spot = None
        for sc in (1.0, 0.9, 0.8):
            spot = find_spot(occ, placed, bx, by, bw * sc, bh * sc)
            if spot: break
        if not spot:
            LOG['not_fitted'].append([k, f, ' '.join(''.join(r['t'] for r in t['runs']) for t in its if t['k'] == 'text')[:200]]); continue
        dx, dy = spot[0] - bx, spot[1] - by
        for it in its: write_item(s, it, pos, dx, dy, sc, bx, by)
        placed[int(spot[1] // 4):int((spot[1] + bh * sc) // 4) + 1, int(spot[0] // 4):int((spot[0] + bw * sc) // 4) + 1] = True
        LOG['cov'].append([k, f, round(spot[0]), round(spot[1]), sc]); PLACED[k] = placed
        LOG['notes'].setdefault(k, []).append('Coverage line from HTML deck v68 page %d added (%s), placed in free space.' % (pos, {'covna': 'Now asking', 'covso': 'So', 'covtg': 'evidence tag'}[f]))

# ---- 'slide N' in our own original shapes: v22s -> v22t; stale lead arrows reworded (as in HTML v67)
def our_runs(k):
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if sh.shape_id in ups or CJK.search(sh.text_frame.text if sh.has_text_frame else ''): continue
        frames = []
        if sh.has_text_frame and sh.shape_id in ORIG[k]: frames.append(sh.text_frame)
        if getattr(sh, 'has_table', False) and sh.has_table and sh.shape_id in ORIG[k]:
            frames += [c.text_frame for row in sh.table.rows for c in row.cells]
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs: yield sh, r
for k in range(1, NS + 1):
    me = QPOS[k]; ch = set()
    for sh, r in our_runs(k):
        new = remap(r.text, q2t)
        def lead(m, arrow):
            n = int(m.group(2)); adj = me - 1 if arrow == '←' else me + 1
            if n == adj: return m.group(0)
            LOG['leads'].append([k, me, m.group(0), n]); return ('See slide ' if arrow == '←' else 'see slide ') + m.group(2)
        new2 = re.sub(r'(←\s*[Ss]lide )(\d+)', lambda m: lead(m, '←'), new)
        new2 = re.sub(r'(→\s*[Ss]lide )(\d+)', lambda m: lead(m, '→'), new2)
        if new2 != r.text: r.text = new2; ch.add(sh.shape_id)
    for sid in ch: LOG['edited'].append([k, sid])
# user shapes / Chinese boxes with 'slide N' references: listed, not edited
for k in range(1, NS + 1):
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if not sh.has_text_frame: continue
        if sh.shape_id in ups or CJK.search(sh.text_frame.text):
            for m in REF.finditer(sh.text_frame.text):
                nums = [int(x) for x in re.findall(r'\d+', m.group(2))]
                if any(q2t(n) != n for n in nums):
                    LOG['stale_user_refs'].append([QPOS[k], sh.shape_id, m.group(0), [q2t(n) for n in nums]])



# ---- plain names for internal codes in OUR original shapes (codes table on HTML v68 Glossary slide 149); user shapes / Chinese boxes untouched
PLAIN68 = [(r'\bM1–M3\b', 'the three predictions'), (r'\(M1–M3\)', '(three predictions)'),
           (r'\bM1\b', 'top lens word'), (r'\bM2\b', 'attribute probe'), (r'\bM3\b', 'change-the-question test'), (r'\bM4\b', 'author-specific lens'),
           (r'\b(Stage )?8D[–-]8E\b', 'Stage 8 replication and follow-up audit'), (r'\b(Stage )?8D\b', 'Stage 8 replication (200 new papers)'),
           (r'\b(Stage )?8E\b', 'Stage 8 follow-up audit (not pre-registered)'),
           (r'\bRQ1\b', 'title test'), (r'\bRQ2\b', 'A−B test'), (r'\bRQ3\b', 'low−high test'),
           (r'\bJMRR\b', 'mean reciprocal rank of the name tokens'),
           (r'\bLine A\b', '“Is it about this paper?”'), (r'\bLine B\b', '“What can each readout see?”'),
           (r'\bLine C\b', '“When does it appear and when is it used?”'), (r'\bLine D\b', '“Which token carries it?”')]
def plain68(s):
    for a, b in PLAIN68: s = re.sub(a, b, s)
    return s
LOG['plain68'] = []
for k in range(1, NS + 1):
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if sh.shape_id in ups or sh.shape_id not in ORIG[k]: continue
        frames = []
        if sh.has_text_frame:
            if CJK.search(sh.text_frame.text): continue
            frames.append(sh.text_frame)
        elif getattr(sh, 'has_table', False) and sh.has_table:
            frames += [c.text_frame for row in sh.table.rows for c in row.cells]
        ch = False
        for tf in frames:
            for p in tf.paragraphs:
                full = ''.join(r.text for r in p.runs); new = plain68(full)
                if new == full: continue
                for r in p.runs:
                    nr = plain68(r.text)
                    if nr != r.text: r.text = nr; ch = True
                if ''.join(r.text for r in p.runs) != new and p.runs:
                    p.runs[0].text = new
                    for r in p.runs[1:]: r.text = ''
                    ch = True
        if ch:
            LOG['edited'].append([k, sh.shape_id]); LOG['plain68'].append([k, sh.shape_id])
            LOG['notes'].setdefault(k, []).append('Internal codes in our text replaced by plain names (Glossary codes table).')


def note_col(k):
    a = np.asarray(Image.open(D + 'render/v22s/r13/p%02d.png' % k).convert('L'))
    return RGBColor(0xA9, 0xCB, 0xEE) if np.median(a) < 110 else RGBColor(0x3C, 0x78, 0xB4)
# ---- rule 13 extended (user 2026-11-23): small "code → plain name" notes beside the user's shapes; shapes untouched
CODEMAP = [(r'\bLine A\b', 'Line A', 'Is it about this paper?'), (r'\bLine B\b', 'Line B', 'What can each readout see?'),
           (r'\bLine C\b', 'Line C', 'When does it appear and when is it used?'), (r'\bLine D\b', 'Line D', 'Which token carries it?'),
           (r'\bJMRR\b', 'JMRR', 'mean reciprocal rank of the name tokens'), (r'\b8D\b', '8D', 'Stage 8 replication (200 new papers)'),
           (r'\bM3\b', 'M3', 'change-the-question test'), (r'\b8E\b', '8E', 'Stage 8 follow-up audit (not pre-registered)')]   # 8E approved by the user 2026-11-23
LOG['code_notes'] = []
for k in range(1, NS + 1):
    s = SL[k - 1]; ups = user_ids(s); occ = None; placed = None
    for sh in list(s.shapes):
        if sh.shape_id not in ups or not sh.has_text_frame or sh.shape_id not in ORIG[k]: continue
        txt = sh.text_frame.text
        found = [(c, pl) for pat, c, pl in CODEMAP if re.search(pat, txt)]
        if not found: continue
        have = slide_text(s)
        found = [(c, pl) for c, pl in found if (c + ' → ' + pl) not in have]
        if not found: continue
        if occ is None: occ = ink_map(k); placed = PLACED.get(k, np.zeros_like(occ)); PLACED[k] = placed
        note = ' · '.join(c + ' → ' + pl for c, pl in found)
        w = min(560, 7.2 * len(note) + 12); hgt = 16
        x0 = sh.left / K; y0 = (sh.top + sh.height) / K + 2
        spot = find_spot(occ, placed, min(max(8, x0), 1272 - w), min(max(8, y0), 700), w, hgt) or find_spot(occ, placed, 8, 690, w, hgt)
        if not spot: LOG['not_fitted'].append([k, 'code note', note]); continue
        tb = s.shapes.add_textbox(E(spot[0]), E(spot[1]), E(w), E(hgt)); tf = tb.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.word_wrap = True
        r = tf.paragraphs[0].add_run(); r.text = note; r.font.size = Pt(10.5 * PT); r.font.name = 'Noto Sans SC'; r.font.color.rgb = note_col(k)
        placed[int(spot[1] // 4):int((spot[1] + hgt) // 4) + 1, int(spot[0] // 4):int((spot[0] + w) // 4) + 1] = True
        LOG['code_notes'].append([k, sh.shape_id, note])
        LOG['notes'].setdefault(k, []).append('Plain-name note added beside your shape #%d (rule 13 extended): %s' % (sh.shape_id, note))


# codes printed inside the user's chart pictures (HTML v68 slides 64 and 112 = v22s S19, S59): note beside the picture, picture untouched
IMGNOTES = {19: (956, [('RQ1', 'title test'), ('RQ2', 'A−B test'), ('RQ3', 'low−high test'), ('Stage 8D', 'Stage 8 replication (200 new papers)')]),
            59: (3562, [('JMRR', 'mean reciprocal rank of the name tokens')])}
for k, (pid, pairs) in IMGNOTES.items():
    s = SL[k - 1]; have = slide_text(s)
    pairs = [(c, pl) for c, pl in pairs if (c + ' → ' + pl) not in have]
    if not pairs: continue
    pic = next(x for x in s.shapes if x.shape_id == pid)
    occ = ink_map(k); placed = PLACED.get(k, np.zeros_like(occ)); PLACED[k] = placed
    note = 'In the chart: ' + ' · '.join(c + ' → ' + pl for c, pl in pairs)
    w = min(760, 6.6 * len(note) + 12); hgt = 16
    y0 = (pic.top + pic.height) / K + 2 if pic.height < 0.9 * SH else 640
    spot = find_spot(occ, placed, 80, min(y0, 700), w, hgt) or find_spot(occ, placed, 8, 690, w, hgt)
    if not spot: LOG['not_fitted'].append([k, 'image code note', note]); continue
    tb = s.shapes.add_textbox(E(spot[0]), E(spot[1]), E(w), E(hgt)); tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = note; r.font.size = Pt(10.5 * PT); r.font.name = 'Noto Sans SC'; r.font.color.rgb = note_col(k)
    LOG['code_notes'].append([k, pid, note]); LOG['notes'].setdefault(k, []).append('Plain-name note added beside your chart picture #%d (rule 13 extended): %s' % (pid, note))

for k, segs in LOG['notes'].items():
    tf = SL[k - 1].notes_slide.notes_text_frame
    for z in dict.fromkeys(segs): tf.add_paragraph().add_run().text = PFX + z
# ---- order
lst = prs.slides._sldIdLst; els = list(lst); idx = {s.slide_id: e for s, e in zip(prs.slides, els)}
SIDQ = {k: SL[k - 1].slide_id for k in range(1, NS + 1)}; SIDH = {h: s.slide_id for h, s in NEW.items()}
for e in els: lst.remove(e)
for t, v in order: lst.append(idx[SIDQ[v] if t == 'q' else SIDH[v]])
FINAL = list(prs.slides); NEWIDS = set(SIDH.values())
for i, s in enumerate(FINAL, 1):
    if s.slide_id not in NEWIDS: continue
    for f in s._element.iter('{%s}fld' % AN):
        if f.get('type') == 'slidenum':
            t = f.find('{%s}t' % AN)
            if t is not None: t.text = str(i)
for k in range(1, NS + 1):
    nid = max(ORIG[k]) + 3000
    for x in SL[k - 1].shapes:
        if any(x._element is b for b in ORIG_EL[k]): continue
        x._element.xpath('./*[1]/p:cNvPr')[0].set('id', str(nid)); nid += 1
prs.save(OUT)
ADDED = [[k, sid] for k in range(1, NS + 1) for sid in [x.shape_id for x in SL[k - 1].shapes] if sid not in ORIG[k]]
ordr = [v if t == 'q' else 0 for t, v in order]
json.dump({'edited': sorted({tuple(x) for x in LOG['edited']}), 'added': ADDED, 'deleted': [], 'notes': sorted(LOG['notes']), 'notes_prefix': PFX,
           'new_slides': [i + 1 for i, o in enumerate(ordr) if o == 0], 'user_authorised': [], 'order': ordr}, open(OUT + '.allow.json', 'w'), indent=0)
PM = {str(p): H67[p] for p in range(1, len(O68) + 1)}
json.dump({'v68_to_v22t_first': PM, 'v68_to_v22t_all': {str(p): ([POS[('q', k)] for k in GROUP[e[1]]] if e[0] == 'old' else [POS[('h', p)]]) for p, e in enumerate(O68, 1)},
           'v22s_to_v22t': {str(k): QPOS[k] for k in range(1, NS + 1)}}, open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t_v68.json', 'w'), indent=0)
json.dump({'order': order, 'log': {k: (v if not isinstance(v, dict) else {str(a): b for a, b in v.items()}) for k, v in LOG.items()}}, open(W9 + 'build22t_log.json', 'w'), indent=0)
print('map pics', LOG.get('map_pics')); print('slides', len(FINAL), 'new', len(NEW), 'cov added', len(LOG['cov']), 'cov skipped', len(LOG['cov_skip']), 'not fitted', len(LOG['not_fitted']))
print('leads reworded', len(LOG['leads']), 'stale user refs', len(LOG['stale_user_refs']), 'code notes', len(LOG['code_notes']))
