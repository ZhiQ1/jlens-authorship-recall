"""Decode-gap check (post hoc, descriptive; 2026-11-14). NOT part of any preregistered plan.

Question: group A papers (R0 x MC strong) - why does the model not write the authors? H_dec: the true first author's
first name token is already near the top of the final-output distribution (rank 2-5 under teacher forcing at the first
generation position, right after "Authors:") and loses to a more common token.

Data (read-only):
  Stage 10 final readout (L63 = actual model next-token logits), raw/final/L63 (true title) and raw/cond_<c>/final/L63
  (false_0..4, delete): per name-token row rank (1 + #logits strictly greater), top1 token id.
  Row used = author_index 0, token_index 0 (first author, first name token; context = prompt ending in "Authors:").
  Groups: 391_groups/papers_used.csv (grp, first_written). Name format = role of that token (Stage 10 X1_by_format).
  Teams: 381_stage13/summary_cpu_teamci/folds_own9108_k5s13.npz 'team'; team-cluster bootstrap, 2000 draws, seed 391.
Outputs: 391_groups/summary_decode_gap_20261114/
"""
import json, os, sys
from pathlib import Path
import numpy as np, pandas as pd

BASE = Path('/scratch/zhang.zhiqi2/jlens'); R10 = BASE / '351_stage10'; G = BASE / '391_groups'
OUT = Path(os.environ.get('DG_OUT', G / 'summary_decode_gap_20261114')); OUT.mkdir(parents=True, exist_ok=True)
NB = int(os.environ.get('DG_NB', 2000)); SEED = 391
CONDS = ['true'] + [f'false_{k}' for k in range(5)] + ['delete']
BINS = [(1, 1), (2, 5), (6, 20), (21, 100), (101, 10 ** 9)]
BLAB = ['r1', 'r2_5', 'r6_20', 'r21_100', 'r_gt100']
GROUPS = ['A', 'B', 'C', 'D', 'U0', 'U1', 'R2s']
LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.append(s)


# ---------------------------------------------------------------- data
toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet')
first = toks[(toks.author_index == 0) & (toks.token_index == 0)].set_index('paper_id')
assert first.index.is_unique
rows = first.row_id.to_numpy()


def load_final(cond):
    d = R10 / 'raw' / ('final' if cond == 'true' else f'cond_{cond}/final') / 'L63'
    parts = []
    for f in sorted(d.glob('shard_*.npz')):
        z = np.load(f); meta = json.loads(str(z['meta']))
        if meta.get('condition', 'true') != cond or meta['readout'] != 'final' or meta['layer'] != 63: raise ValueError(f'meta mismatch {f}')
        parts.append(pd.DataFrame({'row_id': z['row_id'], 'rank': z['rank'], 'ties': z['ties'], 'logprob': z['logprob'], 'top1': z['top1']}))
    x = pd.concat(parts).set_index('row_id')
    if not x.index.is_unique: raise ValueError(f'duplicate rows {cond}')
    return x


R = {}
for c in CONDS:
    x = load_final(c); miss = np.setdiff1d(rows, x.index.to_numpy())
    if len(miss): log(f'WARN {c}: {len(miss)} first-author rows missing')
    R[c] = x.reindex(rows); R[c].index = first.index
    log(f'loaded {c}: {len(x)} rows; first-author rows {R[c]["rank"].notna().sum()}')

P = pd.read_csv(G / 'papers_used.csv').set_index('paper_id')
P = P[P.index.isin(first.index)]
pc = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'authors']).set_index('paper_id')
fmt_role = first.role.reindex(P.index)
P['format'] = np.where(fmt_role == 'initial_first', 'initial_first', np.where(fmt_role == 'given_first', 'given_first', 'other'))
P['gold_id'] = first.token_id.reindex(P.index); P['gold_text'] = first.token_text.reindex(P.index)
P['first_author'] = pc.authors.reindex(P.index).str.split(';').str[0].str.strip()
for c in CONDS:
    P[f'rank_{c}'] = R[c]['rank'].reindex(P.index).to_numpy(); P[f'top1_{c}'] = R[c]['top1'].reindex(P.index).to_numpy()
    P[f'lp_{c}'] = R[c]['logprob'].reindex(P.index).to_numpy(); P[f'ties_{c}'] = R[c]['ties'].reindex(P.index).to_numpy()
# self-check: top1 == gold  <=> rank == 1 (rank is tie-favourable; ties can break it)
chk = ((P.rank_true == 1) == (P.top1_true == P.gold_id))
log(f'self-check rank==1 <=> top1==gold: agree {chk.mean():.4f} (n disagree {(~chk).sum()}; ties at rank 1 explain disagreements)' + ('' if chk.mean() > 0.99 else ' WARN'))

# ---------------------------------------------------------------- tokenizer (decode winners)
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained('Qwen/Qwen3-32B')
dec = lambda i: tok.decode([int(i)])
P['top1_text'] = P.top1_true.map(dec); P['top1_delete_text'] = P.top1_delete.map(dec)

# ---------------------------------------------------------------- team bootstrap
z = np.load(BASE / '381_stage13/summary_cpu_teamci/folds_own9108_k5s13.npz')
team = pd.Series(z['team'], index=z['ids'].astype(str)); codes, uniq = pd.factorize(team)
team = pd.Series(codes, index=team.index); assert P.index.isin(team.index).all()
CNT = np.random.default_rng(SEED).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)


def W(idx): return CNT[:, team.loc[idx].to_numpy()]


def share(idx, x):
    """weighted mean with team bootstrap: est, lo, hi."""
    x = np.asarray(x, float); w = W(idx); b = (w @ x) / w.sum(1)
    return x.mean(), *np.percentile(b, [2.5, 97.5]), b


def fmt(e, lo, hi): return f'{e:.3f} [{lo:.3f}, {hi:.3f}]'


def binof(r):
    r = np.asarray(r); return np.select([(r >= a) & (r <= b) for a, b in BINS], BLAB, 'na')


def dist_rows(sub, label, cond='true'):
    out = []
    for keys, s in sub:
        if len(s) == 0: continue
        r = s[f'rank_{cond}'].to_numpy(); bb = binof(r)
        row = dict(**keys, cond=cond, n_papers=len(s), median_rank=float(np.median(r)), mean_log10_rank=float(np.log10(r).mean()))
        for b in BLAB:
            e, lo, hi, _ = share(s.index, bb == b); row[b] = e; row[b + '_lo'] = lo; row[b + '_hi'] = hi
        e, lo, hi, _ = share(s.index, r <= 5); row['le5'] = e; row['le5_lo'] = lo; row['le5_hi'] = hi
        row['ci_note'] = 'n<30 descriptive' if len(s) < 30 else ''
        out.append(row)
    return out


# 1. by group, split by first author written / unwritten
T1 = []
for g in GROUPS:
    for fw, nm in ((False, 'first_unwritten'), (True, 'first_written')):
        s = P[(P.grp == g) & (P.first_written == fw)]
        T1 += dist_rows([(dict(group=g, subset=nm), s)], 't1')
T1 = pd.DataFrame(T1); T1.to_csv(OUT / 'T1_rank_dist_by_group.csv', index=False)

# 2. by group x name format (first author unwritten)
T2 = []
for g in GROUPS:
    for f in ['initial_first', 'given_first', 'other']:
        s = P[(P.grp == g) & (~P.first_written) & (P.format == f)]
        T2 += dist_rows([(dict(group=g, format=f), s)], 't2')
T2 = pd.DataFrame(T2); T2.to_csv(OUT / 'T2_rank_dist_by_group_format.csv', index=False)

# 2b. conditions: true vs false titles vs delete (title dependence of the first-token rank), first author unwritten
T2b = []
for g in GROUPS:
    s = P[(P.grp == g) & (~P.first_written)]
    if len(s) == 0: continue
    for f in ['all', 'initial_first', 'given_first']:
        ss = s if f == 'all' else s[s.format == f]
        row = dict(group=g, format=f, n_papers=len(ss))
        for c in CONDS:
            row[f'le5_{c}'] = (ss[f'rank_{c}'] <= 5).mean(); row[f'r1_{c}'] = (ss[f'rank_{c}'] == 1).mean()
            row[f'median_{c}'] = float(ss[f'rank_{c}'].median())
        row['le5_false_mean'] = np.mean([row[f'le5_false_{k}'] for k in range(5)]); row['r1_false_mean'] = np.mean([row[f'r1_false_{k}'] for k in range(5)])
        fm = np.mean([(ss[f'rank_false_{k}'] <= 5).to_numpy() for k in range(5)], 0)
        e, lo, hi, _ = share(ss.index, (ss.rank_true <= 5).to_numpy() - fm); row['le5_true_minus_false'] = e; row['lo'] = lo; row['hi'] = hi
        T2b.append(row)
T2b = pd.DataFrame(T2b); T2b.to_csv(OUT / 'T2b_conditions.csv', index=False)

# 3. what beats the gold token (top1 under true title) when gold rank is 2-5 (and >5)
ft = toks[toks.token_index == 0]
freq = ft.token_id.value_counts()                        # how often a token starts an author string in the cohort
freq_rank = pd.Series(np.arange(1, len(freq) + 1), index=freq.index)
co = ft[ft.author_index > 0].groupby('paper_id').token_id.apply(set)
sur = toks[(toks.author_index == 0) & (toks.role == 'surname_first')].groupby('paper_id').token_id.first()


def category(pid, r):
    w = int(r.top1_true); wt = dec(w); gt = r.gold_text; ws = wt.strip(); gs = gt.strip()
    if w == r.gold_id: return 'gold(tie)'
    if pid in sur.index and w == sur.loc[pid]: return 'true_first_author_surname'
    if r.format == 'given_first' and len(ws) == 1 and ws.isupper() and gs[:1] == ws and wt.startswith(' '): return 'initial_of_true_given_name'
    if r.format == 'initial_first' and len(ws) > 1 and ws.isalpha() and ws[:1] == gs[:1] and wt.startswith(' '): return 'full_given_name_same_letter'
    if pid in co.index and w in co.loc[pid]: return 'coauthor_first_token'
    if len(ws) == 1 and ws.isalpha() and ws.isupper() and wt.startswith(' '): return 'other_initial'
    if wt.startswith(' ') and ws[:1].isupper() and ws.isalpha(): return 'other_name_like'
    if ws == '': return 'whitespace/newline'
    return 'punct/other'


P['winner_cat'] = [category(pid, r) for pid, r in P.iterrows()]
P['winner_is_delete_top1'] = P.top1_true == P.top1_delete
P['winner_freq_rank'] = P.top1_true.map(freq_rank).fillna(10 ** 6)
P['gold_freq_rank'] = P.gold_id.map(freq_rank).fillna(10 ** 6)
T3 = []
for g in GROUPS:
    for band, lo_, hi_ in (('2-5', 2, 5), ('6-20', 6, 20), ('>20', 21, 10 ** 9)):
        for f in ['all', 'initial_first', 'given_first']:
            s = P[(P.grp == g) & (~P.first_written) & P.rank_true.between(lo_, hi_)]
            if f != 'all': s = s[s.format == f]
            if len(s) == 0: continue
            row = dict(group=g, gold_rank_band=band, format=f, n_papers=len(s), winner_is_title_free_default=s.winner_is_delete_top1.mean(),
                       winner_in_top20_cohort_first_tokens=(s.winner_freq_rank <= 20).mean(),
                       median_winner_freq_rank=float(s.winner_freq_rank.median()), median_gold_freq_rank=float(s.gold_freq_rank.median()),
                       median_logprob_gap_gold=float(s.lp_true.median()))
            for k, v in s.winner_cat.value_counts(normalize=True).items(): row['cat_' + k] = v
            T3.append(row)
T3 = pd.DataFrame(T3).fillna(0); T3.to_csv(OUT / 'T3_winner_categories.csv', index=False)
top_w = (P[(P.grp.isin(['A', 'B'])) & (~P.first_written) & P.rank_true.between(2, 5)].groupby(['grp', 'format']).top1_text
         .apply(lambda s: '; '.join(f'{repr(k)}:{v}' for k, v in s.value_counts().head(15).items())))
top_w.to_csv(OUT / 'T3b_top_winner_tokens.csv')

# 4. A - B in share at rank <= 5 (first author unwritten): raw, format-standardised, within format, within citation bin
A = P[(P.grp == 'A') & (~P.first_written)]; B = P[(P.grp == 'B') & (~P.first_written)]
T4 = []
for nm, thr in (('le5', 5), ('r1', 1), ('le20', 20)):
    ea, *_, ba = share(A.index, A.rank_true <= thr); eb, *_, bb_ = share(B.index, B.rank_true <= thr)
    d = ba - bb_; T4.append(dict(measure=nm, estimator='raw A-B', est=ea - eb, lo=np.percentile(d, 2.5), hi=np.percentile(d, 97.5), nA=len(A), nB=len(B)))
    # within format and A-format-standardised
    comp = {}
    for f in ['initial_first', 'given_first', 'other']:
        a = A[A.format == f]; b = B[B.format == f]
        if len(a) == 0 or len(b) == 0: continue
        e1, *_, b1 = share(a.index, a.rank_true <= thr); e2, *_, b2 = share(b.index, b.rank_true <= thr)
        comp[f] = (len(a) / len(A), e1 - e2, b1 - b2)
        T4.append(dict(measure=nm, estimator=f'within {f}', est=e1 - e2, lo=np.percentile(b1 - b2, 2.5), hi=np.percentile(b1 - b2, 97.5), nA=len(a), nB=len(b)))
    wsum = sum(v[0] for v in comp.values())
    est = sum(v[0] * v[1] for v in comp.values()) / wsum; bt = sum(v[0] * v[2] for v in comp.values()) / wsum
    T4.append(dict(measure=nm, estimator='format-standardised (A format mix)', est=est, lo=np.percentile(bt, 2.5), hi=np.percentile(bt, 97.5), nA=len(A), nB=len(B)))
    T4.append(dict(measure=nm, estimator='share of raw A-B explained by format = 1 - std/raw', est=1 - est / (ea - eb), lo=np.nan, hi=np.nan, nA=len(A), nB=len(B)))
    # within citation bin (n1n2/(n1+n2), bins >= 30 papers in both) and within bin x format
    for byfmt in (False, True):
        cells = []
        keys = ['citation_bin', 'format'] if byfmt else ['citation_bin']
        for k, a in A.groupby(keys):
            b = B[(B[keys] == pd.Series(k if isinstance(k, tuple) else (k,), index=keys)).all(1)]
            if len(a) >= 30 and len(b) >= 30: cells.append((a, b))
        w = np.array([len(a) * len(b) / (len(a) + len(b)) for a, b in cells]); w /= w.sum()
        e = sum(wi * ((a.rank_true <= thr).mean() - (b.rank_true <= thr).mean()) for wi, (a, b) in zip(w, cells))
        bt = sum(wi * (share(a.index, a.rank_true <= thr)[3] - share(b.index, b.rank_true <= thr)[3]) for wi, (a, b) in zip(w, cells))
        T4.append(dict(measure=nm, estimator='within citation bin' + (' x format' if byfmt else ''), est=e, lo=np.percentile(bt, 2.5), hi=np.percentile(bt, 97.5),
                       nA=sum(len(a) for a, _ in cells), nB=sum(len(b) for _, b in cells), n_cells=len(cells)))
T4 = pd.DataFrame(T4); T4.to_csv(OUT / 'T4_A_minus_B.csv', index=False)

# 5. caveat: A papers whose true first token is rank 1 under teacher forcing (= greedy would start with the right token)
C5 = []
for g in GROUPS:
    s = P[(P.grp == g) & (~P.first_written)]
    for f in ['all', 'initial_first', 'given_first']:
        ss = s if f == 'all' else s[s.format == f]
        if len(ss): C5.append(dict(group=g, format=f, n_papers=len(ss), n_rank1=int((ss.rank_true == 1).sum()), share_rank1=(ss.rank_true == 1).mean(),
                                   share_rank1_delete=(ss.rank_delete == 1).mean()))
C5 = pd.DataFrame(C5); C5.to_csv(OUT / 'T5_rank1_caveat.csv', index=False)

keep = ['grp', 'first_written', 'format', 'citation_bin', 'first_author', 'gold_id', 'gold_text', 'top1_text', 'top1_delete_text', 'winner_cat',
        'winner_is_delete_top1', 'winner_freq_rank', 'gold_freq_rank'] + [f'rank_{c}' for c in CONDS] + ['lp_true', 'ties_true']
P[keep].to_parquet(OUT / 'paper_first_token.parquet')
P[(P.grp == 'A') & P.rank_true.between(2, 5)].sample(min(40, int((P.grp == 'A').sum())), random_state=1)[
    ['format', 'first_author', 'gold_text', 'top1_text', 'rank_true', 'rank_delete', 'winner_cat']].to_csv(OUT / 'examples_A_rank2_5.csv')

pd.set_option('display.width', 250); pd.set_option('display.max_columns', 60)
for nm, t in (('T1', T1), ('T2', T2), ('T2b', T2b), ('T3', T3), ('T4', T4), ('T5', C5)):
    log(f'\n== {nm}'); log(t.round(3).to_string())
log('\n== T3b'); log(top_w.to_string())
(OUT / 'run_log.txt').write_text('\n'.join(LOG))
log('DONE')
