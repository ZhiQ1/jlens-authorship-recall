# 2026-11-08 user decisions before the batch publish:
# (1) D14-1 locked -> drop "pending" tags, point to config/prereg_addendum14_deviations.json
# (2) D13-1 NOT published this batch -> remove D13-1 text from report/deck notes/handbook (advisor untouched: already online);
#     removed snippets saved to sync_20261108b_D13-1_held.json for re-application next batch
# (3) delete the P1/P2 "187/194" progress clause everywhere
import re, json, os, shutil
R='/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
BK='.before_20261108b'
held=[]; log=[]
def load(f): return open(R+f,encoding='utf-8').read()
def save(f,t,orig):
    if t==orig: return
    p=R+f; b=p+BK; assert not os.path.exists(b),b; shutil.copy2(p,b)
    if f.endswith('.json'): json.loads(t)
    open(p,'w',encoding='utf-8').write(t)
def rep(t,f,old,new,cnt=None,regex=False,hold=False):
    ms=list(re.finditer(old if regex else re.escape(old),t,flags=re.S))
    if cnt is not None: assert len(ms)==cnt,(f,old[:60],len(ms))
    for m in ms:
        if hold: held.append({'file':f,'removed':m.group(0),'replacement':new})
    log.append((f,old[:50],len(ms)))
    return (re.sub if regex else (lambda a,b,c,flags=0:c.replace(old,new)))(old,new,t,flags=re.S) if regex else t.replace(old,new)
D14=['stage1_11/stage1_11_report.html','merged_deck/stage1_11_deck.html','talk/src/export/notes_zh.json','talk/src/export/with_notes.html',
 'methods/methods_handbook.html','methods/parts/B_global2.html','methods/parts/K_post_defence.html','process_report/index.html','process_report/draft_zh.md',
 'advisor/index.html','github/README_draft_20261106b.md','pages_20261106b/methods_addendum/index.html','talk_docs/progress_report_for_advisor_zh.html',
 '../../audit_20261105/scoring_audit.html','methods/parts/G_appendix.html','methods/parts/C_stage1_9.html']
for f in D14:
    t0=t=load(f)
    # (1) D14-1
    t=t.replace('D14-1（草稿，待确认）','D14-1').replace('D14-1 (draft, pending confirmation)','D14-1')
    t=t.replace('381_stage13/b3_33_v2/prereg_addendum14_deviations_DRAFT.json','381_stage13/config/prereg_addendum14_deviations.json')
    # (3) 187/194
    for old,new in [('194 个计算单元已完成 187 个，结果尚未出来；',''),('194 个单元已完成 187 个，结果尚未出来，',''),
                    ('（194 个单元已完成 187 个，结果尚未出来）',''),(' — 187 / 194 units done, result pending; result after approval',' — result after approval'),
                    (' (187 / 194 units done, result pending)',''),('running (187 / 194 units, result pending)','running')]:
        if old in t: log.append((f,old,t.count(old))); t=t.replace(old,new)
    # (2) D13-1 (not in advisor)
    if f!='advisor/index.html':
        if f in ('stage1_11/stage1_11_report.html','methods/methods_handbook.html'):
            pass
        for old,new,rx in [
            ('（用户 2026-11-06 决定，偏离 D13-1，见下框）','（用户 2026-11-06 决定）',False),
            (r'\n<div class="bx warn"><b>偏离 D13-1（补充 13 C-2 的规则触发）</b>.*?</div>','',True),
            (r'<li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做，列为偏离 D13-1：.*?</li>',
             '<li><b>不做：</b>Stage 8 在 GPU 上按原 W 统计量重算（补充 13 规则触发，用户 2026-11-06 决定不做；CPU 代理见 Stage 8 节）。</li>',True),
            (r'<li><b>Stage 8 L56 的 RQ2 没有用原统计量复核。</b>[^<]*?（偏离 D13-1，见 Stage 8 节）。</li>\n','',True),
            (r'<tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）= 偏离 D13-1</td>.*?</tr>',
             '<tr><td>V59</td><td>Stage 8 按原 W 统计量的 GPU 重算（补充 13 C-2 的规则触发）</td><td><span class="st st-plan">不做</span></td><td>用户 2026-11-06 决定不做；只报 CPU 代理（public J-lens 名次指标，不是 W）。<span class="src">381_stage13/reports/c13_C2.md “Decision for batch 3 item 3-4”</span></td><td><a href="#s19-s8d">s19-s8d</a></td></tr>',True),
            (r'<tr><td>D13-1（补充 13 C-2）</td>.*?</tr>\n?','',True),
            ('（用户 2026-11-06 决定，偏离 D13-1，见附录 V59）','（用户 2026-11-06 决定）',False),
            (r'Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1〔[^〕]*〕）。','',True),
            (r'Stage 8 RQ2 在 L56 的结论没有用原统计量复核（偏离 D13-1<span class="src">[^<]*</span>）。','',True),
            ]:
            pat=old if rx else re.escape(old)
            for m in re.finditer(pat,t,flags=re.S): held.append({'file':f,'removed':m.group(0),'replacement':new})
            n=len(re.findall(pat,t,flags=re.S))
            if n: log.append((f,'D13:'+old[:40],n)); t=re.sub(pat,lambda m:new,t,flags=re.S)
    save(f,t,t0)
    left=[k for k in ['D13-1','187 个','187 /','待确认）','pending confirmation','DRAFT.json'] if k in t and not (k=='D13-1' and f=='advisor/index.html')]
    print(f, 'LEFT:',left)
for l in log: print(l)
json.dump(held,open(R+'sync_20261108b_D13-1_held.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('held',len(held))
