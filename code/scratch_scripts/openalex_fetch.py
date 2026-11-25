"""Fetch OpenAlex authorships (institutions, countries) for the 9,108 cohort papers by title+year search.
No DOIs in the cohort (paper_id = Semantic Scholar sha; S2 batch API rate-limited without key), so: OpenAlex
/works?filter=title.search:<title>,publication_year:<y-1>-<y+1>&select=... ; best hit accepted if normalised-title
similarity >= 0.90 AND (first-author surname matches OR title similarity >= 0.97). Generic User-Agent, no email.
Resumable: raw JSON per paper in OUT/raw/<paper_id>.json (skip if exists). Then 'build' writes authorships.parquet."""
import json, os, re, sys, time, difflib, urllib.parse, urllib.request
from pathlib import Path
OUT = Path('/scratch/zhang.zhiqi2/jlens/ext/openalex_20261122'); RAW = OUT / 'raw'; RAW.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'research-client/1.0'}
SEL = 'id,doi,title,publication_year,authorships'
def norm(t): return re.sub(r'[^a-z0-9 ]', ' ', (t or '').lower()).split()
def sim(a, b): return difflib.SequenceMatcher(None, ' '.join(norm(a)), ' '.join(norm(b))).ratio()
def get(url):
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return json.load(r)
        except Exception as e:
            time.sleep(2 ** k)
    return None
def fetch(lim=None):
    import pandas as pd
    P = pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/papers.parquet', columns=['paper_id', 'title', 'year'])
    n = 0
    for r in P.itertuples():
        f = RAW / f'{r.paper_id}.json'
        if f.exists(): continue
        q = ' '.join(norm(r.title))[:300].replace(',', ' ')
        y = int(r.year) if r.year == r.year else None
        flt = f'title.search:{q}' + (f',publication_year:{y-1}-{y+1}' if y else '')
        url = 'https://api.openalex.org/works?' + urllib.parse.urlencode({'filter': flt, 'select': SEL, 'per-page': 5})
        d = get(url)
        f.write_text(json.dumps({'query': url, 'resp': d}))
        n += 1; time.sleep(0.15)
        if lim and n >= lim: break
        if n % 500 == 0: print(n, flush=True)
    print('fetched', n)
def build():
    import pandas as pd
    P = pd.read_parquet('/scratch/zhang.zhiqi2/jlens/351_stage10/cohort/papers.parquet', columns=['paper_id', 'title', 'year', 'authors', 'group_tight'])
    rows, meta = [], []
    for r in P.itertuples():
        f = RAW / f'{r.paper_id}.json'
        if not f.exists(): meta.append(dict(paper_id=r.paper_id, status='not_fetched')); continue
        d = json.loads(f.read_text())['resp']
        res = (d or {}).get('results') or []
        auth = r.authors if isinstance(r.authors, (list, tuple)) else (list(r.authors) if hasattr(r.authors, '__iter__') and not isinstance(r.authors, str) else str(r.authors).split(','))
        fa = norm(str(auth[0]))[-1:] if len(auth) else []
        best, bs = None, 0
        for w in res:
            s = sim(r.title, w.get('title'))
            fa_oa = norm(((w.get('authorships') or [{}])[0].get('author') or {}).get('display_name'))[-1:] if w.get('authorships') else []
            ok = s >= 0.97 or (s >= 0.90 and fa and fa == fa_oa)
            if ok and s > bs: best, bs = w, s
        if best is None: meta.append(dict(paper_id=r.paper_id, status='no_match' if res else 'no_result', n_hits=len(res))); continue
        meta.append(dict(paper_id=r.paper_id, status='matched', title_sim=bs, openalex_id=best['id'], doi=best.get('doi')))
        for i, a in enumerate(best.get('authorships') or []):
            insts = a.get('institutions') or []
            rows.append(dict(paper_id=r.paper_id, openalex_work=best['id'], author_position=i,
                             author_name=(a.get('author') or {}).get('display_name'), openalex_author=(a.get('author') or {}).get('id'),
                             institution_ids=[x.get('id') for x in insts], institution_names=[x.get('display_name') for x in insts],
                             institution_countries=[x.get('country_code') for x in insts], institution_types=[x.get('type') for x in insts],
                             countries=a.get('countries') or []))
    A = pd.DataFrame(rows); M = pd.DataFrame(meta).merge(P[['paper_id', 'group_tight']], on='paper_id', how='left')
    A.to_parquet(OUT / 'authorships.parquet'); M.to_parquet(OUT / 'match_meta.parquet')
    A['has_inst'] = A.institution_ids.map(len) > 0; A['has_cty'] = A.apply(lambda x: len([c for c in list(x.institution_countries) + list(x.countries) if c]) > 0, axis=1)
    A = A.merge(P[['paper_id', 'group_tight']], on='paper_id', how='left')
    cov = {'papers': len(P), 'matched': int((M.status == 'matched').sum()), 'status': M.status.value_counts().to_dict(),
           'matched_by_group': M[M.status == 'matched'].group_tight.value_counts().to_dict(), 'group_sizes': P.group_tight.value_counts().to_dict(),
           'authorships': len(A), 'with_institution': float(A.has_inst.mean()) if len(A) else None, 'with_country': float(A.has_cty.mean()) if len(A) else None,
           'by_group': {g: dict(n=int(len(x)), inst=float(x.has_inst.mean()), country=float(x.has_cty.mean())) for g, x in A.groupby('group_tight')},
           'with_doi': int(M.doi.notna().sum()) if 'doi' in M else 0}
    (OUT / 'coverage.json').write_text(json.dumps(cov, indent=1, default=str)); print(json.dumps(cov, indent=1, default=str))
if __name__ == '__main__':
    {'fetch': lambda: fetch(int(sys.argv[2]) if len(sys.argv) > 2 else None), 'build': build}[sys.argv[1]]()
