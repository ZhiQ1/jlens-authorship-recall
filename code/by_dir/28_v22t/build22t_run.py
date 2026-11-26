
# ================= v22t run part (appended to build22t_head.py by make_build.sh) =================
O67 = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/order_v67.json'))
RM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map.json')); V2V = {int(a): b for a, b in RM['v66_to_v67'].items()}
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
for pos, e in enumerate(O67, 1):
    if e[0] == 'old':
        h66 = e[1]; assert V2V[h66] == pos, (h66, pos)
        for k in GROUP[h66]: order.append(('q', k))
    else:
        order.append(('h', pos))
assert len([e for e in order if e[0] == 'q']) == NS
POS = {e: i + 1 for i, e in enumerate(order)}
QPOS = {k: POS[('q', k)] for k in range(1, NS + 1)}
for pos, e in enumerate(O67, 1):
    H67[pos] = POS[('h', pos)] if e[0] == 'new' else QPOS[GROUP[e[1]][0]]
def q2t(n): return QPOS.get(n, n)

# ---- new native slides
NEW = {}
for e in order:
    if e[0] != 'h': continue
    ns = prs.slides.add_slide(BGREF.slide_layout)
    for ph in list(ns.placeholders): ph._element.getparent().remove(ph._element)
    nb_ = bg_and_number(ns); full_page(ns, e[1]); NEW[e[1]] = ns
    el_ = nb_._element; el_.getparent().remove(el_); ns.shapes._spTree.append(el_)
    ns.notes_slide.notes_text_frame.text = PFX + 'Native page built from HTML deck v67 page %d.' % e[1]

# ---- coverage lines (Now asking / So / evidence tag) added in v67: mirror where the pptx slide lacks them
def slide_text(s): return ' '.join(x.text_frame.text for x in s.shapes if x.has_text_frame)
def has_feat(s, feat):
    t = slide_text(s)
    if feat == 'covna': return 'Now asking' in t
    if feat == 'covso': return re.search(r'(^|\s)So\b\s*(\((section|this slide)\))?\s*[:：]', t) is not None
    if feat == 'covtg': return re.search(r'\b(settled|locked|descriptive|exploratory|supported|not supported|caveat|marginal)\b', t, re.I) is not None and ('Evidence' in t or re.search(r'locked ·|settled|exploratory|descriptive', t) is not None)
COVK = ('covna', 'covso', 'covtg')
for pos, e in enumerate(O67, 1):
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
        LOG['cov'].append([k, f, round(spot[0]), round(spot[1]), sc])
        LOG['notes'].setdefault(k, []).append('Coverage line from HTML deck v67 page %d added (%s), placed in free space.' % (pos, {'covna': 'Now asking', 'covso': 'So', 'covtg': 'evidence tag'}[f]))

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
PM = {str(p): H67[p] for p in range(1, len(O67) + 1)}
json.dump({'v67_to_v22t_first': PM, 'v67_to_v22t_all': {str(p): ([POS[('q', k)] for k in GROUP[e[1]]] if e[0] == 'old' else [POS[('h', p)]]) for p, e in enumerate(O67, 1)},
           'v22s_to_v22t': {str(k): QPOS[k] for k in range(1, NS + 1)}}, open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t.json', 'w'), indent=0)
json.dump({'order': order, 'log': {k: (v if not isinstance(v, dict) else {str(a): b for a, b in v.items()}) for k, v in LOG.items()}}, open(W9 + 'build22t_log.json', 'w'), indent=0)
print('slides', len(FINAL), 'new', len(NEW), 'cov added', len(LOG['cov']), 'cov skipped', len(LOG['cov_skip']), 'not fitted', len(LOG['not_fitted']))
print('leads reworded', len(LOG['leads']), 'stale user refs', len(LOG['stale_user_refs']))
