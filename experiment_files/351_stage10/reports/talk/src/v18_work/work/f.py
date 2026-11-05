import json,glob,sys,re
T='/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/'
segs=[]
for f in sorted(glob.glob(T+'S*.json')):
    for e in json.load(open(f)):
        n=e['new']
        for m in re.finditer(r'<span class="src">(.*?)</span>',n):
            pre=re.sub(r'<span class="src">.*?</span>','',n[max(0,m.start()-160):m.start()])
            segs.append((f.split('/')[-1],pre,m.group(1)))
for q in sys.argv[1:]:
    print('#####',q)
    for f,p,s in segs:
        if q in p[-100:]: print(f,'|',p[-100:].replace('\n',' '),'\n   >>',s[:400])
