BGREF = SL[16 - 1]          # v22v S16: native page built from HTML (notebook background, tag box, title, sub line, So line, slide number)
def shp(sid): return next(sh for sh in BGREF.shapes if sh.shape_id == sid)
def bg_and_number(dst, ref=BGREF):
    bg = ref.shapes[0]; assert bg.shape_type == 13 and bg.left == 0 and bg.top == 0
    el = copy.deepcopy(bg._element); dst.shapes._spTree.insert(2, el)
    RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
    rid = bg._element.blipFill.find('{%s}blip' % AN).get(RID)
    part = ref.part.related_part(rid); new_rid = dst.part.relate_to(part, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
    el.blipFill.find('{%s}blip' % AN).set(RID, new_rid)
    num = next(sh for sh in ref.shapes if sh.has_text_frame and re.fullmatch(r'\d{1,3}', sh.text_frame.text.strip()) and sh.top > 0.8 * SH)
    el2 = copy.deepcopy(num._element); dst.shapes._spTree.append(el2)
    sh = dst.shapes[-1]; p = sh.text_frame.paragraphs[0]._p
    rs = p.findall('{%s}r' % AN) + p.findall('{%s}fld' % AN); rpr = rs[0].find('{%s}rPr' % AN) if rs else None
    for r in rs: p.remove(r)
    if not rs:
        rpr = None
    fld = etree.SubElement(p, '{%s}fld' % AN); fld.set('id', '{' + str(uuid.uuid4()).upper() + '}'); fld.set('type', 'slidenum')
    if rpr is not None: fld.append(copy.deepcopy(rpr))
    t = etree.SubElement(fld, '{%s}t' % AN); t.text = '0'
    endp = p.find('{%s}endParaRPr' % AN)
    if endp is not None: p.remove(endp); p.append(endp)
    return sh
def clone(dst, src):
    el = copy.deepcopy(src._element); dst.shapes._spTree.append(el); return dst.shapes[-1]
def set_runs(sh, parts):
    """parts: list of (text, dict(size, bold, color, font, hl))"""
    tf = sh.text_frame
    for p in tf.paragraphs[1:]: p._p.getparent().remove(p._p)
    p = tf.paragraphs[0]
    proto = p.runs[0]._r if p.runs else None
    for r in list(p._p.findall('{%s}r' % AN)): p._p.remove(r)
    for txt, st in parts:
        if proto is not None:
            r_el = copy.deepcopy(proto); r_el.find('{%s}t' % AN).text = txt; endp = p._p.find('{%s}endParaRPr' % AN)
            if endp is not None: endp.addprevious(r_el)
            else: p._p.append(r_el)
            from pptx.text.text import _Run
            r = _Run(r_el, p)
        else:
            r = p.add_run(); r.text = txt
        f = r.font
        if 'size' in st: f.size = Pt(st['size'])
        if 'bold' in st: f.bold = st['bold']
        if 'font' in st: f.name = st['font']
        if 'color' in st: f.color.rgb = RGBColor.from_string(st['color'])
        rpr = r._r.get_or_add_rPr()
        for h in rpr.findall('{%s}highlight' % AN): rpr.remove(h)
        if st.get('hl'):
            h = etree.Element('{%s}highlight' % AN); c = etree.SubElement(h, '{%s}srgbClr' % AN); c.set('val', st['hl'])
            pos = None
            for i, ch in enumerate(rpr):
                if etree.QName(ch).localname in ('uLnTx', 'uLn', 'uFillTx', 'uFill', 'latin', 'ea', 'cs', 'sym', 'hlinkClick', 'hlinkMouseOver', 'rtl', 'extLst'): pos = i; break
            if pos is None: rpr.append(h)
            else: rpr.insert(pos, h)
TAGC = {'desc': ('FFFFFF', '6A7385'), 'expl': ('FFFFFF', 'B54708'), 'lnot': ('FFFFFF', 'C84A3E'), 'lsup': ('FFFFFF', '3C78B4'),
        'settled': ('FFFFFF', '2E7D46'), 'solid': ('3C78B4', None), 'lim': ('B54708', None)}
