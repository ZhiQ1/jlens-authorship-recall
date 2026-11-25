"""Proxy for H5: share of 'authors first, then title' vs 'title first' in raw citation strings.
Source: Crossref REST API (metadata CC0), random samples of works with references (sample=100 per call, 100 calls),
only the 'unstructured' reference strings are used (structured refs carry no order). Generic User-Agent, no email.
Raw JSON per call in OUT/raw/call_XXX.json (resumable). Proxy only: Qwen3's training data is not public.
Rules (applied to the stripped string, leading list markers like '[12]' / '12.' removed):
  NAME token  = initials (e.g. 'J', 'J.', 'J.-P.') or a capitalised surname word (Abc, O'Neil, van der X handled loosely)
  AUTHORS_FIRST: the string starts with an author block = 1+ name units 'Surname, I.' | 'I. Surname' | 'Surname I'
                 separated by , ; & and, optionally 'et al.' (regex AUTH below), followed by a year '(1998)' or
                 punctuation, then non-name text (title or venue).
  TITLE_FIRST:   the string starts with a quoted span, or its first sentence (up to the first '.') has >= 4 words,
                 contains >= 1 lowercase function word (of, the, and, in, for, on, a, an, with, to) and no initials,
                 AND a name unit appears later in the string.
  OTHER:         everything else (e.g. URLs, bare venue/patent strings, non-Latin).
  Sub-label for AUTHORS_FIRST: with_title if the remainder has a >= 4-word segment containing a lowercase word,
                 else no_title (name + journal + volume only, common in physics/biology).
v2 (2026-11-22, after audit of v1): initials may be 1–2 letters with optional spaces ('P. L.', 'V. Yu.'),
surnames may start with a non-ASCII capital, ', and' / ', &' separators, and a final initial's period may be consumed
(rest then starts with a capitalised word). v1 kept as crossref_refs_v1.py / counts_v1.json.
Outputs: counts.json, audit_50.csv (random 50 strings with labels, seed 30, for hand checking)."""
import json, random, re, sys, time, urllib.request
from pathlib import Path
OUT = Path('/scratch/zhang.zhiqi2/jlens/ext/citecorpus_20261122'); RAW = OUT / 'raw'; RAW.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'research-client/1.0'}
INIT = r"(?:[A-ZÀ-Þ][a-z]?\.?(?![a-zà-ÿ])-?\s?){1,4}"
SUR = r"(?:(?:van|von|de|der|da|di|du|la|le|del|dos)\s+)*[A-ZÀ-Þ][\w'’\-]+"
UNIT = rf"(?:{SUR},?\s+{INIT}|{INIT}\s+{SUR}|{SUR}\s+{INIT})"
AUTH = re.compile(rf"^(?:{UNIT})(?:\s*(?:,\s*and|,\s*&|,|;|&|and)\s*(?:{UNIT}))*(?:,?\s*et\s+al\.?)?")
FUNC = re.compile(r"\b(of|the|and|in|for|on|a|an|with|to|from|by|using|via)\b")
def fetch(n=100):
    for k in range(n):
        f = RAW / f'call_{k:03d}.json'
        if f.exists(): continue
        url = 'https://api.crossref.org/works?sample=100&filter=has-references:true&select=DOI,reference'
        for t in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: f.write_bytes(r.read()); break
            except Exception: time.sleep(2 ** t)
        time.sleep(1.0)
def clean(s): return re.sub(r"^\s*(\[\d+\]|\d+\.|\(\d+\))\s*", "", s.strip())
def label(s):
    s = clean(s)
    m = AUTH.match(s)
    if m and m.end() >= 3:
        rest = s[m.end():]
        if re.match(r"^\s*(\(|,|\.|:|\d)", rest) or rest.strip() == '' or (s[m.end()-1:m.end()] in '. ' and re.match(r'^\s*[A-Z]', rest)):
            segs = [x for x in re.split(r"[.:]", rest) if len(x.split()) >= 4 and FUNC.search(x)]
            return 'authors_first', ('with_title' if segs else 'no_title')
    if re.match(r"^[\"“‘']", s): return 'title_first', 'quoted'
    first = s.split('.')[0]
    if len(first.split()) >= 4 and FUNC.search(first) and not re.search(r"\b[A-Z]\.", first) and re.search(UNIT, s[len(first):]):
        return 'title_first', 'sentence'
    return 'other', ''
def count():
    refs = []
    for f in sorted(RAW.glob('call_*.json')):
        try: d = json.loads(f.read_text())
        except Exception: continue
        for w in d['message']['items']:
            for r in w.get('reference') or []:
                if r.get('unstructured'): refs.append((w['DOI'], r['unstructured']))
    refs = list(dict.fromkeys(refs))
    L = [(doi, s, *label(s)) for doi, s in refs]
    from collections import Counter
    c = Counter(x[2] for x in L); cs = Counter((x[2], x[3]) for x in L)
    n = len(L); cw = len({x[0] for x in L})
    res = dict(n_strings=n, n_citing_works=cw, shares={k: v / n for k, v in c.items()}, counts=dict(c),
               sub={f'{a}|{b}': v for (a, b), v in cs.items()},
               authors_vs_title_first=c['authors_first'] / max(1, c['authors_first'] + c['title_first']),
               note='proxy only; Crossref unstructured reference strings; Qwen3 training data not public')
    (OUT / 'counts.json').write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))
    random.seed(30); aud = random.sample(L, 50)
    import csv
    with open(OUT / 'audit_50.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['label', 'sub', 'string', 'citing_doi', 'hand_check'])
        for doi, s, a, b in aud: w.writerow([a, b, s, doi, ''])
if __name__ == '__main__':
    {'fetch': fetch, 'count': count}[sys.argv[1]]()
