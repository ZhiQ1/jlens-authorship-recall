"""Stage 13 M5 (V29, handbook s13-m5), CPU parts with EXISTING data only; POST-HOC (M5 has no pre-registered rule).
M5 as proposed: (1) per-position probes, (2) patchscope, (3) true/false discrimination at the name positions.
User decision 2026-10-30 (U47): the part that asks the same as X4 is merged into X4; the rest is done or dropped with a reason.

Part A  (M5-3, name positions, lens readouts): Stage 10 saved, for every gold name token, its rank under each readout x
        layer in the true run and in the 5 false-title runs (351_stage10/raw[/cond_false_j]/<readout>/L<l>). Per paper and
        token role (all tokens; name-first token = initial_first + given_first; surname_first; surname_cont), score =
        mean log10(1/rank) over the paper's tokens of that role. Discrimination = share of (paper, false title j) with
        score(true) > score(false_j) (ties 0.5) = a paired AUROC (0.5 = cannot tell the true-title run from a false one).
        Groups: cohort group_tight; target - control within citation bin (>= 30 per group). 95% team-cluster bootstrap.
Part B  (M5-1 at the positions where residuals exist): can a linear probe tell the TRUE-title run from the FALSE_0 run
        from the residual at the last title token / at ':'? Stage 11 titlepos residuals (9 layers 16-60, all 9,108 papers,
        true and false_0). The prompt keeps the paper's own year after the title, so a false run has a year that may not
        match its title; the probe is split by |year(donor) - year(paper)| = 0 vs > 0 to separate "year/title mismatch"
        from anything else. Ridge classifier (alpha by inner CV on fold 0), 5 folds grouping authors AND donor titles
        (stage13_cpu.group_folds with donors: a title is never on both sides). AUROC on held-out rows, team bootstrap.
Outputs (new, never overwritten): summary_m5/m5_name_discrimination.csv, summary_m5/m5_titlepos_probe.csv,
  reports/m5_report.md (written by this script; text sections on coverage / GPU needs included).
--test: Part A on 2 layers x 6 shards, Part B on 2 layers x 1,500 papers, output summary_m5_test/."""
import importlib.util, sys, time
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R11 = B / '361_stage11'; ROOT = B / '381_stage13'
TEST = '--test' in sys.argv; OUT = ROOT / ('summary_m5_test' if TEST else 'summary_m5'); REP = OUT if TEST else ROOT / 'reports'; NB = 2000
CONDS = ['true'] + [f'false_{j}' for j in range(5)]
ROLES = {'all': None, 'name_first': ('initial_first', 'given_first'), 'surname_first': ('surname_first',), 'surname_cont': ('surname_cont',)}


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def log(*x): print(time.strftime('%H:%M:%S'), *x, flush=True)
def ci(b): return np.nanpercentile(b, [2.5, 97.5])
def fm(e, lo, hi, d=3): return f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]'
def safe(p):
    p = Path(p)
    return p if not p.exists() else p.with_name(f'{p.stem}.{time.strftime("%Y%m%d_%H%M%S")}{p.suffix}')


def cw(cl, seed):
    codes, uniq = pd.factorize(pd.Series(cl))
    return np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NB).astype(float)[:, codes]


def strat(x, grp, cbin, W, min_n=30):
    cells = []
    for b in pd.unique(cbin):
        ia = np.where((cbin == b) & (grp == 'target') & np.isfinite(x))[0]; ib = np.where((cbin == b) & (grp == 'control') & np.isfinite(x))[0]
        if len(ia) >= min_n and len(ib) >= min_n: cells.append((ia, ib))
    w = np.array([len(a) * len(b) / (len(a) + len(b)) for a, b in cells]); w /= w.sum()
    est = sum(wi * (x[a].mean() - x[b].mean()) for wi, (a, b) in zip(w, cells)); bt = np.zeros(NB)
    for wi, (a, b) in zip(w, cells): bt += wi * ((W[:, a] @ x[a]) / np.maximum(W[:, a].sum(1), 1e-9) - (W[:, b] @ x[b]) / np.maximum(W[:, b].sum(1), 1e-9))
    return est, ci(bt), len(cells)


def part_a(papers, team_of):
    toks = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'role']).set_index('row_id')
    plan = [('final', 63)] + [(r, l) for r in ('logit', 'jlens_public') for l in (24, 32, 40, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62)]
    if TEST: plan = [('final', 63), ('logit', 56)]
    pp_all = papers.set_index('paper_id'); rows = []; Wc = {}
    for ro, l in plan:
        sc = {}
        for c in CONDS:
            d = R10 / 'raw' if c == 'true' else R10 / 'raw' / f'cond_{c}'
            fs = sorted((d / ro / f'L{l:02d}').glob('shard_*.npz'))[:6 if TEST else None]
            q = [np.load(f) for f in fs]
            sc[c] = pd.Series(-np.log10(np.concatenate([x['rank'] for x in q]).astype(float)), index=np.concatenate([x['row_id'] for x in q]))
        idx = sc['true'].index
        for c in CONDS[1:]: idx = idx.intersection(sc[c].index)
        df = pd.DataFrame({c: sc[c].reindex(idx).to_numpy() for c in CONDS}, index=idx).join(toks)
        for rname, rr in ROLES.items():
            s = df if rr is None else df[df.role.isin(rr)]
            pp = s.groupby('paper_id')[CONDS].mean()
            T = pp['true'].to_numpy()[:, None]; Fm = pp[CONDS[1:]].to_numpy()
            disc = ((T > Fm) + 0.5 * (T == Fm)).mean(1); diff = T[:, 0] - Fm.mean(1)
            meta = pp_all.loc[pp.index]; key = (rname, len(pp))
            if key not in Wc: Wc[key] = cw([team_of[p] for p in pp.index], 951)
            W = Wc[key]; grp = meta.group_tight.to_numpy(); cb = meta.citation_bin.to_numpy()
            for g in ('all', 'target', 'control'):
                m = np.ones(len(pp), bool) if g == 'all' else grp == g; Wg = W[:, m]
                for est, x in (('discrimination', disc), ('true_minus_false', diff)):
                    b = (Wg @ x[m]) / Wg.sum(1); lo, hi = ci(b)
                    rows.append(dict(readout=ro, layer=l, role=rname, group=g, estimand=est, n=int(m.sum()), est=x[m].mean(), lo=lo, hi=hi))
            for est, x in (('discrimination', disc), ('true_minus_false', diff)):
                e, (lo, hi), nb = strat(x, grp, cb, W)
                rows.append(dict(readout=ro, layer=l, role=rname, group='target-control (within bin)', estimand=est, n=nb, est=e, lo=lo, hi=hi))
        log('A', ro, l)
    return pd.DataFrame(rows)


def auroc(y, s):
    o = np.argsort(s, kind='mergesort'); r = np.empty(len(s)); r[o] = np.arange(1, len(s) + 1)
    _, inv, cnt = np.unique(s, return_inverse=True, return_counts=True)          # average ranks for ties
    sums = np.bincount(inv, r); r = (sums / cnt)[inv]
    n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def auroc_boot(y, s, W):
    """AUROC per bootstrap draw with integer row weights (ties count 0.5)"""
    _, inv = np.unique(s, return_inverse=True); out = np.zeros(len(W))
    for i, w in enumerate(W):
        wp = np.bincount(inv, w * y); wn = np.bincount(inv, w * (1 - y)); n1, n0 = wp.sum(), wn.sum()
        out[i] = (wp * (np.cumsum(wn) - wn + 0.5 * wn)).sum() / (n1 * n0) if n1 > 0 and n0 > 0 else np.nan
    return out


def part_b(papers, c13):
    ft = pd.read_parquet(R10 / 'cohort/conditions/false_titles.parquet'); ft = ft[ft.k == 0].set_index('paper_id')
    R, P, Lr = {}, {}, None
    for c in ('true', 'false_0'):
        fs = sorted((R11 / 'raw/titlepos' / c).glob('shard_*.npz'))
        zs = [np.load(f) for f in fs]
        Lr = [int(x) for x in zs[0]['probe_layers']]
        P[c] = np.concatenate([z['resid_paper_id'] for z in zs])
        R[c] = {pos: np.concatenate([z[f'resid_{pos}'] for z in zs]) for pos in ('title', 'colon')}
    assert (P['true'] == P['false_0']).all(), 'paper order differs between true and false_0'
    pids = P['true']; n = len(pids)
    sel = np.arange(n) if not TEST else np.sort(np.random.default_rng(0).choice(n, 1500, replace=False))
    donors = ft.loc[pids, 'donor_paper_id'].to_numpy(); dyear = ft.loc[pids, 'd_year'].to_numpy()
    ids = np.concatenate([pids, pids]); dn = np.concatenate([pids, donors])
    folds, grp = c13.group_folds(ids, donors=dn)
    folds = np.concatenate([folds[:n][sel], folds[n:][sel]]); grp = np.concatenate([grp[:n][sel], grp[n:][sel]])
    y = np.r_[np.ones(len(sel)), np.zeros(len(sel))].astype(int); dy = np.r_[dyear[sel], dyear[sel]]
    meta = papers.set_index('paper_id').loc[pids[sel]]; gt = np.r_[meta.group_tight.to_numpy(), meta.group_tight.to_numpy()]
    W = cw(grp, 952); rows = []
    for pos in ('title', 'colon'):
        nl = R['true'][pos].shape[1]; layers = (Lr if pos == 'title' else Lr + [63])[:nl]          # colon stores one extra layer (63)
        for li, l in enumerate(layers):
            if TEST and l not in (24, 56): continue
            X = np.concatenate([R['true'][pos][sel, li], R['false_0'][pos][sel, li]]).astype(np.float32); s = np.zeros(len(y)); alpha = None
            for k in np.unique(folds):
                tr, te = folds != k, folds == k; mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6; A = (X[tr] - mu) / sd; yt = y[tr] - y[tr].mean()
                G = A.T @ A; scl = np.trace(G) / len(G)
                if alpha is None:
                    inner = np.random.default_rng(1).random(tr.sum()) < 0.8; Gi = A[inner].T @ A[inner]; best = -1
                    for a in (1.0, 10.0, 100.0, 1000.0, 10000.0):
                        w_ = np.linalg.solve(Gi + a * scl * np.eye(len(G)), A[inner].T @ (y[tr][inner] - y[tr][inner].mean()))
                        au = auroc(y[tr][~inner], A[~inner] @ w_)
                        if au > best: best, alpha = au, a
                s[te] = ((X[te] - mu) / sd) @ np.linalg.solve(G + alpha * scl * np.eye(len(G)), A.T @ yt)
            for sub, m in (('all', np.ones(len(y), bool)), ('d_year = 0', dy == 0), ('d_year > 0', dy > 0), ('target', gt == 'target'), ('control', gt == 'control')):
                if m.sum() < 50: continue
                e = auroc(y[m], s[m]); bt = auroc_boot(y[m], s[m], W[:, m]); lo, hi = ci(bt)
                rows.append(dict(pos=pos, layer=l, subset=sub, n_rows=int(m.sum()), auroc=e, lo=lo, hi=hi, alpha=alpha))
            log('B', pos, l, f'AUROC {rows[-5]["auroc"]:.3f}' if len(rows) >= 5 else '')
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True); c13 = load(H / '13_stage13/stage13_cpu.py', 'c13')
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin'])
    _, team = c13.group_folds(papers.paper_id.to_numpy()); team_of = dict(zip(papers.paper_id, team))
    warn = []
    try: A = part_a(papers, team_of); pA = safe(OUT / 'm5_name_discrimination.csv'); A.to_csv(pA, index=False)
    except Exception: import traceback; traceback.print_exc(); warn.append('Part A failed'); A = None
    try: Bt = part_b(papers, c13); pB = safe(OUT / 'm5_titlepos_probe.csv'); Bt.to_csv(pB, index=False)
    except Exception: import traceback; traceback.print_exc(); warn.append('Part B failed'); Bt = None
    L = ['# Stage 13 M5 (V29): what of M5 can be answered with existing data (POST-HOC)', '',
         f'Script `~/jlens_work/13_stage13/stage13_m5_cpu.py`, run {time.strftime("%Y-%m-%d %H:%M")}' + (' **TEST RUN**' if TEST else '') + '. CPU only, existing data, no GPU. **M5 has no pre-registered rule: every number here is post-hoc.**', '',
         '## What M5 was', '',
         'Proposed in the progress log ("M5 (per-position probes, patchscope, true/false at name positions) is proposed and will be decided after M1-M3") and in report Part IV ("true/false discrimination must be done at positions where author names are already in the context (M5-3)", because at the title and ":" the true and false titles are both real papers). Its three parts were never specified further. User decision 2026-10-30 (U47): merge into X4 what asks the same question; do or drop the rest with a reason.', '',
         '## Part by part', '',
         '| part | status | where |', '|---|---|---|',
         '| M5-2 patchscope at the title / ":" | **covered by X4** (same question: decode year / first author / field from the paper\'s own state at the title and ":"; X4 does it with a partner control, tune / test and team CIs) | `reports/x4_report.md`, V42 adds paper CIs and recognition on tune / test |',
         '| M5-1 per-position probes at the title / ":" (paper attributes, first author) | **covered by M2 / E4b / M3** (probes of year, citations, field, recognised, first-author token at the last title token and ":", L16-L63, team folds) | `reports/stage13_cpu_report_group.md`, `m2_teamci.md`, `m3_report.md` |',
         '| M5-1 at the title / ":" for true vs false title (new, this script, Part B) | **done (post-hoc)**: probe true-title run vs false_0 run from the existing Stage 11 titlepos residuals | below |',
         '| M5-3 true / false discrimination at the name positions, by lens readout (new, this script, Part A) | **done (post-hoc)** from the existing Stage 10 ranks (every gold name token, true and 5 false runs, logit / public J-lens L24-L62, output) | below |',
         '| M5-1 probes and M5-2 patchscope AT THE NAME POSITIONS | **not possible without new GPU runs**: no residuals at name positions were ever saved (Stage 10 saved ranks / top-1 only; Stage 11 titlepos saved the title and ":" only; Stage 12 patch_pos ranks only; M3 / X1 / X3 title and ":" only) | cost below |', '']
    if A is not None:
        L += ['## Part A: true / false discrimination at the name positions (lens readouts)', '',
              'Discrimination = share of (paper, false title) pairs where the gold-name score in the true-title run beats the false-title run (0.5 = chance; ties 0.5). true - false = the Stage 10 title-specific signal (mean over the 5 false titles) for reference. Team CI.', '']
        for role in ROLES:
            L += [f'### role: {role}', '', '| readout | layer | all | target | control | target - control (within bin) | true - false (all) |', '|---|---|---|---|---|---|---|']
            for (ro, l), g in A[(A.role == role)].groupby(['readout', 'layer'], sort=False):
                f = lambda gr, e='discrimination': g[(g.group == gr) & (g.estimand == e)].iloc[0]
                L.append(f'| {ro} | L{l} | ' + ' | '.join(fm(f(x).est, f(x).lo, f(x).hi) for x in ('all', 'target', 'control', 'target-control (within bin)'))
                         + f' | {fm(f("all", "true_minus_false").est, f("all", "true_minus_false").lo, f("all", "true_minus_false").hi)} |')
            L.append('')
        a = A[(A.role == 'all') & (A.group == 'all') & (A.estimand == 'discrimination')]
        first = a[(a.lo > 0.5)]
        L += ['Earliest layer with discrimination interval above 0.5 (all tokens, all papers): ' + ', '.join(f'{ro} ' + (f'L{int(first[first.readout == ro].layer.min())}' if (first.readout == ro).any() else 'none') for ro in a.readout.unique()) + '.', '']
    if Bt is not None:
        L += ['## Part B: probe true-title run vs false_0 run at the last title token and ":" (Stage 11 titlepos residuals)', '',
              'AUROC on held-out rows (5 folds; a title is never in two folds); 0.5 = cannot tell. The prompt keeps the paper\'s year, so with d_year > 0 the false run has a title whose real year differs from the year in the prompt; at the title token the year has not been read yet (it comes after the title).', '',
              '| pos | layer | all | d_year = 0 | d_year > 0 | target | control |', '|---|---|---|---|---|---|---|']
        for (pos, l), g in Bt.groupby(['pos', 'layer'], sort=False):
            f = lambda sub: (lambda r: fm(r.auroc, r.lo, r.hi) + f' (n {r.n_rows})')(g[g.subset == sub].iloc[0]) if (g.subset == sub).any() else '-'
            L.append(f'| {pos} | L{l} | ' + ' | '.join(f(s) for s in ('all', 'd_year = 0', 'd_year > 0', 'target', 'control')) + ' |')
        L.append('')
    L += ['## What would need new GPU runs (not submitted)', '',
          '- Residuals at the name positions (each author-name token of the true run and of false_0, Stage 10 prompt with the author list teacher-forced), 9,108 papers, layers e.g. 16-62 (9-15 layers): one forward pass per paper and condition, the same pass as Stage 10 / Stage 11 titlepos; Stage 11 titlepos (all 9,108 papers, 6 conditions, 9 layers, title + ":") took 72 shards x 6 conditions of short A100 units. Saving all ~150k name tokens x 10 layers x 5,120 fp16 is about 15 GB per condition, so a subsample (e.g. the 1,186-paper Stage 11 sample, about 20k tokens: about 2 GB per condition) is the practical choice: about 24 A100 units of < 30 min for true + false_0 at the Stage 11 rate (rough estimate, not measured).',
          '- Patchscope at the name positions (X4 design with the source state taken at a name token): the X4 pscope cost (24 A100 units for 1,178 papers, 7 layers, 2 positions, 3 answers) per name position added.',
          '- Neither was approved as a new GPU experiment; this report does not submit them (instruction for V29).', '',
          '## Caveats', '', '- Post-hoc; no thresholds were fixed in advance. Teacher-forced scores, not generation (addendum 4).',
          '- Part A uses lens readouts, which cannot see information that is present but not lens-decodable (the reason M5 was proposed); a probe on name-position residuals would be needed for that.',
          '- Part B separates a year/title mismatch (d_year > 0) from other differences; with d_year = 0 the true and false runs differ only by which real title is shown.']
    if warn: L += ['', '## WARN', ''] + [f'- {w}' for w in warn]
    p = safe(REP / 'm5_report.md'); p.write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('\nM5 DONE', p)


if __name__ == '__main__':
    main()
