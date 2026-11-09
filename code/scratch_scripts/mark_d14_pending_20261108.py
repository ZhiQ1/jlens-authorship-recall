# 2026-11-08: user asked that local docs not cite D14-1 as settled before it is locked -> tag every mention "draft, pending confirmation".
import re, shutil, sys, os
R='/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
files=['stage1_11/stage1_11_report.html','merged_deck/stage1_11_deck.html','talk/src/export/notes_zh.json','talk/src/export/with_notes.html',
 'methods/methods_handbook.html','methods/parts/B_global2.html','methods/parts/K_post_defence.html','process_report/index.html','process_report/draft_zh.md',
 'advisor/index.html','github/README_draft_20261106b.md','pages_20261106b/methods_addendum/index.html','talk_docs/progress_report_for_advisor_zh.html']
cjk=re.compile(r'[一-鿿]')
for f in files:
    p=R+f; t=open(p,encoding='utf-8').read()
    def rep(m):
        ctx=t[max(0,m.start()-60):m.end()+60]
        return 'D14-1（草稿，待确认）' if cjk.search(ctx) else 'D14-1 (draft, pending confirmation)'
    new,n=re.subn(r'D14-1(?!（草稿| \(draft)',rep,t)
    if n:
        b=p+'.before_20261108_d14pending'
        assert not os.path.exists(b); shutil.copy2(p,b)
        if f.endswith('.json'):
            import json; json.loads(new)
        open(p,'w',encoding='utf-8').write(new)
    print(f,n)
