import pyarrow.parquet as pq, hashlib, random, re, json, sys
src='/scratch/zhang.zhiqi2/jlens/fitting_corpus/source/wikitext-103-raw-v1/'
lines=[]
for f in ['train-00000-of-00002.parquet','train-00001-of-00002.parquet']:
    lines+=pq.read_table(src+f,columns=['text']).column(0).to_pylist()
def canon(s): return ' '.join(s.split()).strip()
got={h:[json.loads(l)['text_sha256'] for l in open(f'/scratch/zhang.zhiqi2/jlens/351_stage9/prompts/{h}.jsonl')] for h in ['fit_A','fit_B','holdout']}
for mn,mx in [(100,1200),(100,1196),(64,2000),(100,2000)]:
    u={}
    for line in lines:
        s=canon(line)
        if len(s)<mn or len(s)>mx or re.match(r'^=+ .* =+$',s): continue
        u.setdefault(hashlib.sha256(s.encode()).hexdigest(),s)
    keys=sorted(u); random.Random(int(sys.argv[1])).shuffle(keys)
    sel=keys[:300]
    print(mn,mx,'unique',len(u),'fit_A match',sel[:100]==got['fit_A'],'fit_B',sel[100:200]==got['fit_B'],'holdout',sel[200:]==got['holdout'])
