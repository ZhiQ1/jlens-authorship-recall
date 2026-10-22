#!/usr/bin/env python3
"""3.5.1: non-destructive all-paper four-group cohort preparation."""
import argparse,csv,json,collections,hashlib
from pathlib import Path

def main():
 p=argparse.ArgumentParser(); p.add_argument('--labels',required=True);p.add_argument('--outdir',required=True);a=p.parse_args()
 src=Path(a.labels); out=Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
 with src.open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
 if not rows: raise SystemExit('Empty CSV')
 needed=['paper_id','title','year','authors','n_authors','field','citation_bin','recall_level','group_tight','hr2','m']
 assert all(x in rows[0] for x in needed), 'Missing columns'
 ids=[r['paper_id'] for r in rows];assert len(ids)==len(set(ids)), 'Duplicate IDs'
 mapped=[]; counts=collections.Counter(); per_bin=collections.defaultdict(collections.Counter)
 for r in rows:
  g=r['group_tight'];level=r['recall_level']; hr=float(r['hr2']);m=int(r['m'])
  group= ('A' if level=='R0' else 'C') if g=='target' else (('B' if level=='R0' else 'D') if g=='control' else 'excluded')
  if group!='excluded':
   assert level in ('R0','R1') and hr>0.5 and ((level=='R0')==(m==0)),(r['paper_id'],level,m,hr)
  x=dict(r);x['group_351']=group;x['recognition_351']='pass' if group in ('A','C') else ('fail' if group in ('B','D') else 'other');mapped.append(x)
  counts[group]+=1;per_bin[r['citation_bin']][group]+=1
 fields=list(mapped[0]);
 with (out/'351_all_papers.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(mapped)
 included=[r for r in mapped if r['group_351']!='excluded']
 with (out/'351_four_groups.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(included)
 with (out/'351_four_groups.jsonl').open('w',encoding='utf-8') as f:
  for r in included: f.write(json.dumps(r,ensure_ascii=False)+'\n')
 order=['0-2','3-4','5-8','9-16','17-32','33-64','65-128','129-256','257-512','513-1024','1025-2048','2049-4096','4097+']
 with (out/'351_bin_counts.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.writer(f);w.writerow(['citation_bin','A','B','C','D','known_total','unknown_total','AB_max_pairs','CD_max_pairs'])
  for b in sorted(per_bin,key=lambda b:order.index(b) if b in order else 100):
   c=per_bin[b];w.writerow([b,*[c[x] for x in 'ABCD'],c['A']+c['C'],c['B']+c['D'],min(c['A'],c['B']),min(c['C'],c['D'])])
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 summary={'source':str(src),'source_sha256':digest,'total':len(rows),'four_group_total':len(included),'group_counts':dict(counts),'notes':'No split, no matching, no GPU analysis, no J-Lens metrics; candidates only.'}
 (out/'351_audit.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(summary,indent=2,ensure_ascii=False));print('FILES:',*[str(x) for x in sorted(out.glob('351_*'))],sep='\n  ')
if __name__=='__main__':main()
