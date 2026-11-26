import os, json
os.environ['HF_HOME']='/scratch/zhang.zhiqi2/hf'; os.environ['HF_HUB_OFFLINE']='1'
from transformers import AutoTokenizer
tk=AutoTokenizer.from_pretrained('Qwen/Qwen3-32B')
T='Affect dynamics, bereavement and resilience to loss'
P={'authors':f'Who are the authors of the paper titled "{T}"?\nAuthors:',
   'year':f'In what year was the research paper titled "{T}" published?\nYear:',
   'field':f'In what research field is the paper titled "{T}"?\nField:',
   'fict':'Who are the authors of the paper titled "Emotional change, grief and coping after loss"?\nAuthors:',
   'false0':'Who are the authors of the paper titled "Scholars, foreign policy and the state"?\nAuthors:',
   'ps':'Paper: X · The first author of the paper is'}
out={k:[tk.decode([i]) for i in tk(v)['input_ids']] for k,v in P.items()}
json.dump(out,open('toks.json','w'),ensure_ascii=False,indent=0)
for k,v in out.items(): print(k,len(v),v)
