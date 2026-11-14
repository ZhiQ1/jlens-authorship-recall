"""Addendum 16 (LOCKED 2026-11-14), items B (format lock) and D (name chain): freeze, precheck, runner, tiny test.

Plan: /scratch/zhang.zhiqi2/jlens/391_groups/config/prereg_addendum16.md, sha256 c78daad0... (checked at every start; never
edited). Frozen code is imported by path, never edited: 10_stage10/351_stage10_fix1.py (-> 351_stage10.py: PROMPT,
tokenizer, condition prompts, score(), fix-1 load_model), Stage 11 E3 chain joining (names tokenised as encode(' ' + name),
joined by the ',' token 11), Stage 10 R0/R1 matcher (10_stage10/stage10_extra_r0r1.py words/same/match: surname + first
initial, both orders, one-to-one; copied verbatim below and checked against the file at start).

Samples (freeze, CPU; one numpy default_rng(1114) stream consumed in this order: B sample A, B, C; D sample A, B, C;
B controls; D controls):
  groups     391_groups/papers_used.csv grp (A = R0 x MC strong, B = R0 x fail, C = R1 x strong; checked against
             papers.parquet recall_level / mc_team_outcome_tight).
  quotas     A 600, B 600, C 300; per citation bin n_b = quota x share of the bin in 361_stage11/config/sample.parquet
             (largest remainder, ties by ascending citation; bins absent from that sample get 0); a bin with too few papers:
             all of them, shortfall re-allocated proportionally over the other bins (rerun_gpu.allocate rule, copied).
             Within bin rng.choice without replacement, bins in pandas groupby order, candidates in papers.parquet order.
  D          same, candidates restricted to papers with >= 3 listed authors.
  controls   B: per sample paper (paper_id order) one control paper: same field, |n_authors - n| <= 1, not the paper itself,
             no shared author surname (words()[-1]); F4: same field, same normalised first initial of the first author, no
             shared surname; if none, any same-field paper without shared surname. D (P_other): the B rule (same field,
             +-1 authors, no shared surname). P_shuffle(2): rng.permutation(2) per D paper (stored); the swapped order [2,1]
             is always computed as well (see report: with k = 1 the shuffle is the identity).
  shards     sample sorted by paper_id, 50 papers per shard; team id (folds_own9108_k5s13 'team') stored for the bootstrap.

B runner, per paper (true title only for generation):
  generation F0..F4: Stage 10 plain prompt (no chat template, so no thinking block), '\\nAuthors:' replaced by the format
  suffix; greedy, max 80 new tokens, stop at the first newline after non-space output or at an EOS token; left-padded
  batches (WARN check: first 4 prompts of the shard regenerated one by one). Parse: split on ; , 'and' & (F1 without ';':
  consecutive items paired as 'surname, given'); F4: the forced 'K.' is prepended. Matching vs the true authors and vs
  the control paper's authors: full matcher (Stage 10) and surname-only matcher (true surname = words()[-1] equals the
  first or last word of a generated item; one-to-one).
  teacher forcing, 7 title conditions (true, false_0..4, deleted): every author alone after the format prompt (as Stage 10),
  all name tokens: F0 ' ' + name (Stage 10 token ids); F1 ' Surname, Given'; F2 ' Surname'; F3 first author ' Surname';
  F4 first author, tokens after the forced initial (' L. Smith' for 'Kevin L. Smith' -> 'K. L. Smith').
D runner, per paper, 7 title conditions, teacher forcing after 'Authors:' + prefix names joined by ',' (Stage 11 chain),
  then ',' + the scored author alone: P_true1/2, P_other1/2 (control paper's first 1/2 authors), P_none (all authors, = Stage
  10), P_shuffle2 (perm as drawn), P_shuffle2x (always [2,1]), P_reverse (prefix authors 2..n in list order, score author 1).
  Scored set k = 1: authors 2..n; k = 2: authors 3..n (prefix authors never scored). Generation check (true title): prefix
  true first author vs control first author, greedy rest, matched against authors 2..n.
Self-checks (WARN only, never stop): F0 and P_none ranks vs stored Stage 10 final L63 ranks (all 7 conditions), tolerance
  |d logprob| <= 1.0 nat (4 bf16 ulps at |logit| 32-64) and |d log10 rank| <= 0.1; batched vs single generation.
Outputs: 391_groups/raw/a16_{B,D}/{tf,gen}/shard_KKK.parquet + meta/shard_KKK.json (written last = done marker).
Commands: freeze | precheck | tiny --root DIR | work --item B|D --shards 0[,1..] [--max-minutes M] | remaining
"""
import argparse, hashlib, importlib.util, json, os, re, sys, time, unicodedata
from pathlib import Path
import numpy as np

H = Path.home() / 'jlens_work'; BASE = Path('/scratch/zhang.zhiqi2/jlens')
G = BASE / '391_groups'; CFG = G / 'config'; R10 = BASE / '351_stage10'; R11 = BASE / '361_stage11'
PREREG = CFG / 'prereg_addendum16.md'; PREREG_SHA = 'c78daad08f77080e7dd49c84c2501f9ca31b1195ab9e38364e3c3bab9243e66a'
CFG_OUT = Path(os.environ.get('A16_CFG', CFG))    # override only for a dry-run freeze test
SAMPLE = {'B': CFG_OUT / 'prereg16_sample_B.parquet', 'D': CFG_OUT / 'prereg16_sample_D.parquet'}
OUT = Path(os.environ.get('A16_OUT', G / 'raw'))
SEED, PER_SHARD, MAX_NEW = 1114, 50, 80
QUOTA = {'A': 600, 'B': 600, 'C': 300}
TITLE_CONDS = ['true'] + [f'false_{k}' for k in range(5)] + ['delete']
FMTS = ['F0', 'F1', 'F2', 'F3', 'F4']
SUFFIX = {'F0': '\nAuthors:', 'F1': '\nAuthors (surname, given name):', 'F2': '\nAuthor surnames:', 'F3': "\nFirst author's surname:",
          'F4': '\nAuthors: {K}.'}
DCONDS = ['P_true1', 'P_true2', 'P_other1', 'P_other2', 'P_none', 'P_shuffle2', 'P_shuffle2x', 'P_reverse']
COMMA = 11
EOS = (151643, 151645)
TOL_LP, TOL_NLR, TOL_SHARE = 1.0, 0.1, 0.95

_sp = importlib.util.spec_from_file_location('s10fix1_a16', H / '10_stage10/351_stage10_fix1.py')
_fix1 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_fix1); s10 = _fix1.s10


def log(*x): print(time.strftime('%Y-%m-%dT%H:%M:%S'), *x, flush=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_prereg():
    h = sha(PREREG)
    if h != PREREG_SHA: raise SystemExit(f'PREREG CHANGED {h}')
    return h


# ------------------------------------------------------------------ matcher (verbatim copy of stage10_extra_r0r1.py)
def words(s): return [x for x in re.sub(r'[^a-z \-]', ' ', unicodedata.normalize('NFKD', s.replace('-', ' - ')).encode('ascii', 'ignore').decode().lower()).split() if x != '-']


def same(tw, gw, swap):
    if not tw or len(gw) < 2: return False
    ts, ti = tw[-1], (tw[0][0] if len(tw) > 1 else '')
    for gs, gi in ([(gw[-1], gw[0][0]), (gw[0], gw[1][0])] if swap else [(gw[-1], gw[0][0])]):
        if gs == ts and (not ti or gi == ti): return True
    return False


def match(true, gen):
    """One-to-one: first pass given-name-first order, second pass surname-first order ("Sakaguchi Shimon", "Tounsi A")."""
    tw = [words(t) for t in true]; gw = [words(g) for g in gen]; used, hit = set(), [False] * len(true)
    for swap in (False, True):
        for i, t in enumerate(tw):
            if hit[i]: continue
            for j, g in enumerate(gw):
                if j not in used and same(t, g, swap): used.add(j); hit[i] = True; break
    return hit


def check_matcher_copy():
    src = (H / '10_stage10/stage10_extra_r0r1.py').read_text(); me = Path(__file__).read_text()
    for fn in ('def words(', 'def same(', 'def match('):
        a = src[src.index(fn):]; a = a[:a.index('\n\n\n')]; b = me[me.index(fn):]; b = b[:b.index('\n\n\n')]
        if a != b: raise SystemExit(f'matcher copy differs from stage10_extra_r0r1.py: {fn}')


def match_items(true, gen):
    """hit per true author + which generated items were used (full matcher, same passes as match())."""
    tw = [words(t) for t in true]; gw = [words(g) for g in gen]; used, hit = {}, [False] * len(true)
    for swap in (False, True):
        for i, t in enumerate(tw):
            if hit[i]: continue
            for j, g in enumerate(gw):
                if j not in used and same(t, g, swap): used[j] = i; hit[i] = True; break
    return hit, used


def match_surname(true, gen):
    """surname-only, one-to-one: true words()[-1] equals the last (first pass) or first (second pass) word of an item."""
    ts = [words(t)[-1] if words(t) else None for t in true]; gw = [words(g) for g in gen]; used, hit = {}, [False] * len(true)
    for pos in (-1, 0):
        for i, s in enumerate(ts):
            if hit[i] or s is None: continue
            for j, g in enumerate(gw):
                if j not in used and g and g[pos] == s: used[j] = i; hit[i] = True; break
    return hit, used


SENT_END = re.compile(r'(?<=[a-z]{2})\.(?=\s|$)')            # '.' after >= 2 lower-case letters = end of the list sentence
MARKER = re.compile(r'^\s*(?:[-*\u2022]|\d+[.)])\s*')


def list_text(full):
    """the answer list inside the generated text (v2 rule; generation is NOT stopped early, so this can be revised on CPU).
    Answer on the same line as the prompt: that line up to the first sentence end. Answer starting on a new line (vertical
    list, e.g. '\\n1. Smith, J.\\n2. ...'): consecutive non-empty lines up to the first blank line, list markers removed, each
    line cut at its sentence end, joined by '; '."""
    if not full.strip(): return ''
    first_nl = full.find('\n'); same_line = full[:first_nl if first_nl >= 0 else len(full)]
    if same_line.strip():
        m = SENT_END.search(same_line); return (same_line[:m.start()] if m else same_line).strip()
    out = []
    for ln in full.lstrip('\n').split('\n'):
        if not ln.strip(): break
        ln = MARKER.sub('', ln); m = SENT_END.search(ln); ln = (ln[:m.start()] if m else ln).strip()
        if ln: out.append(ln)
    return '; '.join(out)


def split_items(text, fmt):
    t = re.sub(r'\bet al\.?', ' ', text)
    if ';' in t: parts = re.split(r';|\band\b|&', t)
    elif fmt == 'F1':
        parts = [x.strip() for x in re.split(r',|\band\b|&', t) if x.strip()]
        parts = [' '.join(parts[i:i + 2]) for i in range(0, len(parts), 2)]
    else: parts = re.split(r',|\band\b|&', t)
    return [x.strip() for x in parts if x.strip() and words(x)]


# ------------------------------------------------------------------ name rendering
def surname(a): return a.split()[-1]
def given(a): return a.split()[:-1]
def first_initial(a):
    c = next((ch for ch in a if ch.isalpha()), 'X'); return c.upper()
def init_norm(a):
    w = words(a); return w[0][0] if w else ''
def render(a, fmt):
    if fmt == 'F0': return ' ' + a
    if fmt == 'F1': return ' ' + surname(a) + (', ' + ' '.join(given(a)) if given(a) else '')
    if fmt in ('F2', 'F3'): return ' ' + surname(a)
    if fmt == 'F4':                       # tokens after the forced first initial 'K.'
        g = given(a)
        if not g: return None
        rest = [w[0] + '.' for w in g[1:] if any(ch.isalpha() for ch in w)]
        return ' ' + ' '.join(rest + [surname(a)])


def authors_of(s): return [x.strip() for x in s.split(';') if x.strip()]


# ------------------------------------------------------------------ freeze (CPU)
def cite_lo(b): return int(str(b).split('-')[0].rstrip('+'))


def allocate(share, avail, n):
    """largest-remainder allocation of n over bins proportional to share, capped by avail (shortfall re-allocated).
    (verbatim logic of rerun_gpu.allocate)"""
    bins = sorted(share, key=cite_lo); alloc = {b: 0 for b in bins}; active = [b for b in bins]; left = n; notes = []
    while left > 0 and active:
        tot = sum(share[b] for b in active); q = {b: left * share[b] / tot for b in active}
        fl = {b: int(np.floor(q[b])) for b in active}; rem = left - sum(fl.values())
        order = sorted(active, key=lambda b: (-(q[b] - fl[b]), cite_lo(b)))
        for b in order[:rem]: fl[b] += 1
        capped = [b for b in active if alloc[b] + fl[b] > avail[b]]
        if not capped:
            for b in active: alloc[b] += fl[b]
            left = 0
        else:
            for b in capped: notes.append(f'bin {b}: only {avail[b]} papers, take all'); left -= avail[b] - alloc[b]; alloc[b] = avail[b]; active.remove(b)
    if left > 0: notes.append(f'all bins exhausted: {left} short of {n}')
    return alloc, notes


def cohort_table():
    import pandas as pd
    p = pd.read_parquet(R10 / 'cohort/papers.parquet')
    u = pd.read_csv(G / 'papers_used.csv')[['paper_id', 'grp']]
    p = p.merge(u, on='paper_id', how='left')
    r, o = p.recall_level, p.mc_team_outcome_tight
    chk = {'A': (r == 'R0') & (o == 'strong'), 'B': (r == 'R0') & (o == 'fail'), 'C': (r == 'R1') & (o == 'strong')}
    for g, m in chk.items():
        if not ((p.grp == g) == (m & p.grp.notna())).all(): raise SystemExit(f'group {g} definition mismatch')
    z = np.load(BASE / '381_stage13/summary_cpu_teamci/folds_own9108_k5s13.npz', allow_pickle=True)
    team = pd.Series(z['team'], index=z['ids'].astype(str))
    p['team'] = p.paper_id.map(team)
    if p.team.isna().any(): raise SystemExit('papers without team id')
    p['alist'] = p.authors.map(authors_of)
    p['surnames'] = p.alist.map(lambda L: {words(a)[-1] for a in L if words(a)})
    p['fa_init'] = p.alist.map(lambda L: init_norm(L[0]) if L else '')
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'token_index', 'role'])
    t0 = toks[(toks.author_index == 0) & (toks.token_index == 0)].set_index('paper_id').role
    p['fa_type'] = p.paper_id.map(t0).map(lambda r: 'initial_first' if r == 'initial_first' else ('given_first' if r == 'given_first' else 'other'))
    return p


def draw(p, rng, min_authors, rec, tag):
    import pandas as pd
    share = pd.read_parquet(R11 / 'config/sample.parquet').citation_bin.value_counts().to_dict()
    rows = []
    for g in ['A', 'B', 'C']:
        cand = p[(p.grp == g) & (p.n_authors_listed >= min_authors)]
        avail = {b: int((cand.citation_bin == b).sum()) for b in share}
        alloc, notes = allocate(share, avail, QUOTA[g])
        rec[f'{tag}_{g}'] = dict(alloc=alloc, notes=notes, n=int(sum(alloc.values())), quota=QUOTA[g],
                                 candidates_outside_stage11_bins=int((~cand.citation_bin.isin(list(share))).sum()))
        log(tag, g, alloc, notes)
        for b, gg in cand.groupby('citation_bin'):
            if b not in alloc: continue
            k = alloc[b]; pick = gg.iloc[rng.choice(len(gg), k, replace=False)] if k < len(gg) else gg
            rows += [dict(paper_id=x, grp=g) for x in pick.paper_id]
    s = pd.DataFrame(rows).sort_values('paper_id').reset_index(drop=True)
    s['shard'] = np.arange(len(s)) // PER_SHARD
    return s


def pick_control(p, row, rng, f4=False):
    """control paper id (and whether the F4 same-initial rule was met)."""
    same_field = (p.field == row.field) & (p.paper_id != row.paper_id) & p.surnames.map(lambda s: not (s & row.surnames))
    if f4:
        c = p[same_field & (p.fa_init == row.fa_init)]
        if len(c): return c.paper_id.iloc[rng.choice(len(c))], True
        c = p[same_field]; return c.paper_id.iloc[rng.choice(len(c))], False
    c = p[same_field & ((p.n_authors_listed - row.n_authors_listed).abs() <= 1)]
    if not len(c): raise SystemExit(f'no control for {row.paper_id}')
    return c.paper_id.iloc[rng.choice(len(c))], True


def freeze(a):
    import pandas as pd
    check_prereg()
    for f in SAMPLE.values():
        if f.exists(): raise SystemExit(f'{f} exists; refusing to overwrite')
    p = cohort_table(); rng = np.random.default_rng(SEED)
    rec = dict(created=time.strftime('%Y-%m-%dT%H:%M:%S'), script_sha256=sha(__file__), prereg_sha256=PREREG_SHA, seed=SEED,
               rng_order='B sample (A,B,C) -> D sample (A,B,C) -> B controls (per paper: ctrl, ctrl_f4) -> D controls (per paper: ctrl, perm)',
               stage11_sample_sha256=sha(R11 / 'config/sample.parquet'))
    sB = draw(p, rng, 1, rec, 'B'); sD = draw(p, rng, 3, rec, 'D')
    P = p.set_index('paper_id', drop=False)
    out = {}
    for item, s in (('B', sB), ('D', sD)):
        rows = []
        for r in s.itertuples():
            row = P.loc[r.paper_id]; c, _ = pick_control(p, row, rng)
            d = dict(paper_id=r.paper_id, grp=r.grp, shard=r.shard, citation_bin=row.citation_bin, field=row.field, year=row.year,
                     n_authors=int(row.n_authors_listed), team=str(row.team), fa_type=row.fa_type, ctrl_paper_id=c)
            if item == 'B':
                c4, ok = pick_control(p, row, rng, f4=True)
                d.update(ctrl_f4_paper_id=c4, ctrl_f4_same_initial=ok, first_initial=first_initial(row.alist[0]))
            else:
                d.update(shuffle2=json.dumps([int(x) for x in rng.permutation(2)]))
            rows.append(d)
        df = pd.DataFrame(rows); out[item] = df
    for item, df in out.items():
        f = SAMPLE[item]; df.to_parquet(f, index=False); h = sha(f); Path(str(f) + '.sha256').write_text(f'{h}  {f.name}\n'); os.chmod(f, 0o444)
        rec[item] = dict(n=len(df), shards=int(df.shard.max()) + 1, sha256=h, groups={k: int(v) for k, v in df.grp.value_counts().items()},
                         bins={str(k): int(v) for k, v in df.citation_bin.value_counts().items()})
        if item == 'B': rec[item]['f4_same_initial_share'] = float(df.ctrl_f4_same_initial.mean())
        log(item, json.dumps(rec[item]))
    (CFG_OUT / 'prereg16_freeze.json').write_text(json.dumps(rec, indent=1)); log('wrote', CFG_OUT / 'prereg16_freeze.json')


def load_sample(item, root=None):
    import pandas as pd
    f = (root / 'config' / SAMPLE[item].name) if root else SAMPLE[item]
    ref = Path(str(f) + '.sha256').read_text().split()[0]
    if sha(f) != ref: raise SystemExit(f'SAMPLE CHANGED {f}')
    return pd.read_parquet(f)


# ------------------------------------------------------------------ data context
class Data:
    def __init__(self, root=None):
        import pandas as pd
        self.tok = s10.tokenizer()
        self.papers = pd.read_parquet(R10 / 'cohort/papers.parquet').set_index('paper_id', drop=False)
        nt = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index', 'token_index', 'token_id'])
        self.nt = {}
        for (pid, ai), g in nt.sort_values(['paper_id', 'author_index', 'token_index']).groupby(['paper_id', 'author_index'], sort=False):
            self.nt.setdefault(pid, {})[int(ai)] = (g.token_id.tolist(), g.row_id.tolist())
        self.prompts = {c: s10.condition_prompts(R10, self.papers.reset_index(drop=True), c)[0] for c in TITLE_CONDS}
        self.written = pd.read_parquet(G / 'data/author_flags.parquet').set_index(['paper_id', 'author_index']).written.to_dict()
        self.root = root

    def authors(self, pid): return authors_of(self.papers.loc[pid, 'authors'])

    def prompt_ids(self, pid, cond, fmt, K=None):
        text, ids = self.prompts[cond][pid]
        if fmt == 'F0': return ids, text
        assert text.endswith('\nAuthors:')
        t2 = text[:-len('\nAuthors:')] + SUFFIX[fmt].format(K=K)
        return self.tok(t2).input_ids, t2

    def name_ids(self, pid, ai): return self.nt[pid][ai][0]


# ------------------------------------------------------------------ unit construction (CPU; shared by precheck and work)
def b_units(D, s):
    """teacher-forcing sequences and generation prompts for B sample rows s."""
    tf, gen = [], []
    for r in s.itertuples():
        A = D.authors(r.paper_id); K = r.first_initial
        for fmt in FMTS:
            ids, text = D.prompt_ids(r.paper_id, 'true', fmt, K)
            gen.append(dict(paper_id=r.paper_id, fmt=fmt, prompt=text, ids=ids))
        for cond in TITLE_CONDS:
            for fmt in FMTS:
                pids, _ = D.prompt_ids(r.paper_id, cond, fmt, K)
                who = range(len(A)) if fmt in ('F0', 'F1', 'F2') else [0]
                for ai in who:
                    if fmt == 'F0': name = D.name_ids(r.paper_id, ai); rend = ' ' + A[ai]
                    else:
                        rend = render(A[ai], fmt)
                        if rend is None: continue
                        name = D.tok(rend, add_special_tokens=False).input_ids
                    tf.append(dict(paper_id=r.paper_id, title_cond=cond, cond=fmt, author_index=ai, rendered=rend, prefix=pids, name=name))
    return tf, gen


def d_units(D, s):
    tf, gen = [], []
    for r in s.itertuples():
        pid = r.paper_id; A = D.authors(pid); n = len(A); cA = D.authors(r.ctrl_paper_id)
        nid = lambda ai: D.name_ids(pid, ai)
        cid = lambda ai: D.name_ids(r.ctrl_paper_id, ai)
        perm = json.loads(r.shuffle2)
        pre = {'P_true1': [nid(0)], 'P_true2': [nid(0), nid(1)], 'P_other1': [cid(0)], 'P_other2': [cid(0), cid(1)], 'P_none': [],
               'P_shuffle2': [nid(perm[0]), nid(perm[1])], 'P_shuffle2x': [nid(1), nid(0)], 'P_reverse': [nid(i) for i in range(1, n)]}
        lab = {'P_true1': '0', 'P_true2': '0,1', 'P_other1': 'ctrl:0', 'P_other2': 'ctrl:0,1', 'P_none': '', 'P_shuffle2': ','.join(map(str, perm)),
               'P_shuffle2x': '1,0', 'P_reverse': ','.join(map(str, range(1, n)))}
        scored = {'P_true1': range(1, n), 'P_true2': range(2, n), 'P_other1': range(1, n), 'P_other2': range(2, n), 'P_none': range(n),
                  'P_shuffle2': range(2, n), 'P_shuffle2x': range(2, n), 'P_reverse': [0]}
        for cond in TITLE_CONDS:
            pids = D.prompts[cond][pid][1]
            for c in DCONDS:
                prefix = list(pids)
                for i, nm in enumerate(pre[c]): prefix += nm + [COMMA]
                for ai in scored[c]:
                    tf.append(dict(paper_id=pid, title_cond=cond, cond=c, author_index=ai, prefix_authors=lab[c], prefix=prefix, name=nid(ai)))
        pids = D.prompts['true'][pid][1]
        gen.append(dict(paper_id=pid, fmt='G_true1', prompt=A[0], ids=list(pids) + nid(0) + [COMMA]))
        gen.append(dict(paper_id=pid, fmt='G_other1', prompt=cA[0], ids=list(pids) + cid(0) + [COMMA]))
    return tf, gen


def d_invariants(tf):
    """prefix authors never scored; P_true/P_other/P_none/P_shuffle scored sets identical per k."""
    import pandas as pd
    d = pd.DataFrame([dict(paper_id=u['paper_id'], title_cond=u['title_cond'], cond=u['cond'], ai=u['author_index'], pa=u['prefix_authors']) for u in tf])
    bad = d[d.apply(lambda r: (not r.pa.startswith('ctrl')) and r.pa != '' and str(r.ai) in r.pa.split(','), axis=1)]
    sets = d.groupby(['paper_id', 'title_cond', 'cond']).ai.apply(lambda v: tuple(sorted(v))).unstack()
    none2 = sets.P_none.map(lambda t: tuple(x for x in t if x >= 2)); none1 = sets.P_none.map(lambda t: tuple(x for x in t if x >= 1))
    ok1 = (sets.P_true1 == sets.P_other1).all() and (sets.P_true1 == none1).all()
    ok2 = all((sets[c] == sets.P_true2).all() for c in ['P_other2', 'P_shuffle2', 'P_shuffle2x']) and (sets.P_true2 == none2).all()
    return dict(prefix_scored_rows=int(len(bad)), scored_sets_identical_k1=bool(ok1), scored_sets_identical_k2=bool(ok2),
                reverse_scores_only_first=bool((d[d.cond == 'P_reverse'].ai == 0).all()))


# ------------------------------------------------------------------ GPU (or tiny CPU) side
def load_model(tiny=False):
    import torch, transformers, jlens
    if tiny:   # = stage13_alltok_gpu.tiny_model (64-layer random Qwen3, bf16, seed 0), real tokenizer
        cfg = transformers.AutoConfig.from_pretrained(s10.MODEL, revision=s10.REV)
        cfg.hidden_size = 64; cfg.intermediate_size = 128; cfg.num_attention_heads = 4; cfg.num_key_value_heads = 2; cfg.head_dim = 16
        torch.manual_seed(0); hf = transformers.AutoModelForCausalLM.from_config(cfg, dtype=torch.bfloat16).eval()
        tok = s10.tokenizer(); return hf, jlens.from_hf(hf, tok), tok
    model, tok = s10.load_model()                     # fix-1 loader (prefetch, single GPU, no offload)
    return model._hf_model, model, tok


def tf_run(model, units, torch, max_tokens=12000, max_seqs=96, chunk=512):
    """batched teacher forcing (right padding, causal => scored positions unaffected); final L63 logits as Stage 10
    fast_readout (ActivationRecorder at the last block, model.unembed(h.float())). Adds rank/ties/logprob/top1 per token."""
    from jlens.hooks import ActivationRecorder
    LAST = model.n_layers - 1
    order = sorted(range(len(units)), key=lambda i: len(units[i]['prefix']) + len(units[i]['name']))
    batches, cur, cur_len = [], [], 0
    for i in order:
        L = len(units[i]['prefix']) + len(units[i]['name']) - 1
        if cur and (max(cur_len, L) * (len(cur) + 1) > max_tokens or len(cur) >= max_seqs): batches.append(cur); cur, cur_len = [], 0
        cur.append(i); cur_len = max(cur_len, L)
    if cur: batches.append(cur)
    for b in batches:
        seqs = [units[i]['prefix'] + units[i]['name'][:-1] for i in b]; T = max(len(x) for x in seqs)
        x = torch.zeros(len(b), T, dtype=torch.long)
        for j, sq in enumerate(seqs): x[j, :len(sq)] = torch.tensor(sq)
        bi, pi, gold = [], [], []
        for j, i in enumerate(b):
            u = units[i]; P0 = len(u['prefix'])
            for t in range(len(u['name'])): bi.append(j); pi.append(P0 - 1 + t); gold.append(u['name'][t])
        with torch.inference_mode():
            with ActivationRecorder(model.layers, at=[LAST]) as rec:
                model.forward(x.to(model.input_device))
                act = rec.activations[LAST].detach()
            h = act[torch.tensor(bi, device=act.device), torch.tensor(pi, device=act.device)]
            res = [[], [], [], []]
            for c0 in range(0, len(bi), chunk):
                lg = model.unembed(h[c0:c0 + chunk].float()).float()
                for r_, v in zip(res, s10.score(lg, torch.tensor(gold[c0:c0 + chunk]), torch)): r_.append(v)
        res = [np.concatenate(v) for v in res]; k = 0
        for j, i in enumerate(b):
            n = len(units[i]['name']); units[i]['rank'], units[i]['ties'], units[i]['logprob'], units[i]['top1'] = (v[k:k + n] for v in res); k += n
    return len(batches)


class NLStop:
    """per row: stop after the first newline that follows non-space output, or at EOS (handled by generate)."""
    def __init__(self, tok, start): self.tok, self.start, self.state = tok, start, {}

    def __call__(self, input_ids, scores, **kw):
        import torch
        done = []
        for r in range(input_ids.shape[0]):
            t = self.tok.decode(input_ids[r, self.start:].tolist(), skip_special_tokens=False)
            done.append(bool(re.search(r'\S[^\n]*\n', t)))
        return torch.tensor(done, device=input_ids.device)


def cut_text(text):
    m = re.search(r'\S[^\n]*\n', text)
    return text[:m.end() - 1] if m else text


def generate(hf, tok, prompts, torch, bs=16, max_new=MAX_NEW, stop_nl=False):
    """greedy, left-padded batches; returns list of (gen_ids, full_text, stop_reason). v2 (2026-11-14, after B shard 0 v1):
    no newline stop by default - v1 stopped F1/F2 answers that start with '\\n1.' after the first marker; greedy decoding is
    causal, so generating to 80 tokens / EOS and cutting the list afterwards (list_text) equals stopping at that point."""
    from transformers import StoppingCriteriaList
    out = [None] * len(prompts); order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))
    dev = next(hf.parameters()).device
    for s0 in range(0, len(order), bs):
        b = order[s0:s0 + bs]; T = max(len(prompts[i]) for i in b)
        x = torch.full((len(b), T), tok.pad_token_id, dtype=torch.long); m = torch.zeros((len(b), T), dtype=torch.long)
        for j, i in enumerate(b): x[j, T - len(prompts[i]):] = torch.tensor(prompts[i]); m[j, T - len(prompts[i]):] = 1
        with torch.inference_mode():
            g = hf.generate(input_ids=x.to(dev), attention_mask=m.to(dev), max_new_tokens=max_new, do_sample=False, temperature=None,
                            top_p=None, top_k=None, num_beams=1, eos_token_id=list(EOS), pad_token_id=tok.pad_token_id,
                            stopping_criteria=(StoppingCriteriaList([NLStop(tok, T)]) if stop_nl else None))
        for j, i in enumerate(b):
            raw = g[j, T:].tolist(); e = next((q for q, t in enumerate(raw) if t in EOS), None)
            ids = raw if e is None else raw[:e]          # rows stopped by NLStop are padded with pad=EOS id afterwards
            full = tok.decode(ids); txt = full
            reason = 'eos' if e is not None else 'max_new'
            out[i] = (ids, txt, reason)
    return out


def score_gen(items, true, ctrl):
    """outcomes for one generated list vs the true and the control authors."""
    ht, ut = match_items(true, items); hc, _ = match_items(ctrl, items)
    st, us = match_surname(true, items); sc, _ = match_surname(ctrl, items)
    w0 = words(true[0]); wc0 = words(ctrl[0])
    pos1_full = bool(items) and same(w0, words(items[0]), False) or (bool(items) and same(w0, words(items[0]), True))
    pos1_sur = bool(items) and bool(words(items[0])) and bool(w0) and w0[-1] in (words(items[0])[-1], words(items[0])[0])
    pos1_sur_c = bool(items) and bool(words(items[0])) and bool(wc0) and wc0[-1] in (words(items[0])[-1], words(items[0])[0])
    return dict(n_items=len(items), any_full=any(ht), first_full=ht[0], any_sur=any(st), first_sur=st[0],
                first_sur_pos1=pos1_sur, first_full_pos1=bool(pos1_full),
                c_any_full=any(hc), c_first_full=hc[0], c_any_sur=any(sc), c_first_sur=sc[0], c_first_sur_pos1=pos1_sur_c,
                n_true_full=int(sum(ht)), n_true_sur=int(sum(st)),
                n_fab_full=len(items) - len(ut), n_fab_sur=len(items) - len(us),
                hit_full=json.dumps([bool(h) for h in ht]), hit_sur=json.dumps([bool(h) for h in st]))


def stage10_ranks(rows_by_cond):
    """{cond: row_ids} -> {cond: Series(row_id -> (rank, logprob))} from the stored Stage 10 final L63 files."""
    import pandas as pd
    out = {}
    for c, rows in rows_by_cond.items():
        d = R10 / 'raw' / ('final' if c == 'true' else f'cond_{c}/final') / 'L63'
        shards = sorted({int(x) for x in rows['shard']})
        parts = []
        for k in shards:
            z = np.load(d / f'shard_{k:03d}.npz')
            parts.append(pd.DataFrame({'row_id': z['row_id'], 'rank10': z['rank'], 'lp10': z['logprob']}))
        out[c] = pd.concat(parts).set_index('row_id')
    return out


def parity_check(D, tf_df, sel_cond, tiny=False):
    """WARN-only comparison with Stage 10 final L63 (ranks + logprob), per title condition."""
    import pandas as pd
    x = tf_df[tf_df.cond == sel_cond].copy()
    x['row_id'] = [D.nt[p][a][1][t] for p, a, t in zip(x.paper_id, x.author_index, x.token_index)]
    shard_of = D.papers.shard.to_dict(); x['s10shard'] = x.paper_id.map(shard_of)
    res = {}
    for c in TITLE_CONDS:
        xc = x[x.title_cond == c]
        ref = stage10_ranks({c: {'shard': xc.s10shard.unique()}})[c]
        j = xc.join(ref, on='row_id')
        if j.rank10.isna().any(): res[c] = dict(status='WARN', note=f'{int(j.rank10.isna().sum())} rows missing in Stage 10'); continue
        dl = (np.log10(j['rank']) - np.log10(j.rank10)).abs(); dlp = (j.logprob - j.lp10).abs()
        within = ((dl <= TOL_NLR) | (dlp <= TOL_LP)).mean()
        res[c] = dict(n=int(len(j)), rank_exact=float((j['rank'] == j.rank10).mean()), within_tol=float(within),
                      max_abs_dlogprob=float(dlp.max()), median_abs_dlogprob=float(dlp.median()), max_abs_dlog10rank=float(dl.max()),
                      mean_dlog10rank=float((np.log10(j['rank']) - np.log10(j.rank10)).mean()),
                      status=('OK' if within >= TOL_SHARE else 'WARN') + (' (tiny model: values not meaningful)' if tiny else ''))
    return res


def save_parquet(df, f):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.parquet'); df.to_parquet(tmp, index=False); os.replace(tmp, f)


def save_json(o, f):
    f.parent.mkdir(parents=True, exist_ok=True); tmp = f.with_name(f.stem + f'.tmp{os.getpid()}.json'); tmp.write_text(json.dumps(o, indent=1, default=str)); os.replace(tmp, f)


def paths(root, item, k):
    r = root / f'a16_{item}'
    # gen/ + meta/ = v1 (newline-stopped generation; B shard 0 job 11867053, D shard 0 job 11867054): superseded, kept.
    # tf/ is the same code in v1 and v2 -> reused if present.
    return dict(tf=r / f'tf/shard_{k:03d}.parquet', gen=r / f'gen_v2/shard_{k:03d}.parquet', meta=r / f'meta_v2/shard_{k:03d}.json',
                meta_v1=r / f'meta/shard_{k:03d}.json')


def tf_frame(units, keys):
    import pandas as pd
    rows = []
    for u in units:
        n = len(u['name'])
        base = {k: u[k] for k in keys}
        rows.append(pd.DataFrame(dict(**{k: [v] * n for k, v in base.items()}, token_index=np.arange(n, dtype=np.int16),
                                      token_id=np.array(u['name'], np.int32), n_tokens=np.full(n, n, np.int16),
                                      rank=u['rank'].astype(np.int32), ties=u['ties'].astype(np.int32),
                                      logprob=u['logprob'].astype(np.float32), top1=u['top1'].astype(np.int32))))
    return pd.concat(rows, ignore_index=True)


def do_shard(item, k, s, D, hf, model, tok, torch, root, tiny=False, sample_sha=None):
    import pandas as pd
    t0 = time.monotonic(); P = paths(root, item, k); sk = s[s.shard == k]
    meta = dict(item=item, shard=k, n_papers=len(sk), prereg_sha256=PREREG_SHA, script_sha256=sha(__file__), tiny=tiny,
                sample_sha256=sample_sha,
                torch=torch.__version__, gpu=(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'), job=os.environ.get('SLURM_JOB_ID'))
    if item == 'B':
        tf, gen = b_units(D, sk); keys = ['paper_id', 'title_cond', 'cond', 'author_index', 'rendered']
    else:
        tf, gen = d_units(D, sk); keys = ['paper_id', 'title_cond', 'cond', 'author_index', 'prefix_authors']
        meta['invariants'] = d_invariants(tf)
        if not all([meta['invariants']['prefix_scored_rows'] == 0, meta['invariants']['scored_sets_identical_k1'],
                    meta['invariants']['scored_sets_identical_k2'], meta['invariants']['reverse_scores_only_first']]):
            meta['invariants']['status'] = 'WARN'; log('WARN D invariants', meta['invariants'])
    t1 = time.monotonic(); reuse = P['tf'].exists() and P['meta_v1'].exists()
    if reuse:                                   # v1 run of this shard: identical teacher-forcing code -> reuse
        tfd = pd.read_parquet(P['tf']); nb = None; m1 = json.loads(P['meta_v1'].read_text())
        if len(tfd) != sum(len(u['name']) for u in tf): raise RuntimeError('stored tf rows differ from the units')
        meta['tf_reused_from_v1'] = dict(job=m1.get('job'), seconds=m1['seconds']['teacher_forcing'])
    else:
        nb = tf_run(model, tf, torch)
        tfd = tf_frame(tf, keys)
        tfd['written'] = [bool(D.written.get((p, a), False)) for p, a in zip(tfd.paper_id, tfd.author_index)]
    t2 = time.monotonic()
    g = generate(hf, tok, [u['ids'] for u in gen], torch); t3 = time.monotonic()
    # WARN check: batched vs one-by-one greedy for the first 4 prompts
    single = [generate(hf, tok, [u['ids']], torch, bs=1)[0] for u in gen[:4]]
    meta['gen_batch_vs_single_identical'] = f'{sum(a[0] == b[0] for a, b in zip(g[:4], single))}/4'
    t4 = time.monotonic()
    S = sk.set_index('paper_id'); rows = []
    for u, (ids, full, reason) in zip(gen, g):
        pid = u['paper_id']; true = D.authors(pid); row = S.loc[pid]; txt = list_text(full)
        if item == 'B':
            fmt = u['fmt']; items = split_items((row.first_initial + '.' + txt) if fmt == 'F4' else txt, fmt)
            ctrl = D.authors(row.ctrl_f4_paper_id if fmt == 'F4' else row.ctrl_paper_id)
            sc = score_gen(items, true, ctrl)
        else:
            items = split_items(txt, 'F0'); rest = true[1:]
            ht, ut = match_items(rest, items); hs, us = match_surname(rest, items)
            sc = dict(n_items=len(items), n_rest=len(rest), n_rest_full=int(sum(ht)), n_rest_sur=int(sum(hs)), any_rest_full=any(ht),
                      n_fab_full=len(items) - len(ut), hit_full=json.dumps([bool(h) for h in ht]), hit_sur=json.dumps([bool(h) for h in hs]),
                      prefix_author=u['prompt'])
            fmt = u['fmt']
        rows.append(dict(paper_id=pid, grp=row.grp, cond=fmt, prompt=u['prompt'] if item == 'B' else '', gen_ids=json.dumps(ids), full_text=full, text=txt,
                         stop=reason, n_gen=len(ids), items=json.dumps(items), **sc))
    gd = pd.DataFrame(rows)
    meta['parity_vs_stage10'] = m1['parity_vs_stage10'] if reuse else parity_check(D, tfd, 'F0' if item == 'B' else 'P_none', tiny)
    for c, v in meta['parity_vs_stage10'].items():
        if not str(v.get('status', '')).startswith('OK'): log(f'WARN parity {item} shard {k} {c}: {v}')
    meta.update(n_tf_seqs=len(tf), n_tf_tokens=int(len(tfd)), n_tf_batches=nb, n_gen=len(gen), mean_gen_tokens=float(gd.n_gen.mean()),
                stop_counts=gd.stop.value_counts().to_dict(),
                seconds=dict(build=t1 - t0, teacher_forcing=t2 - t1, generation=t3 - t2, gen_single_check=t4 - t3, total=time.monotonic() - t0))
    if torch.cuda.is_available(): meta['peak_mem_gib'] = torch.cuda.max_memory_allocated() / 2 ** 30
    if item == 'B':
        meta['quick'] = {f: {o: float(gd[gd.cond == f][o].mean()) for o in ['any_full', 'c_any_full', 'any_sur', 'c_any_sur', 'first_sur', 'c_first_sur', 'n_fab_full']} for f in FMTS}
    else:
        meta['quick'] = {f: {o: float(gd[gd.cond == f][o].mean()) for o in ['any_rest_full', 'n_rest_full', 'n_fab_full']} for f in ['G_true1', 'G_other1']}
    if not reuse: save_parquet(tfd, P['tf'])
    save_parquet(gd, P['gen']); meta['seconds']['total'] = time.monotonic() - t0; save_json(meta, P['meta'])
    log(f'{item} shard {k:03d} papers={len(sk)} tf_seqs={len(tf)} tokens={len(tfd)} gen={len(gen)} {json.dumps(meta["seconds"])}')
    log('  parity', json.dumps({c: (v.get('rank_exact'), v.get('within_tol'), v.get('status')) for c, v in meta['parity_vs_stage10'].items()}))
    log('  gen batch-vs-single', meta['gen_batch_vs_single_identical'], 'quick', json.dumps(meta['quick']))
    return meta


def work(a, tiny_root=None):
    import torch
    check_prereg(); check_matcher_copy()
    root = tiny_root or OUT; t_start = time.monotonic()
    s = load_sample(a.item, tiny_root.parent if tiny_root else None)
    sample_sha = sha((tiny_root.parent / 'config' / SAMPLE[a.item].name) if tiny_root else SAMPLE[a.item])
    shards = sorted(set(int(x) for x in a.shards.split(','))) if a.shards != 'all' else sorted(s.shard.unique())
    todo = [k for k in shards if not paths(root, a.item, k)['meta'].exists()]
    for k in shards:
        if k not in todo: log(f'{a.item} shard {k:03d}: skip (exists)')
    if not todo: return 0
    D = Data(); hf, model, tok = load_model(tiny=bool(tiny_root)); log(f'model loaded {time.monotonic() - t_start:.0f}s')
    for k in todo:
        t0 = time.monotonic()
        do_shard(a.item, k, s, D, hf, model, tok, torch, root, tiny=bool(tiny_root), sample_sha=sample_sha)
        el = time.monotonic() - t0
        if a.max_minutes and (time.monotonic() - t_start) / 60 + 1.3 * el / 60 > a.max_minutes:
            log('time budget reached; remaining shards left for the next job'); break
    return 0


def remaining(a):
    for item in ('B', 'D'):
        s = load_sample(item); n = int(s.shard.max()) + 1
        miss = [k for k in range(n) if not paths(OUT, item, k)['meta'].exists()]
        print(f'{item}: {n - len(miss)}/{n} shards done; REMAINING {len(miss)}', miss[:40])


def unit_asserts():
    """matcher / parser / renderer sanity (CPU)."""
    assert match(['Shimon Sakaguchi'], ['Sakaguchi Shimon']) == [True] and match(['A. Smith'], ['B. Smith']) == [False]
    assert match_surname(['Kevin L. Smith', 'J. Doe'], ['Doe', 'Smith'])[0] == [True, True]
    assert split_items('Smith, John, Doe, Jane', 'F1') == ['Smith John', 'Doe Jane']
    assert split_items('Zhang, Lixian; Boukas, El-Kebir; Lam, James', 'F1') == ['Zhang, Lixian', 'Boukas, El-Kebir', 'Lam, James']
    assert list_text(' L. Li, Y. Zhang, and W. X. Zheng. The paper was') == 'L. Li, Y. Zhang, and W. X. Zheng'
    assert list_text('\n\n1. Smith, John\n2. Doe, Jane.\n\nThe paper') == 'Smith, John; Doe, Jane'
    assert list_text(' Zhang, Lixian; Lam, James. The paper titled "X" (2014)') == 'Zhang, Lixian; Lam, James'
    assert list_text(' C. Y. Liang, Jr. Smith\nmore') == 'C. Y. Liang, Jr. Smith'
    assert render('Kevin L. Smith', 'F4') == ' L. Smith' and render('N. Arkani-Hamed', 'F4') == ' Arkani-Hamed' and render('Sung K. Kang', 'F1') == ' Kang, Sung K.'
    print('unit asserts OK')


# ------------------------------------------------------------------ precheck (CPU, no model)
def precheck(a):
    import pandas as pd
    check_prereg(); check_matcher_copy()
    D = Data(); rep = {}
    unit_asserts()
    for item in ('B', 'D'):
        s = load_sample(item); per = []
        for k in sorted(s.shard.unique()):
            sk = s[s.shard == k]
            tf, gen = (b_units if item == 'B' else d_units)(D, sk)
            L = [len(u['prefix']) + len(u['name']) - 1 for u in tf]
            per.append(dict(shard=int(k), papers=len(sk), tf_seqs=len(tf), tf_tokens=int(sum(L)), tf_name_tokens=int(sum(len(u['name']) for u in tf)),
                            max_len=int(max(L)), gen=len(gen)))
            if item == 'B':
                f0 = [u for u in tf if u['cond'] == 'F0' and u['title_cond'] == 'true']
                bad = sum(D.tok(' ' + D.authors(u['paper_id'])[u['author_index']], add_special_tokens=False).input_ids != u['name'] for u in f0)
                f0p = [u for u in gen if u['fmt'] == 'F0']
                badp = sum(D.tok(u['prompt']).input_ids != u['ids'] for u in f0p)
                per[-1].update(f0_name_ids_differ=bad, f0_prompt_ids_differ=badp)
            else:
                per[-1].update(d_invariants(tf))
        df = pd.DataFrame(per); rep[item] = df
        print(f'== {item}: {len(s)} papers, {len(df)} shards'); print(df.describe().loc[['mean', 'max', 'min']].round(1).to_string())
        if item == 'B': print('F0 name/prompt id mismatches vs Stage 10:', int(df.f0_name_ids_differ.sum()), int(df.f0_prompt_ids_differ.sum()))
        else: print('D invariants all OK:', bool((df.prefix_scored_rows == 0).all() and df.scored_sets_identical_k1.all() and df.scored_sets_identical_k2.all() and df.reverse_scores_only_first.all()))
        df.to_csv(G / f'raw/a16_{item}_precheck_units.csv', index=False) if a.write else None
    s = load_sample('B'); print('B groups', s.grp.value_counts().to_dict(), 'F4 same-initial control share', round(s.ctrl_f4_same_initial.mean(), 3))
    print('B first-token type by group'); print(pd.crosstab(s.grp, s.fa_type))
    s = load_sample('D'); print('D groups', s.grp.value_counts().to_dict(), 'min n_authors', s.n_authors.min(), 'shuffle2 identity share', round((s.shuffle2 == '[0, 1]').mean(), 3))
    print('PRECHECK DONE')


# ------------------------------------------------------------------ tiny whole-pipeline test (CPU)
def tiny(a):
    import pandas as pd
    root = Path(a.root); (root / 'config').mkdir(parents=True, exist_ok=True)
    unit_asserts(); checks = {}
    for item in ('B', 'D'):
        s = load_sample(item)
        sk = pd.concat([s[s.grp == g].head(2) for g in ['A', 'B', 'C']]).copy(); sk['shard'] = [0, 0, 0, 1, 1, 1]
        f = root / 'config' / SAMPLE[item].name; sk.to_parquet(f, index=False); Path(str(f) + '.sha256').write_text(f'{sha(f)}  {f.name}\n')
        ns = argparse.Namespace(item=item, shards='0,1', max_minutes=None)
        work(ns, tiny_root=root / 'raw')
        for k in (0, 1):
            P = paths(root / 'raw', item, k); m = json.loads(P['meta'].read_text())
            tfd = pd.read_parquet(P['tf']); gd = pd.read_parquet(P['gen'])
            checks[f'{item} shard {k} outputs written'] = P['tf'].exists() and P['gen'].exists()
            checks[f'{item} shard {k} ranks >= 1'] = bool((tfd['rank'] >= 1).all())
            checks[f'{item} shard {k} all 7 title conditions'] = set(tfd.title_cond) == set(TITLE_CONDS)
            checks[f'{item} shard {k} parity code ran (values not meaningful on tiny)'] = len(m['parity_vs_stage10']) == 7
            if item == 'B':
                checks[f'B shard {k} 5 formats generated'] = set(gd.cond) == set(FMTS) and len(gd) == 15
                checks[f'B shard {k} TF formats'] = set(tfd.cond) == set(FMTS)
            else:
                inv = m['invariants']
                checks[f'D shard {k} invariants'] = inv['prefix_scored_rows'] == 0 and inv['scored_sets_identical_k1'] and inv['scored_sets_identical_k2'] and inv['reverse_scores_only_first']
                checks[f'D shard {k} 8 conditions'] = set(tfd.cond) == set(DCONDS)
        t = time.monotonic(); work(argparse.Namespace(item=item, shards='0,1', max_minutes=None), tiny_root=root / 'raw')
        checks[f'{item} skip-if-exists (no recompute)'] = time.monotonic() - t < 30
        # v1 -> v2 path: a shard with tf + v1 meta must reuse tf and only regenerate (meta_v2 moved to the v1 name, no deletion)
        P = paths(root / 'raw', item, 1); P['meta_v1'].parent.mkdir(parents=True, exist_ok=True); os.replace(P['meta'], P['meta_v1']); h_tf = sha(P['tf'])
        work(argparse.Namespace(item=item, shards='1', max_minutes=None), tiny_root=root / 'raw')
        m2 = json.loads(P['meta'].read_text())
        checks[f'{item} v1 tf reused, not recomputed'] = 'tf_reused_from_v1' in m2 and sha(P['tf']) == h_tf
    # parity code on REAL Stage 10 data: feed stored Stage 10 ranks back in -> must be exact (tests the row alignment)
    D = Data(); s = load_sample('B').head(3); tf, _ = b_units(D, s)
    tf = [u for u in tf if u['cond'] == 'F0']
    for u in tf: u['rank'] = u['ties'] = u['top1'] = np.zeros(len(u['name']), int); u['logprob'] = np.zeros(len(u['name']))
    tfd = tf_frame(tf, ['paper_id', 'title_cond', 'cond', 'author_index', 'rendered'])
    tfd['row_id'] = [D.nt[p][a][1][t] for p, a, t in zip(tfd.paper_id, tfd.author_index, tfd.token_index)]
    for c in TITLE_CONDS:
        ref = stage10_ranks({c: {'shard': D.papers.loc[s.paper_id, 'shard'].unique()}})[c]
        sel = tfd.title_cond == c; tfd.loc[sel, 'rank'] = ref.loc[tfd[sel].row_id, 'rank10'].to_numpy(); tfd.loc[sel, 'logprob'] = ref.loc[tfd[sel].row_id, 'lp10'].to_numpy()
    pc = parity_check(D, tfd.drop(columns='row_id'), 'F0')
    checks['parity on stored Stage 10 values = exact (row alignment)'] = all(v['rank_exact'] == 1.0 for v in pc.values())
    pc_bad = parity_check(D, tfd.assign(logprob=tfd.logprob - 3, rank=tfd['rank'] * 10).drop(columns='row_id'), 'F0')
    checks['parity flags a perturbed copy as WARN'] = all(v['status'].startswith('WARN') for v in pc_bad.values())
    ok = all(checks.values())
    for k, v in checks.items(): print('TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    print('TINY', 'ALL PASS' if ok else 'SOME FAIL'); return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['freeze', 'precheck', 'tiny', 'work', 'remaining'])
    ap.add_argument('--root'); ap.add_argument('--item', choices=['B', 'D']); ap.add_argument('--shards', default='0')
    ap.add_argument('--max-minutes', type=float, default=None); ap.add_argument('--write', action='store_true')
    a = ap.parse_args()
    if a.cmd == 'freeze': freeze(a)
    elif a.cmd == 'precheck': precheck(a)
    elif a.cmd == 'tiny': sys.exit(tiny(a))
    elif a.cmd == 'work': sys.exit(work(a))
    else: remaining(a)


if __name__ == '__main__':
    main()
