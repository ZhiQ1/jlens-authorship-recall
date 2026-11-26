import os, json
os.environ['HF_HOME']='/scratch/zhang.zhiqi2/hf'; os.environ['HF_HUB_OFFLINE']='1'
from transformers import AutoTokenizer
tk=AutoTokenizer.from_pretrained('Qwen/Qwen3-32B')
d=json.load(open('toks.json'))
d['fict_y']=[tk.decode([i]) for i in tk('Who are the authors of the paper titled "Emotional change, grief and coping after loss" (2007)?\nAuthors:')['input_ids']]
json.dump(d,open('toks.json','w'),ensure_ascii=False,indent=0); print(d['fict_y'])
