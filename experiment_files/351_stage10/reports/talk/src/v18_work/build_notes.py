import json, sys, os
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D)
import notes_spec as S
orig=json.load(open(D+'/notes_v17_readonly.json',encoding='utf-8'))
out={}; errs=[]; ntags=0
for k,v in orig.items():
    t=v['text']
    for a,b in S.FIXES.get(k,[]):
        assert t.count(a)==1,(k,a); t=t.replace(a,b)
    cur=0
    for a,tag in S.TAGS.get(k,[]):
        i=t.find(a,cur)
        if i<0: errs.append((k,a)); continue
        e=i+len(a); ins='〔'+tag+'〕'; t=t[:e]+ins+t[e:]; cur=e+len(ins); ntags+=1
    if k in S.CAVEAT_NOTES: t=t+S.CAVEAT
    out[k]=dict(v); out[k]['text']=t
json.dump(out,open(D+'/notes_v18_tagged.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('tags',ntags,'errors',errs)
