"""Addendum 18b item 5 - title-token importance (L8-L24), GPU driver + CPU prep / analysis. New file 2026-11-17.

Design (addendum 18b item 5, locked; no numeric decision rule is given there -> descriptive, "pre-registered design"):
 classes of TRUE-title words (fixed here before any GPU output):
   content   alphabetic word, > 2 letters, not in the sklearn English stop-word list
   rare      content word whose document frequency among the 9,108 cohort titles is <= 5 ("by corpus frequency")
   function  word in the stop-word list
   firstlast the first and the last word of the title
 replacements (all words of the class at once):
   syn       WordNet synonym (first lemma of the word's synsets, in WordNet order, that differs from the word, single word,
             alphabetic; capitalisation copied); function words: a fixed near-synonym table (FUNC_SYN) - words without a synonym
             stay unchanged (coverage reported); the prompt is re-tokenised (Stage 10 rule tok(prompt).input_ids)
   rand      same token length: every title token of those words is replaced by a random vocabulary token (alphabetic token
             starting with 'Ġ', >= 3 letters; rng seeded per paper and class), positions unchanged
 -> 8 variants. Readouts: (1) final output: log10(1/rank) of every gold name token (Stage 10 contexts); loss = true - variant
 (paper means); spec_variant = variant - mean of 5 false titles; (2) L8-L24 title-position probe (E4b recipe on the last title
 token: ridge to the true-title L63 ':' residual, 5 archived team folds, decoded on the 9,137 name ids; gold = first-name and
 surname-first tokens) at L8, L12, L16, L20, L24. Key contrast: syn loss - rand loss (meaning vs surface form).
 Team-bootstrap CIs (2,000 draws), paired.
Units ('main', k) -> raw/a18b_item5/main/shard_XXX.npz.  'prep' (CPU) -> a18b_config/item5_variants.parquet.
Commands: prep | work [--shards S] | remaining | tiny --root DIR | analyze
"""
import argparse, json, os, re, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a18b_common as A

CLASSES = ['content', 'rare', 'function', 'firstlast']; KINDS = ['syn', 'rand']
VARIANTS = [f'{c}_{k}' for c in CLASSES for k in KINDS]; ALLC = A.CONDS + VARIANTS
PL = [8, 12, 16, 20, 24]; RARE_DF = 5
DEPS = A.R13 / 'a18b_deps'
FUNC_SYN = {'and': '&', 'with': 'using', 'using': 'with', 'via': 'through', 'through': 'via', 'towards': 'toward', 'toward': 'towards',
            'between': 'among', 'among': 'between', 'on': 'upon', 'upon': 'on', 'about': 'regarding', 'without': 'lacking', 'into': 'in',
            'within': 'inside', 'under': 'beneath', 'over': 'above', 'by': 'through', 'across': 'throughout', 'beyond': 'past',
            'from': 'out of', 'for': 'towards', 'in': 'within', 'of': 'from', 'to': 'towards', 'can': 'may', 'not': 'never', 'is': 'remains',
            'are': 'remain', 'its': 'their', 'their': 'its', 'how': 'in what way', 'what': 'which', 'which': 'what', 'when': 'whenever',
            'new': 'novel', 'more': 'further', 'all': 'every', 'each': 'every', 'every': 'each', 'some': 'certain', 'many': 'numerous',
            'few': 'several', 'two': '2', 'three': '3', 'first': 'initial', 'large': 'big', 'part': 'portion', 'beyond': 'past'}
RAW = Path(os.environ.get('A18B_RAW5', A.R13 / 'raw/a18b_item5')); SUM = Path(os.environ.get('A18B_SUM5', A.R13 / 'summary_a18b_item5'))
VARF = Path(os.environ.get('A18B_VAR5', A.CFG / 'item5_variants_v3.parquet'))   # v1/v2 item5_variants.parquet superseded (slur, lost inflection)
_SMP = {}


def smp():
    if 'm' not in _SMP: _SMP['m'] = A.sample()
    return _SMP['m']


def out_path(u): return RAW / u[0] / f'shard_{u[1]:03d}.npz'
def all_units(shards=None): return [('main', k) for k in A.parse_shards(shards, 24)]
WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")


def wordnet():
    sys.path.insert(0, str(DEPS / 'py')); import nltk
    nltk.data.path.insert(0, str(DEPS / 'nltk_data')); from nltk.corpus import wordnet as wn
    wn.ensure_loaded(); return wn


BLOCK = {'chink', 'wop', 'spic', 'kike', 'nigger', 'gook', 'dago', 'jap', 'chinaman', 'coon', 'paki', 'wetback', 'honky', 'redskin', 'squaw',
         'dyke', 'fag', 'faggot', 'queer', 'retard', 'bitch', 'bastard', 'whore', 'slut', 'cunt', 'piss', 'shit', 'crap', 'tit', 'boob'}
BAD_USAGE = ('slur', 'disparagement', 'obscenity', 'vulgarism', 'derogation', 'profanity')


def synonym(wn, w):
    """v3 (2026-11-17, before any GPU output of item 5): keep the inflection (base form via wn.morphy, the word's suffix is
    re-attached), skip synsets whose usage domain is a slur / disparagement / obscenity (the v1 table had e.g. an ethnic slur)."""
    lw = w.lower(); base = wn.morphy(lw) or lw
    # inflection of the original relative to its base: '', plural / 3rd person ('s'), past ('ed'), gerund ('ing'); else skip
    if lw == base: infl = ''
    elif lw in (base + 's', base + 'es'): infl = 's'
    elif lw in (base + 'ed', base + 'd') or (len(base) > 2 and lw == base + base[-1] + 'ed'): infl = 'ed'
    elif lw in (base + 'ing', base[:-1] + 'ing') or (len(base) > 2 and lw == base + base[-1] + 'ing'): infl = 'ing'
    else: return None
    def inflect(n):
        if infl == 's': return n + ('es' if n.endswith(('s', 'x', 'z', 'ch', 'sh')) else 's')
        if infl == 'ed': return n + ('d' if n.endswith('e') else 'ed')
        if infl == 'ing': return (n[:-1] if n.endswith('e') and not n.endswith('ee') else n) + 'ing'
        return n
    for s in wn.synsets(base):
        if any(any(b in d.name() for b in BAD_USAGE) for d in s.usage_domains()): continue
        for l in s.lemmas():
            n = l.name()
            if '_' in n or not n.isalpha() or n.lower() in (lw, base) or n.lower() in BLOCK: continue
            if n.lower().endswith(('ing', 'ed')) and infl: continue          # avoid double inflection (e.g. 'unmaskingd')
            n = inflect(n)
            return n.capitalize() if w[0].isupper() else n
    return None


def prep(a=None, out=None, papers_subset=None):
    """variant table: paper_id, variant, title (syn) or ids (rand, JSON), n_class_words, n_replaced."""
    import pandas as pd
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as SW
    out = Path(out or VARF)
    if out.exists(): print('exists', out); return
    m = A.s11(); s10 = m.s10; tok = s10.tokenizer(); wn = wordnet()
    papers = pd.read_parquet(A.R10 / 'cohort/papers.parquet', columns=['paper_id', 'title', 'year', 'prompt_ids']); P = papers.set_index('paper_id')
    df = {}
    for t in papers.title:
        for w in set(x.lower() for x in WORD.findall(str(t))): df[w] = df.get(w, 0) + 1
    vocab = [i for t, i in tok.get_vocab().items() if t.startswith('Ġ') and t[1:].isalpha() and len(t) >= 4 and i < 151643]
    vocab = np.array(sorted(vocab))
    rows = []
    for pid in (papers_subset if papers_subset is not None else A.sample().paper_id):
        r = P.loc[pid]; title = str(r.title); text = s10.PROMPT.format(title=title, year=r.year); ids = json.loads(r.prompt_ids)
        tpos = m.title_positions(tok, text, ids); e = tok(text, return_offsets_mapping=True); a0 = text.index('titled "') + len('titled "')
        words = list(WORD.finditer(title))
        cls = {'content': [w for w in words if len(w.group()) > 2 and w.group().lower() not in SW],
               'function': [w for w in words if w.group().lower() in SW]}
        cls['rare'] = [w for w in cls['content'] if df.get(w.group().lower(), 0) <= RARE_DF]
        cls['firstlast'] = ([words[0]] + ([words[-1]] if len(words) > 1 else [])) if words else []
        for c in CLASSES:
            ws = cls[c]
            # syn: rebuild the title string
            new, last, nrep = [], 0, 0
            for w in ws:
                lw = w.group().lower()
                s = FUNC_SYN.get(lw) if lw in SW else synonym(wn, w.group())
                if s is not None and s.lower() != w.group().lower():
                    if w.group()[0].isupper() and s[0].isalpha(): s = s[0].upper() + s[1:]
                    new.append(title[last:w.start()] + s); last = w.end(); nrep += 1
            new_title = ''.join(new) + title[last:]
            ptx = s10.PROMPT.format(title=new_title, year=r.year); pids = tok(ptx).input_ids
            rows.append(dict(paper_id=pid, variant=f'{c}_syn', prompt=ptx, ids=json.dumps(pids), n_class_words=len(ws), n_replaced=nrep, title_new=new_title))
            # rand: replace the title tokens overlapping those words, same length
            rng = np.random.default_rng([SEED_RAND, CLASSES.index(c), int(pid[:8], 16)])
            rid = list(ids); nr = 0
            for p in tpos:
                x, y = e.offset_mapping[p]
                if any(w.start() + a0 < y and w.end() + a0 > x for w in ws): rid[p] = int(vocab[rng.integers(len(vocab))]); nr += 1
            rows.append(dict(paper_id=pid, variant=f'{c}_rand', prompt=None, ids=json.dumps(rid), n_class_words=len(ws), n_replaced=nr, title_new=None))
    T = pd.DataFrame(rows); out.parent.mkdir(parents=True, exist_ok=True); T.to_parquet(out, index=False)
    s = T.groupby('variant').agg(papers_with_class=('n_class_words', lambda v: int((v > 0).sum())), mean_words=('n_class_words', 'mean'),
                                 papers_changed=('n_replaced', lambda v: int((v > 0).sum())), mean_replaced=('n_replaced', 'mean'))
    print(s.to_string()); (out.with_suffix('.summary.txt')).write_text(s.to_string() + f'\nRARE_DF={RARE_DF}; random vocab tokens: {len(vocab)}\n')


SEED_RAND = 1805
_VAR = {}
def variants():
    if 'v' not in _VAR:
        import pandas as pd
        T = pd.read_parquet(VARF); _VAR['v'] = {(r.paper_id, r.variant): r for r in T.itertuples()}
    return _VAR['v']


def prompt_of(C, pid, v):
    """ids, last title position, changed?"""
    if v in A.CONDS: L = C.layout(pid, v); return L['ids'], L['last_title'], True
    r = variants()[(pid, v)]; ids = json.loads(r.ids)
    if v.endswith('_rand'): return ids, C.layout(pid, 'true')['last_title'], r.n_replaced > 0
    tp = C.s11.title_positions(C.tok, r.prompt, ids); return ids, tp[-1], r.n_replaced > 0


def compute(C, u):
    torch = C.torch; sm = smp(); papers = sm[sm.shard == u[1]].paper_id.tolist()
    out = {v: [] for v in ALLC}; rows = []; res = []; res_key = []; ycol = []; changed = []
    for pid in papers:
        Lt = C.layout(pid, 'true')
        for ai, rids, name in C.ctx[pid]: rows += rids
        for v in ALLC:
            ids, lt, ch = prompt_of(C, pid, v); changed.append((pid, v, ch)); rk = []
            for ci_, (ai, rids, name) in enumerate(C.ctx[pid]):
                T = ids + name[:-1]; pos = [len(ids) - 1 + j for j in range(len(name))]
                if ci_ == 0:
                    lg, acts = A.final_logits(C, T, pos, record_layers=PL + [63])
                    res.append(np.stack([acts[l][0, lt].float().cpu().numpy() for l in PL]).astype(np.float16)); res_key.append((pid, v))
                    if v == 'true': ycol.append(acts[63][0, len(ids) - 1].float().cpu().numpy().astype(np.float16))
                    lg = lg[0]
                else: lg = A.final_logits(C, T, pos)[0]
                rk.append(A.ranks(lg, torch.tensor(name, device=C.model.input_device), torch))
            out[v].append(np.concatenate(rk))
    d = dict(row_id=np.array(rows), variants=np.array(ALLC), res=np.stack(res), res_pid=np.array([k[0] for k in res_key]), res_var=np.array([k[1] for k in res_key]),
             y_colon=np.stack(ycol), y_pid=np.array(papers), changed_pid=np.array([c[0] for c in changed]), changed_var=np.array([c[1] for c in changed]),
             changed=np.array([c[2] for c in changed]), **{f'rank_{v}': np.concatenate(x) for v, x in out.items()})
    import a18b_item4 as I4
    chk = I4.check_vs_e1(dict(row_id=d['row_id'], rank_true=d['rank_true'][:, None], rank_false_0=d['rank_false_0'][:, None]))
    return d, dict(check=chk)


def work(a, C=None):
    if not VARF.exists(): raise SystemExit('run prep first (CPU)')
    miss, C = A.work(all_units(a.shards), out_path, compute, a.max_minutes, C=C, tiny=A.TINY, tag='a18b_item5'); return miss


# ------------------------------------------------------------------ analysis
def analyze(a=None):
    import pandas as pd
    A.check_addendum(); B = A.Boot(); SUM.mkdir(parents=True, exist_ok=True)
    have = [out_path(u) for u in all_units() if out_path(u).exists()]; Z = [np.load(f) for f in have]
    cat = lambda k: np.concatenate([z[k] for z in Z])
    tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    rid = cat('row_id'); pid = tk.reindex(rid).to_numpy()
    PM = pd.DataFrame({v: pd.Series(A.nlr(cat(f'rank_{v}'))).groupby(pid).mean() for v in ALLC})
    ch = pd.DataFrame(dict(p=cat('changed_pid'), v=cat('changed_var'), c=cat('changed'))).pivot(index='p', columns='v', values='c')
    pids = PM.index.to_numpy(); F = PM[A.FALSES].mean(1)
    rows, boots = [], {}
    def add(name, readout, v_series, extra=None):
        v_series = v_series.dropna(); pp = v_series.index.to_numpy(); v = v_series.to_numpy()
        e, b = B.mean(pp, v); t, tb, _ = B.tc(pp, v)
        r = dict(readout=readout, quantity=name, n_papers=len(pp), est=e, lo=B.ci(b)[0], hi=B.ci(b)[1], tc=t, tc_lo=B.ci(tb)[0], tc_hi=B.ci(tb)[1])
        if extra: r.update(extra)
        rows.append(r); return b
    add('spec_true', 'final', PM['true'] - F)
    for c in CLASSES:
        for k in KINDS:
            v = f'{c}_{k}'; m = ch[v].reindex(pids).fillna(False).astype(bool).to_numpy()
            add(f'loss_{v}', 'final', (PM['true'] - PM[v])[m]); add(f'spec_{v}', 'final', (PM[v] - F)[m])
        m = (ch[f'{c}_syn'].reindex(pids).fillna(False).astype(bool) & ch[f'{c}_rand'].reindex(pids).fillna(False).astype(bool)).to_numpy()
        add(f'syn_minus_rand_loss_{c}', 'final', ((PM['true'] - PM[f'{c}_syn']) - (PM['true'] - PM[f'{c}_rand']))[m])
    # ---- title-position probe (E4b recipe) on the stored last-title residuals
    import a18b_item1 as I1
    Wr, nw, eps, col = I1.decoder()
    c13 = A.load_mod(A.H / '13_stage13/stage13_cpu.py', 'c13_i5'); allp = B.meta.index.to_numpy(); fo, _ = c13.group_folds(allp); FOLD = pd.Series(np.asarray(fo), index=allp)
    m11 = A.s11(); papers, toks = m11.cohort(); ctx = m11.contexts_of(toks)
    rt = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['paper_id', 'author_index', 'token_id', 'role'])
    sf = {(p, int(a_)): int(t) for p, a_, t in rt[rt.role == 'surname_first'][['paper_id', 'author_index', 'token_id']].itertuples(index=False)}
    rv, rp, RES = cat('res_var'), cat('res_pid'), cat('res'); yp = cat('y_pid'); YC = cat('y_colon').astype(np.float32); yi = {p: i for i, p in enumerate(yp)}
    for li, l in enumerate(PL):
        tr = rv == 'true'
        evals = [(RES[rv == v, li].astype(np.float32), FOLD.reindex(rp[rv == v]).to_numpy()) for v in ALLC]
        _, _, preds = I1.ridge_predict(RES[tr, li].astype(np.float32), YC[[yi[p] for p in rp[tr]]], FOLD.reindex(rp[tr]).to_numpy(), evals)
        for kd in ('first', 'surname'):
            pm = {}
            for v, pr in zip(ALLC, preds):
                pc = rp[rv == v]
                gls = [[col[name[0]] for _, _, name in ctx[p_]] if kd == 'first' else [col[sf[(p_, a_)]] for a_, _, _ in ctx[p_] if (p_, a_) in sf] for p_ in pc]
                pm[v] = pd.Series(I1.decode_paper_mean(pr, gls, Wr, nw, eps), index=pc)
            pm = pd.DataFrame(pm); Fp = pm[A.FALSES].mean(1)
            add(f'spec_true', f'probe_L{l}_{kd}', pm['true'] - Fp)
            for c in CLASSES:
                for k in KINDS:
                    v = f'{c}_{k}'; m = ch[v].reindex(pm.index).fillna(False).astype(bool).to_numpy()
                    add(f'loss_{v}', f'probe_L{l}_{kd}', (pm['true'] - pm[v])[m])
                m = (ch[f'{c}_syn'].reindex(pm.index).fillna(False).astype(bool) & ch[f'{c}_rand'].reindex(pm.index).fillna(False).astype(bool)).to_numpy()
                add(f'syn_minus_rand_loss_{c}', f'probe_L{l}_{kd}', ((pm['true'] - pm[f'{c}_syn']) - (pm['true'] - pm[f'{c}_rand']))[m])
    T = pd.DataFrame(rows); T.to_csv(SUM / 'item5_table.csv', index=False)
    vs = (VARF.with_suffix('.summary.txt')).read_text() if VARF.with_suffix('.summary.txt').exists() else ''
    f = lambda e, lo, hi: f'{e:+.3f} [{lo:+.3f}, {hi:+.3f}]' + ('*' if (lo > 0 or hi < 0) else '')
    L = ['# Addendum 18b item 5 — title-token importance (L8–L24)', '',
         f'**Pre-registered design (addendum 18b, locked 2026-11-17, sha256 {A.ADDENDUM_SHA[:12]}…), no locked numeric decision rule → descriptive.** '
         f'600-paper subsample (seed {A.SEED}); {len(have)}/24 shards, {len(pids)} papers. Word classes, synonym table and random-token rule fixed in a18b_item5.py before any GPU output '
         f'(rare = cohort-title document frequency ≤ {RARE_DF}; synonyms = WordNet 3.0 via nltk, function words = fixed near-synonym table; papers whose class is empty or '
         'unchanged are left out of that variant). loss = true − variant (paper mean log10(1/rank)); syn − rand = loss(syn) − loss(rand) (negative → synonyms keep more → "meaning"; '
         '≈ 0 with both losses > 0 → "surface form" equally needed). Author-team cluster bootstrap 2,000 draws; T − C within citation bin. * = CI excludes 0.', '',
         '## Final output', '', '| quantity | estimate | n papers | T − C |', '|---|---|---|---|']
    for r in T[T.readout == 'final'].itertuples(): L.append(f'| {r.quantity} | {f(r.est, r.lo, r.hi)} | {r.n_papers} | {f(r.tc, r.tc_lo, r.tc_hi)} |')
    for kd in ('first', 'surname'):
        L += ['', f'## Title-position probe (last title token), gold = {kd}', '', '| quantity | ' + ' | '.join(f'L{l}' for l in PL) + ' |', '|' + '---|' * (len(PL) + 1)]
        sub = T[T.readout.str.endswith(kd) & T.readout.str.startswith('probe')]
        for q, x in sub.groupby('quantity', sort=False):
            x = x.set_index('readout'); L.append(f'| {q} | ' + ' | '.join(f(x.loc[f"probe_L{l}_{kd}", "est"], x.loc[f"probe_L{l}_{kd}", "lo"], x.loc[f"probe_L{l}_{kd}", "hi"]) for l in PL) + ' |')
    L += ['', '## Variant table (prep)', '', '```', vs, '```']
    chk = [json.loads(str(z['meta'])).get('check', {}) for z in Z]
    L += ['', '## Checks (WARN only)', '', f'- true / false_0 ranks vs stored Stage 11 E1 rows: ' + str(pd.Series([c.get('status') for c in chk]).value_counts().to_dict()) +
          f'; min exact share true {min([c.get("eq_true", 1) for c in chk]):.3f}, false_0 {min([c.get("eq_false0", 1) for c in chk]):.3f} (threshold 0.95).']
    (SUM / 'item5_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


def tiny(a):
    global RAW, SUM, VARF
    import pandas as pd
    root = Path(a.root); RAW = root / 'raw'; SUM = root / 'summary'; VARF = root / 'variants.parquet'; ok = {}
    sm = A.sample(); _SMP['m'] = pd.concat([sm[sm.shard == k].head(1) for k in range(3)])     # 3 papers (CPU tiny is slow: 14 prompt variants)
    prep(out=VARF, papers_subset=_SMP['m'].paper_id.tolist())
    T = pd.read_parquet(VARF); ok['8 variants per paper'] = bool((T.groupby('paper_id').size() == 8).all())
    ok['rand keeps length'] = bool(all(len(json.loads(r.ids)) == len(json.loads(A.s11().cohort()[0].set_index('paper_id').loc[r.paper_id].prompt_ids)) for r in T[T.variant.str.endswith('rand')].head(20).itertuples()))
    ok['syn changes some titles'] = bool((T[T.variant == 'content_syn'].n_replaced > 0).mean() > 0.5)
    print(T[T.variant.str.endswith('syn')].head(8)[['variant', 'n_class_words', 'n_replaced', 'title_new']].to_string())
    C = A.make_ctx(tiny=True); import a18b_item1 as I1; I1.set_tiny_decoder(C)
    ns = argparse.Namespace(shards='0-2', max_minutes=600); miss = work(ns, C=C); ok['all units written'] = not miss
    z = np.load(out_path(('main', 0))); ok['res shape'] = z['res'].shape[1:] == (len(PL), C.model.d_model)
    mt = out_path(('main', 0)).stat().st_mtime; work(ns, C=C); ok['skip-if-done'] = out_path(('main', 0)).stat().st_mtime == mt
    try: analyze(); ok['analysis ran'] = (SUM / 'item5_report.md').exists()
    except Exception: import traceback; traceback.print_exc(); ok['analysis ran'] = False
    for k, v in ok.items(): print('A18B ITEM5 TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    r = all(ok.values()); print('A18B ITEM5 TINY', 'PASS' if r else 'FAIL', flush=True); return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['prep', 'work', 'remaining', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'prep': prep(a); return
    if a.cmd == 'analyze': analyze(a); return
    if a.cmd == 'remaining':
        m = [u for u in all_units(a.shards) if not out_path(u).exists()]; print(f'REMAINING {len(m)} of {len(all_units(a.shards))}'); return
    A.check_addendum(); work(a)


if __name__ == '__main__':
    main()
