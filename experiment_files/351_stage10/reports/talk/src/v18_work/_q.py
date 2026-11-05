import sys,re
L=open('/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/deck/_tagindex.txt').read().splitlines()
mx=int(sys.argv[1]); 
for p in sys.argv[2:]:
    print('####',p); n=0
    for l in L:
        i=l.find(p)
        while i>=0 and n<mx:
            j=l.find('〔',i); k=l.find('〕',j)
            if j>=0 and j-i<120:
                print('  ',l.split(']')[0]+']', l[max(0,i-50):i+len(p)].replace('\n',' '),'=>',l[j:k+1][:400]); n+=1
            i=l.find(p,i+1)
