import re, sys, os
S='/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/180809d4-e5ec-4f13-97be-7ef90a42d8be/scratchpad'
pages=[('c3ccbea9-502b-4d5a-8d8a-0269793ad0de','experiment_walkthrough_zh',0),
('c68db092-617b-4e52-a42c-a8451e68dae9','experiment_walkthrough_methods_zh',0),
('934ec17e-7c99-49c1-a12a-bd744cce314e','stage13_script_zh_en',1),
('e00057aa-7309-49ff-a01b-e5b34d1c9a52','keys_and_shelves_script_zh_en',1),
('eeb8ae47-737a-4220-a550-95a9d1224872','methods_handbook_guide_plain_zh',0),
('d8d00f46-53c4-4709-913c-dcfa30670503','process_report',0),
('59d82f22-3013-4416-b299-4193ca39091e','scoring_audit',0),
('e8e3fad3-99f2-4a08-991b-10867046c5d9','methods_addendum',0)]
PRE='<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style></head><body>\n'
SUF='\n</body></html>'
ZH='本页部分数字和措辞正在更正，以<a href="https://claude.ai/artifact/XtBbnuuE9xKki4uiL7KxBs" style="color:#7a4b00">进度汇报（合并版）</a>和<a href="https://claude.ai/artifact/QB335qoaBWvSdFyfvc2bSe" style="color:#7a4b00">报告 v29h</a>为准。'
EN='<br><span lang="en">Some numbers and wording on this page are being corrected; the merged progress report and report v29h take precedence.</span>'
def banner(bi): return '<div role="note" style="margin:0 0 16px;padding:10px 14px;border:1px solid #b7791f;border-radius:6px;background:#fff6e0;color:#3d2a00;font-size:15px;line-height:1.55">'+ZH+(EN if bi else '')+'</div>'
for uid,slug,bi in pages:
    b=open(f'{S}/artifact-files/{uid}/index.html','rb').read().decode('utf-8')
    assert b.startswith(PRE), slug; assert b.endswith(SUF), slug
    d=b[len(PRE):-len(SUF)]
    open(f'{S}/banners_20261108/dewrapped/{slug}.html','w',encoding='utf-8',newline='').write(d)
    last_style=d.rfind('</style>')
    m=re.compile(r'<(header|main|h1)\b').search(d,last_style)
    tag=m.group(1); pos=m.start()
    if tag=='main':  # put banner inside main, before its first child
        pos=d.index('>',pos)+1
        if d[pos]=='\n': pos+=1
    out=d[:pos]+banner(bi)+d[pos:]
    open(f'{S}/banners_20261108/{slug}.html','w',encoding='utf-8',newline='').write(out)
    print(slug, 'anchor', tag, 'starts:', repr(d[:40]), 'banner before:', repr(d[pos:pos+30]))
