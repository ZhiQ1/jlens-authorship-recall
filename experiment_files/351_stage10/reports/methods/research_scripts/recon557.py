import pyarrow.parquet as pq, hashlib, json, pandas as pd, re
src='/scratch/zhang.zhiqi2/jlens/fitting_corpus/source/wikitext-103-raw-v1/'
N=557; maxc=2000; prompts=[]; buf=''
def gen():
    for f in ['train-00000-of-00002.parquet','train-00001-of-00002.parquet']:
        for b in pq.ParquetFile(src+f).iter_batches(batch_size=4096,columns=['text']):
            yield from b.column(0).to_pylist()
for t in gen():
    t=str(t or '').strip()
    if not t or t.startswith('='): continue
    buf+=' '+t
    while len(buf)>maxc:
        prompts.append(buf[:maxc].strip()); buf=buf[maxc:]
        if len(prompts)>=N: break
    if len(prompts)>=N: break
print('n',len(prompts),'chars',sum(map(len,prompts)))
print('sha256(json)',hashlib.sha256(json.dumps(prompts).encode()).hexdigest())
print('first60',prompts[0][:60]); print('last60',prompts[-1][:60])
json.dump(prompts,open('/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/public557_prompts_reconstructed.json','w'))
P=pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/papers.parquet',columns=['paper_id','title','authors'])
big=' '.join(prompts).lower()
hits=[t for t in P.title if len(t)>=25 and t.lower() in big]
print('cohort titles (>=25 chars) found verbatim in 557 prompts:',len(hits), hits[:5])
