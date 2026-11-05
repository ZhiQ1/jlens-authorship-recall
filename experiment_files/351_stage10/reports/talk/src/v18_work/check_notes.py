import json, re, os, sys
D=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,D); import notes_spec as S
o=json.load(open(D+'/notes_v17_readonly.json',encoding='utf-8')); n=json.load(open(D+'/notes_v18_tagged.json',encoding='utf-8'))
assert list(o)==list(n); bad=0; tags=0; missing_paths=set()
for k in o:
    assert n[k]['new']==o[k]['new'] and set(n[k])==set(o[k])
    t=n[k]['text']; tags+=t.count('〔'); assert t.count('〔')==t.count('〕')
    stripped=re.sub('〔[^〔〕]*〕','',t)
    exp=o[k]['text']
    for a,b in S.FIXES.get(k,[]): exp=exp.replace(a,b)
    if k in S.CAVEAT_NOTES: exp+=S.CAVEAT
    if stripped!=exp: bad+=1; print('MISMATCH',k)
    for p in re.findall(r'(?:\d{3}_[A-Za-z0-9_]+|labels_20261015)/[A-Za-z0-9_./\-*]+',t):
        p=p.rstrip('.').split('*')[0]
        if not os.path.exists('/scratch/zhang.zhiqi2/jlens/'+p) and not p.endswith('/'): missing_paths.add(p)
print('notes',len(o),'tags',tags,'mismatches',bad); print('paths not found:',sorted(missing_paths))
