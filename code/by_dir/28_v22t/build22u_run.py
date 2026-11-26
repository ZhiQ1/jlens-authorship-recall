
# ================= v22u: HTML v69/v70 changes mirrored on v22t =================
MAP = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t_v68.json'))
for p, v in MAP['v68_to_v22t_first'].items(): H67[int(p)] = v
H67[161] = NS + 1                                     # new backup B23 goes last
REBUILD = {36: 37, 37: 38, 53: 57, 54: 58, 82: 86, 83: 87, 108: 115, 127: 135, 135: 143, 136: 144}   # HTML v70 page -> our-only v22t slide
MAPS = {int(a): b for a, b in json.load(open(W9 + 'maps70/maps.json')).items()} if os.path.exists(W9 + 'maps70/maps.json') else {}
_load0 = load
def load(h, mode):
    d = _load0(h, mode)
    if d is None or mode != 'full' or h not in MAPS: return d
    b = MAPS[h]
    def inside(x, y): return b['x'] - 2 <= x <= b['x'] + b['w'] + 2 and b['y'] - 2 <= y <= b['y'] + b['h'] + 2
    def ctr(it):
        if it['k'] == 'poly': xs = [q[0] for q in it['pts']]; ys = [q[1] for q in it['pts']]; return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        return it['x'] + it.get('w', 0) / 2, it['y'] + it.get('h', 0) / 2
    SVGTXT = ('Read early, said late: where each step happens', 'x: the prompt as Qwen3 tokens', 'Step 1:')
    LEG = {'settled', 'locked', 'fairly solid', 'descriptive', 'exploratory', 'pending'}
    def keep(it):
        t0 = ''.join(r.get('t', '') for r in it.get('runs') or []).lstrip()
        return t0.startswith('Now asking') or t0.startswith('So (') or any(k in (it.get('cls') or '').split() for k in ('askl', 'soln', 'covna', 'covso', 'covtg', 'lead'))
    def clipped(it):
        if it['k'] != 'text' or it['x'] > b['x'] + b['w'] or it['x'] + it['w'] < b['x']: return False
        if not (b['y'] - 70 <= it['y'] <= b['y'] + b['h'] + 40): return False
        t0 = ''.join(r.get('t', '') for r in it.get('runs') or []).strip()
        return t0.startswith(SVGTXT) or (t0 in LEG and it['h'] <= 14)
    d = dict(d); d['items'] = [it for it in d['items'] if keep(it) or not (inside(*ctr(it)) or clipped(it))]
    d['maths'] = [m if not inside(m[0] + m[2] / 2, m[1] + m[3] / 2) else [m[0], m[1], m[2], m[3], False] for m in d['maths']]
    return d
LOG['rebuilt'] = []
for h, k in REBUILD.items():
    s = SL[k - 1]; ups = user_ids(s); assert not ups, (k, 'has user shapes')
    shapes = list(s.shapes); bg = shapes[0]; assert bg.shape_type == 13 and bg.left == 0 and bg.top == 0
    num = [sh for sh in shapes if sh.has_text_frame and re.fullmatch(r'\d{1,3}', sh.text_frame.text.strip()) and sh.top > 0.8 * SH]
    keep_ = {bg.shape_id} | {x.shape_id for x in num[-1:]}
    for sh in shapes:
        if sh.shape_id in keep_: continue
        LOG['deleted'].append([k, sh.shape_id, 'rebuilt from HTML v70 page %d' % h]); sh._element.getparent().remove(sh._element)
    full_page(s, h)
    if h in MAPS:
        b = MAPS[h]; add_pic(s, W9 + 'maps70/map_%03d.png' % h, b['x'], b['y'], b['w'], b['h'])
    if num:      # keep the slide-number box last
        el_ = num[-1]._element; el_.getparent().remove(el_); s.shapes._spTree.append(el_)
    LOG['rebuilt'].append([h, k]); LOG['notes'].setdefault(k, []).append('Our content rebuilt from HTML deck v70 page %d (canonical matrix / v69–v70 fixes).' % h)

# HTML 23 (v22t S24): verb fix in our own shapes ("names" -> "carries information about")
REPL23 = [(r"the own state names its own first author better", "the paper's own state carries information about its first author"),
          (r"can the title state name its own first author when", "does the paper's own title state carry information about its first author when")]
def frame_sub(tf, pairs):
    ch = False
    for p in tf.paragraphs:
        full = ''.join(r.text for r in p.runs); new = full
        for a, b_ in pairs: new = re.sub(a, b_, new)
        if new == full: continue
        for r in p.runs:
            nr = r.text
            for a, b_ in pairs: nr = re.sub(a, b_, nr)
            if nr != r.text: r.text = nr; ch = True
        if ''.join(r.text for r in p.runs) != new and p.runs:
            p.runs[0].text = new
            for r in p.runs[1:]: r.text = ''
        ch = True
    return ch
for k, pairs in ((24, REPL23),):
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if sh.shape_id in ups or not sh.has_text_frame or CJK.search(sh.text_frame.text): continue
        if frame_sub(sh.text_frame, pairs): LOG['edited'].append([k, sh.shape_id])
    LOG['notes'].setdefault(k, []).append('Wording: "the own state names its first author" -> "carries information about its first author" (HTML v69).')

# HTML 35 (v22t S36, the user's table): our "How to read" line updated; current results noted beside the user's table (table untouched)
s = SL[35]; ups = user_ids(s)
for sh in s.shapes:
    if sh.shape_id in ups or not sh.has_text_frame: continue
    if sh.text_frame.text.startswith('How to read'):
        frame_sub(sh.text_frame, [(r' · ⚠ = known issue, marked for confirmation, not yet changed', ''),
                                  (r'measured top lens word and the evidence matrix see slide 36b', 'measured top lens word and the evidence matrix → slide %d' % H67[37])])
        LOG['edited'].append([36, sh.shape_id])
occ = ink_map(36); placed = np.zeros_like(occ)
lines = ['Current results (2026-11-24, from the canonical matrix):',
         '• Task only (H1): downgraded — “:” follows the question; the format layer is not pinned down (descriptive; locked rule downgraded) → slide %d' % H67[53],
         '• Change-the-question check: cannot separate — ceiling: the same title text gives cosine 0.998 already at L4 → slide %d' % H67[77],
         '• Paper facts are inferable from the title text and readable early (attribute probe) · surname signal from L8']
w, hgt = 600, 64
spot = find_spot(occ, placed, 660, 560, w, hgt) or find_spot(occ, placed, 40, 560, w, hgt)
if spot:
    tb = s.shapes.add_textbox(E(spot[0]), E(spot[1]), E(w), E(hgt)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for j, ln in enumerate(lines):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph(); r = p.add_run(); r.text = ln
        r.font.size = Pt((11 if j else 11.5) * PT); r.font.name = 'Noto Sans SC'; r.font.bold = (j == 0); r.font.color.rgb = RGBColor(0x22, 0x30, 0x4A)
    LOG['notes'].setdefault(36, []).append('Current results from the canonical matrix noted beside your table (table unchanged).')
else:
    LOG['not_fitted'].append([36, 'current results note'])

# new backup B23 (HTML 161), last
ns = prs.slides.add_slide(BGREF.slide_layout)
for ph in list(ns.placeholders): ph._element.getparent().remove(ph._element)
nb_ = bg_and_number(ns); full_page(ns, 161)
el_ = nb_._element; el_.getparent().remove(el_); ns.shapes._spTree.append(el_)
ns.notes_slide.notes_text_frame.text = PFX + 'Native page built from HTML deck v70 page 161 (B23).'
FINAL = list(prs.slides)
for f in ns._element.iter('{%s}fld' % AN):
    if f.get('type') == 'slidenum':
        t = f.find('{%s}t' % AN)
        if t is not None: t.text = str(len(FINAL))
for k, segs in LOG['notes'].items():
    tf = SL[k - 1].notes_slide.notes_text_frame
    for z in dict.fromkeys(segs): tf.add_paragraph().add_run().text = PFX + z
for k in range(1, NS + 1):
    nid = max(ORIG[k]) + 4000
    for x in SL[k - 1].shapes:
        if any(x._element is b for b in ORIG_EL[k]): continue
        x._element.xpath('./*[1]/p:cNvPr')[0].set('id', str(nid)); nid += 1
prs.save(OUT)
ADDED = [[k, sid] for k in range(1, NS + 1) for sid in [x.shape_id for x in SL[k - 1].shapes] if sid not in ORIG[k]]
DELS = [[k, sid] for k, sid, _ in LOG['deleted']]
json.dump({'edited': sorted({tuple(x) for x in LOG['edited']}), 'added': ADDED, 'deleted': DELS, 'notes': sorted(LOG['notes']), 'notes_prefix': PFX,
           'new_slides': [NS + 1], 'user_authorised': [], 'order': list(range(1, NS + 1)) + [0]}, open(OUT + '.allow.json', 'w'), indent=0)
M = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22t_v68.json'))
out = {'v70_to_v22u_first': dict(M['v68_to_v22t_first'], **{'161': NS + 1}), 'v70_to_v22u_all': dict(M['v68_to_v22t_all'], **{'161': [NS + 1]}),
       'note': 'v22u = v22t slide order unchanged (1-168) + B23 at 169; HTML v69/v70 kept v68 page numbers 1-160, added 161.'}
json.dump(out, open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22u_v70.json', 'w'), indent=0)
json.dump({'log': {k: (v if not isinstance(v, dict) else {str(a): b for a, b in v.items()}) for k, v in LOG.items()}}, open(W9 + 'build22u_log.json', 'w'), indent=0)
print('slides', len(FINAL), 'rebuilt', LOG['rebuilt'], 'edited', len(LOG['edited']), 'not fitted', LOG['not_fitted'])
