import json,re,sys
T='/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/'
for f in sys.argv[1:]:
  for e in json.load(open(T+f)):
    n=e['new']
    for m in re.finditer(r'<span class="src">(.*?)</span>',n):
        pre=re.sub(r'<[^>]+>','',re.sub(r'<span class="src">.*?</span>','',n[max(0,m.start()-200):m.start()]))
        print('*',pre[-70:].replace('\n',' '),'=>',m.group(1)[:260])
