"""2026-11-25 main pptx v22w -> v22x (mirrors HTML v73; HANDOFF item 47):
- story-figure images updated in place (same picture shape, new image blob) where 31_figures/deck16x9 changed:
  flow a, flow d, L24-L40 a/b, L4-L24 a;
- 4 new native story slides (as build22w): step0b after S141; exp2story_a, exp2story_b, contrib_overview after S165;
- "slide N" in our own shapes renumbered v22w -> v22x (142-165 -> +1, >=166 -> +4); user shapes / Chinese boxes never edited.
usage: build22x.py [DRY]"""
import sys, json, re, copy, uuid, hashlib
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
DRY = len(sys.argv) > 1
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
W = '/home/zhang.zhiqi2/jlens_work/33_v73/'
IN_, OUT = D + 'jlens_1113_pre_v22w.pptx', D + 'jlens_1113_pre_v22x.pptx'
AN = 'http://schemas.openxmlformats.org/drawingml/2006/main'; CJK = re.compile('[一-鿿]')
PFX = '[2026-11-25 v22x] '
prs = Presentation(IN_); SL = list(prs.slides); SW, SH = prs.slide_width, prs.slide_height; NS = len(SL); assert NS == 188
K = SW / 1280.0; PT = 0.5625
def E(v): return Emu(int(round(v * K)))
UPLOAD = Presentation(D + 'stage1-13 超长卷.pptx'); UPS = {su.slide_id: {x.shape_id for x in su.shapes} for su in UPLOAD.slides}
def user_ids(s): return UPS.get(s.slide_id, set())
LOG = {'edited': [], 'notes': {}, 'renum': [], 'img': [], 'stale_user_refs': []}
CHANGED = ['flow_16x9_a.png', 'flow_16x9_d.png', 'stage_L24_L40_16x9_a.png', 'stage_L24_L40_16x9_b.png', 'stage_L4_L24_16x9_a.png']
OLDDIR = '/home/zhang.zhiqi2/jlens_work/32_v72/story16x9/'
# ---------------- 1) block S141-S165: picture names in order; swap updated images
blockf = []
for k in range(141, 166):
    pics = [sh for sh in SL[k - 1].shapes if sh.shape_type == 13 and sh.name.startswith('story figure ')]
    assert len(pics) == 1, k; blockf.append(pics[0].name[len('story figure '):] + '.png')
    f = blockf[-1]
    if f in CHANGED:
        pic = pics[0]; rid = pic._element.blipFill.find('{%s}blip' % AN).get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        part = SL[k - 1].part.related_part(rid)
        assert hashlib.sha256(part.blob).digest() == hashlib.sha256(open(OLDDIR + f, 'rb').read()).digest(), ('old blob mismatch', k, f)
        users = [s for s in SL for r in s.part.rels.values() if not r.is_external and r.target_part is part]
        assert len(users) == 1, ('shared image part', k, f, len(users))
        part._blob = open(W + 'story16x9/' + f, 'rb').read()
        LOG['edited'].append([k, pic.shape_id]); LOG['img'].append([k, f])
        LOG['notes'].setdefault(k, []).append('Story figure image updated (HTML v73).')
files = [l.split()[1] for l in open('/home/zhang.zhiqi2/jlens_work/31_figures/deck16x9/ORDER.txt') if l.strip()]
assert [f for f in files if f in blockf] == blockf and len(LOG['img']) == len(CHANGED), (blockf, LOG['img'])
# ---------------- 2) renumber "slide N" in our own shapes
REF = re.compile(r'(\b[Ss]lides? )(\d+(?:\s*(?:[,–-]|and|to|&)\s*\d+)*)')
def remap(text, f): return REF.sub(lambda m: m.group(1) + re.sub(r'\d+', lambda x: str(f(int(x.group(0)))), m.group(2)), text)
def old2new(n): return n + 1 if 142 <= n <= 165 else (n + 4 if 166 <= n <= NS else n)
for k in range(1, NS + 1):
    s = SL[k - 1]; ups = user_ids(s)
    for sh in s.shapes:
        if sh.shape_id in ups or not sh.has_text_frame or CJK.search(sh.text_frame.text): continue
        ch = False
        for p_ in sh.text_frame.paragraphs:
            for r in p_.runs:
                nt = remap(r.text, old2new)
                if nt != r.text: r.text = nt; ch = True
        if ch:
            LOG['edited'].append([k, sh.shape_id]); LOG['renum'].append([k, sh.shape_id])
            LOG['notes'].setdefault(k, []).append('Slide references renumbered to v22x (HTML v73 order).')
    for sh in s.shapes:
        if sh.shape_id in ups and sh.has_text_frame and REF.search(sh.text_frame.text): LOG['stale_user_refs'].append([k, sh.shape_id, sh.text_frame.text[:60]])
# ---------------- 3) 4 new native slides (helpers copied from build22w.py)
exec(open(W + 'pptx_helpers.py').read())
NEWS = json.load(open(W + 'new_slides_v73.json')); assert [x[0] for x in NEWS] == [134, 159, 160, 161]
NEWSL = []
for pg, fname, title, ask, so, tc, tt, alt, *rest in NEWS:
    sok = rest[0] if rest else 'So (this slide)'
    ns = prs.slides.add_slide(BGREF.slide_layout)
    for ph in list(ns.placeholders): ph._element.getparent().remove(ph._element)
    nb = bg_and_number(ns)
    clone(ns, shp(5)); tg = clone(ns, shp(6)); set_runs(tg, [('Summary · story figures', {})])
    ti = clone(ns, shp(7)); set_runs(ti, [(title, {'size': 24 * PT, 'bold': True})])
    ti.left, ti.top, ti.width, ti.height = E(70), E(40), E(1110), E(32)
    ak = clone(ns, shp(8)); set_runs(ak, [('Now asking: ', {'size': 15 * PT, 'bold': True, 'color': '22304A'}), (ask, {'size': 15 * PT, 'bold': False, 'color': '22304A'})])
    ak.left, ak.top, ak.width, ak.height = E(70), E(76), E(1140), E(20)
    pic = ns.shapes.add_picture(W + 'story16x9/' + fname, E(116), E(100), E(1048), E(589.5)); pic.name = 'story figure ' + fname[:-4]
    pic._element.nvPicPr.cNvPr.set('descr', alt)
    b1 = clone(ns, shp(21)); b2 = clone(ns, shp(22)); st_ = clone(ns, shp(23))
    for b in (b1, b2): b.top, b.height = E(694), E(22)
    b1.left, b1.width = E(70), E(1140); b2.left = E(70)
    fg, hl = TAGC[tc]
    set_runs(st_, [(sok + ': ', {'size': 14 * PT, 'bold': True, 'color': 'B54708'}), (so + ' ', {'size': 14 * PT, 'bold': False, 'color': '22304A'}),
                   (' ' + tt + ' ', {'size': 11 * PT, 'bold': True, 'color': fg, 'font': 'Noto Sans SC', 'hl': hl})])
    st_.left, st_.top, st_.width, st_.height = E(82), E(697), E(1120), E(18)
    st_.text_frame.word_wrap = True
    el_ = nb._element; el_.getparent().remove(el_); ns.shapes._spTree.append(el_)
    ns.notes_slide.notes_text_frame.text = PFX + 'Native page built from HTML deck v73 page %d (summary chapter, story figure).' % pg
    NEWSL.append(ns)
# ---------------- 4) order
lst = prs.slides._sldIdLst; ids = list(lst)
old_el = {k: ids[k - 1] for k in range(1, NS + 1)}; new_el = ids[NS:]
SEQ = ([('old', k) for k in range(1, 142)] + [('new', 0)] + [('old', k) for k in range(142, 166)] + [('new', 1), ('new', 2), ('new', 3)]
       + [('old', k) for k in range(166, NS + 1)])
for e in list(lst): lst.remove(e)
for t, k in SEQ: lst.append(old_el[k] if t == 'old' else new_el[k])
for k, segs in LOG['notes'].items():
    tf = SL[k - 1].notes_slide.notes_text_frame
    for z in dict.fromkeys(segs): tf.add_paragraph().add_run().text = PFX + z
print('img swaps', LOG['img']); print('renum shapes', len(LOG['renum']), LOG['renum'][:10], 'stale user refs', len(LOG['stale_user_refs']))
if DRY: sys.exit(0)
prs.save(OUT)
order = [k if t == 'old' else 0 for t, k in SEQ]
json.dump({'edited': sorted({tuple(x) for x in LOG['edited']}), 'added': [], 'deleted': [], 'notes': sorted(LOG['notes']), 'notes_prefix': PFX,
           'new_slides': [i for i, o in enumerate(order, 1) if o == 0], 'deleted_slides': [], 'user_authorised': [], 'order': order},
          open(OUT + '.allow.json', 'w'), indent=0)
PM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22w_v72.json'))
RM = json.load(open('/home/zhang.zhiqi2/jlens_work/27_v67/renumber_map_v73.json'))
all73 = {}
for p72, ks in PM['v72_to_v22w_all'].items(): all73[RM['v72_to_v73'][p72]] = [old2new(k) for k in ks]
newpos = [i for i, o in enumerate(order, 1) if o == 0]
for x, kk in zip(NEWS, newpos): all73[x[0]] = [kk]
json.dump({'v73_to_v22x_first': {str(p): all73[p][0] for p in sorted(all73)}, 'v73_to_v22x_all': {str(p): all73[p] for p in sorted(all73)},
           'v22w_to_v22x': {str(k): old2new(k) for k in range(1, NS + 1)},
           'note': 'v22x = HTML v73 order; story-figure block S141-S169 (HTML v73 133-161); new native S142, S167, S168, S169; images updated on 5 block slides.'},
          open('/home/zhang.zhiqi2/jlens_work/27_v67/pptx_map_v22x_v73.json', 'w'), indent=0)
json.dump(LOG, open(W + 'build22x_log.json', 'w'), indent=0, ensure_ascii=False)
print('saved', OUT, 'slides', len(prs.slides), 'new at', newpos)
