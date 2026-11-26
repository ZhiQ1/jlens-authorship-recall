import sys
sys.path.insert(0,'/scratch/zhang.zhiqi2/pylib2')
from pptx import Presentation
P=Presentation(sys.argv[1]); 
for k in [int(x) for x in sys.argv[2].split(',')]:
    s=P.slides[k-1]; print('=== S%d'%k, s.slide_layout.name)
    for sh in s.shapes:
        fs=[(r.font.size.pt if r.font.size else None, r.font.name, (lambda c: (str(c.rgb) if c.type==1 else "sch") if c.type else None)(r.font.color), r.font.bold) for p in sh.text_frame.paragraphs for r in p.runs][:3] if sh.has_text_frame else ''
        print(sh.shape_id, sh.shape_type, sh.name[:20], round(sh.left/12700), round(sh.top/12700), round(sh.width/12700), round(sh.height/12700), (sh.text_frame.text[:60] if sh.has_text_frame else ''), fs)
