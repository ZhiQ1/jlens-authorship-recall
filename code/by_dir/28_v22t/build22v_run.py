# ================= v22v: HTML v71 changes mirrored on v22u =================
# - 3 new native slides from HTML v71 pages 16, 77, 107 (Statistical conventions (continued), How the 75% is computed, The locked rule)
# - B12 (v70 151 -> v71 47) and B22 (v70 150 -> v71 54) move next to their main slides
# - the nine How-computed backups (v70 152-160 = v22u S160-S168) are deleted (user-approved 2026-11-24, after migration)
# - B23 kept; every "slide N" in our own shapes renumbered v22u -> v22v; user shapes and Chinese boxes untouched
RM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map_v71.json'))
V70_71 = {int(a): b for a, b in RM['v70_to_v71'].items()}
NEW71 = {v: k for k, v in RM['new'].items()}                 # v71 page -> slot name
DEL70 = set(RM['deleted_v70'])
PM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22u_v70.json'))['v70_to_v22u_all']
A70 = {int(a): b for a, b in PM.items()}
INV = {v: q for q, v in V70_71.items()}
N71 = max(list(V70_71.values()) + list(NEW71))
DEL_OLD = sorted(x for q in DEL70 for x in A70[q])          # v22u slides to delete
assert DEL_OLD == list(range(160, 169)), DEL_OLD
# new order: list of ('old', k) / ('new', p71)
SEQ = []
for p in range(1, N71 + 1):
    if p in NEW71: SEQ.append(('new', p)); continue
    q = INV[p]
    for k in A70[q]: SEQ.append(('old', k))
assert sorted(k for t, k in SEQ if t == 'old') == sorted(set(range(1, NS + 1)) - set(DEL_OLD))
NEWPOS = {}; OLD2NEW = {}; P71_FIRST = {}
for i, (t, k) in enumerate(SEQ, 1):
    if t == 'new': NEWPOS[k] = i
    else: OLD2NEW[k] = i
for p in range(1, N71 + 1):
    if p in NEW71: P71_FIRST[p] = NEWPOS[p]
    else: P71_FIRST[p] = OLD2NEW[A70[INV[p]][0]]
for p, v in P71_FIRST.items(): H67[p] = v                      # HTML v71 page -> v22v first slide (refs inside the new native pages)
# deleted backups: references to them go to the new "Statistical conventions (continued)" slide (repeated statistics moved there) — logged
def old2new(n):
    if n in OLD2NEW: return OLD2NEW[n]
    if n in DEL_OLD: LOG.setdefault('ref_to_deleted', []).append(n); return NEWPOS[16]
    return n
# 1) renumber "slide N" in our own shapes on the kept slides
LOG['renum'] = []
for k in range(1, NS + 1):
    if k in DEL_OLD: continue
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if sh.shape_id in ups or not sh.has_text_frame or CJK.search(sh.text_frame.text): continue
        ch = False
        for p_ in sh.text_frame.paragraphs:
            for r in p_.runs:
                nt = remap(r.text, old2new)
                if nt != r.text: r.text = nt; ch = True
        if ch: LOG['edited'].append([k, sh.shape_id]); LOG['renum'].append([k, sh.shape_id]); LOG['notes'].setdefault(k, []).append('Slide references renumbered to v22v (HTML v71 order).')
    for sh in s.shapes:                                        # stale refs inside user shapes: report only
        if sh.shape_id in ups and sh.has_text_frame and REF.search(sh.text_frame.text): LOG['stale_user_refs'].append([k, sh.shape_id, sh.text_frame.text[:60]])
# B22's tag pointed at the old hypothesis-table slide; HTML v71 says "for slide 53" (the ":" ratio page) -> its pptx slide
for sh in SL[158 - 1].shapes:
    if sh.shape_id in user_ids(SL[157]) or not sh.has_text_frame: continue
    if re.search(r'Backup B22 · for slide \d+', sh.text_frame.text):
        for p_ in sh.text_frame.paragraphs:
            for r in p_.runs: r.text = re.sub(r'(for slide )\d+', lambda m: m.group(1) + str(P71_FIRST[53]), r.text)
        LOG['edited'].append([158, sh.shape_id]); LOG['notes'].setdefault(158, []).append('B22 tag points to the ":" ratio slide (HTML v71 slide 53).')
# 2) the 3 new native slides (appended, moved into place below)
NEWSL = {}
for p in sorted(NEW71):
    ns = prs.slides.add_slide(BGREF.slide_layout)
    for ph in list(ns.placeholders): ph._element.getparent().remove(ph._element)
    nb_ = bg_and_number(ns); full_page(ns, p)
    el_ = nb_._element; el_.getparent().remove(el_); ns.shapes._spTree.append(el_)
    ns.notes_slide.notes_text_frame.text = PFX + 'Native page built from HTML deck v71 page %d.' % p
    NEWSL[p] = ns
# 3) reorder + delete
PNS = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
RNS = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
lst = prs.slides._sldIdLst; ids = list(lst)
old_el = {k: ids[k - 1] for k in range(1, NS + 1)}
new_el = {p: ids[NS + i] for i, p in enumerate(sorted(NEW71))}
for k in DEL_OLD:                                              # drop the slide part from the package
    el = old_el[k]; rid = el.get(RNS); prs.part.drop_rel(rid); lst.remove(el)
for e in list(lst): lst.remove(e)
for t, k in SEQ: lst.append(old_el[k] if t == 'old' else new_el[k])
FINAL = list(prs.slides); assert len(FINAL) == len(SEQ)
for k, segs in LOG['notes'].items():
    tf = SL[k - 1].notes_slide.notes_text_frame
    for z in dict.fromkeys(segs): tf.add_paragraph().add_run().text = PFX + z
prs.save(OUT)
order = [k if t == 'old' else 0 for t, k in SEQ]
json.dump({'edited': sorted({tuple(x) for x in LOG['edited']}), 'added': [], 'deleted': [], 'notes': sorted(LOG['notes']), 'notes_prefix': PFX,
           'new_slides': [i for i, o in enumerate(order, 1) if o == 0], 'deleted_slides': DEL_OLD, 'user_authorised': [], 'order': order},
          open(OUT + '.allow.json', 'w'), indent=0)
all_ = {}
for i, (t, k) in enumerate(SEQ, 1):
    if t == 'new': all_.setdefault(k, []).append(i)
    else: all_.setdefault(V70_71[[q for q in A70 if k in A70[q]][0]], []).append(i)
json.dump({'v71_to_v22v_first': {str(p): P71_FIRST[p] for p in range(1, N71 + 1)}, 'v71_to_v22v_all': {str(p): all_[p] for p in sorted(all_)},
           'v22u_to_v22v': {str(k): OLD2NEW[k] for k in sorted(OLD2NEW)}, 'deleted_v22u': DEL_OLD,
           'note': 'v22v = HTML v71 order; 3 new native slides (v71 16, 77, 107); v22u S160-S168 (How-computed backups B13-B21) deleted; B12/B22 moved next to their main slides.'},
          open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22v_v71.json', 'w'), indent=0)
json.dump({'log': {k: (v if not isinstance(v, dict) else {str(a): b for a, b in v.items()}) for k, v in LOG.items()}}, open(W9 + 'build22v_log.json', 'w'), indent=0)
print('slides', len(FINAL), 'new at', [i for i, o in enumerate(order, 1) if o == 0], 'renum shapes', len(LOG['renum']), 'refs to deleted', LOG.get('ref_to_deleted'), 'stale user refs', len(LOG['stale_user_refs']))
