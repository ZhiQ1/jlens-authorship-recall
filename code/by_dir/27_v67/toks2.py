import os, json, pandas as pd
os.environ['HF_HOME']='/scratch/zhang.zhiqi2/hf'; os.environ['HF_HUB_OFFLINE']='1'
from transformers import AutoTokenizer
tk=AutoTokenizer.from_pretrained('Qwen/Qwen3-32B')
P=pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/papers.parquet',columns=['paper_id','title','year']).set_index('paper_id')
V=pd.read_parquet('/scratch/zhang.zhiqi2/jlens/391_groups/raw/a24_freeze/variants.parquet')
pid='048bf6d3555b8a3ef942e43a9f14a222c3a009fd'
orig=P.loc[pid,'title']; print(orig, P.loc[pid,'year'])
d=json.load(open('toks.json'))
d['rare_orig']=[tk.decode([i]) for i in tk(orig)['input_ids']]
for v in 'ab':
    t=V[(V.paper_id==pid)&(V.variant==v)].title.iloc[0]; d['rare_'+v]=[tk.decode([i]) for i in tk(t)['input_ids']]
d['authors_y']=[tk.decode([i]) for i in tk('Who are the authors of the paper titled "Affect dynamics, bereavement and resilience to loss" (2007)?\nAuthors:')['input_ids']]
json.dump(d,open('toks.json','w'),ensure_ascii=False,indent=0)
for k in ['rare_orig','rare_a','rare_b','authors_y']: print(k,d[k])
