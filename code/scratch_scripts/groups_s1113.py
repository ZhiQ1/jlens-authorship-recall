"""Addendum 7 (+8), exploratory: Stage 11 / 12 / 13 measures split by group (A/B/C/D only: the GPU samples hold no U0/U1/R2 papers).

Unwritten authors only where per-token rows exist (E1, E2, X6, X7, P1, P2, N2, F2), with the addendum-8 position split
(unwritten first author / unwritten other authors) beside the pooled number. First-author-only measures (X1, X3, X4) use papers whose
first author was NOT written. Per-paper measures over all authors / the whole list (E4b, N1) and two-class measures (M2) are reported
per group descriptively, with the caveat that C/D values there include the written authors.
Estimators as in the original stages (ratio of means for recovery / loss, plain means otherwise); 95% team-cluster bootstrap, ONE shared
draw (groups_core.Engine, cohort team ids). Differences between groups are UNADJUSTED (no citation-bin weighting; the Stage 11 sample is
bin-balanced only for target vs control). n < 30 papers -> descriptive only.
Output: OUT/s1113_groups.csv, OUT/s1113_contrasts.csv (refuse to overwrite).
"""
import os, sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import groups_core as gc

R11 = gc.BASE / '361_stage11'; R12 = gc.BASE / '371_stage12'; R13 = gc.BASE / '381_stage13'
OUT = gc.OUT; G4 = ['A', 'B', 'C', 'D']
CONTR = [('A', 'B'), ('C', 'A'), ('C', 'B'), ('C', 'D'), ('D', 'B')]


def nlr(r): return -np.log10(np.asarray(r, float))


def load_dir(d, keys=None):
    zs = [np.load(f) for f in sorted(Path(d).glob('shard_*.npz'))]
    ks = [k for k in zs[0].files if k != 'meta' and (keys is None or k in keys)]
    out = {}
    for k in ks:
        if zs[0][k].ndim == 0 or k in ('layers', 'items', 'comps', 'probe_layers'): out[k] = zs[0][k]
        else: out[k] = np.concatenate([z[k] for z in zs])
    return out


class S1113:
    def __init__(self):
        gc.check_plan()
        self.P = gc.papers(); self.E = gc.Engine(self.P)
        self.ok = self.P[(self.P.consistent == True) & self.P.grp.isin(G4)]               # noqa: E712
        au = pd.read_parquet(gc.DATA / 'author_flags.parquet')
        t = pd.read_parquet(gc.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'author_index'])
        self.tok = t.merge(au[['paper_id', 'author_index', 'written']], on=['paper_id', 'author_index']).set_index('row_id')
        self.rows, self.crows = [], []

    # -------------------------------------------------- generic
    def per_paper(self, row_id, cols, who):
        t = self.tok.loc[row_id]
        df = pd.DataFrame(cols); df['paper_id'] = t.paper_id.to_numpy(); w = t.written.to_numpy(); fi = (t.author_index == 0).to_numpy()
        sel = {'unwritten': ~w, 'unwritten_first': ~w & fi, 'unwritten_other': ~w & ~fi, 'all authors': np.ones(len(w), bool)}[who]
        df['_ai'] = t.author_index.to_numpy(); df = df[sel]
        n_auth = df.groupby('paper_id')['_ai'].nunique()
        pp = df.drop(columns='_ai').groupby('paper_id').mean(); pp['n_auth'] = n_auth
        return pp[pp.index.isin(self.ok.index)]

    def emit(self, stage, measure, item, who, est_boot, n, n_auth, note=''):
        """est_boot: dict group -> (est, boot[NB])"""
        for g, (e, b, nn, na) in est_boot.items():
            lo, hi = self.E.ci(b)
            self.rows.append(dict(stage=stage, measure=measure, item=item, who=who, group=g, estimate=e, lo=lo, hi=hi, n_papers=nn, n_authors=na,
                                  descriptive_only=nn < 30, note=note))
        for a, b_ in CONTR:
            if a in est_boot and b_ in est_boot:
                ea, ba, na_, _ = est_boot[a]; eb, bb, nb_, _ = est_boot[b_]; d = ba - bb; lo, hi = self.E.ci(d)
                self.crows.append(dict(stage=stage, measure=measure, item=item, who=who, contrast=f'{a} - {b_} (unadjusted)', estimate=ea - eb, lo=lo, hi=hi,
                                       p_raw=self.E.pval(d), n_a=na_, n_b=nb_, descriptive_only=min(na_, nb_) < 30, note=note))

    def ratio(self, pp, num, den):
        out = {}
        for g in G4:
            s = pp[self.ok.grp.reindex(pp.index).to_numpy() == g]
            if len(s) == 0: continue
            W = self.E.W(s.index); nu, de = num(s).to_numpy(float), den(s).to_numpy(float)
            with np.errstate(invalid='ignore', divide='ignore'):
                out[g] = (nu.mean() / de.mean(), (W @ nu) / (W @ de), len(s), int(s.n_auth.sum()) if 'n_auth' in s else np.nan)
        return out

    def mean(self, pp, col):
        out = {}
        for g in G4:
            s = pp[self.ok.grp.reindex(pp.index).to_numpy() == g]
            v = (s[col] if isinstance(col, str) else col(s)).to_numpy(float); m = np.isfinite(v); s, v = s[m], v[m]
            if len(s) == 0: continue
            W = self.E.W(s.index)
            out[g] = (v.mean(), (W @ v) / W.sum(1), len(s), int(s.n_auth.sum()) if 'n_auth' in s else np.nan)
        return out

    # -------------------------------------------------- Stage 11
    def stage11(self):
        d = load_dir(R11 / 'raw/patch'); ly = [int(x) for x in d['layers']]
        k = load_dir(R11 / 'raw/knockout'); kl = [int(x) for x in k['layers']]
        assert (k['row_id'] == d['row_id']).all()
        cols = {'true': nlr(d['rank_true']), 'false': nlr(d['rank_false'])} | {f'p{l}': nlr(d['rank_patch'][:, i]) for i, l in enumerate(ly)} \
            | {f'k{l}': nlr(k['rank_ko'][:, i]) for i, l in enumerate(kl)}
        # X6 false_1..4 and X7 ko on false_0
        xf = {}
        for j in range(1, 5):
            z = load_dir(R13 / f'raw/xf_patch/false_{j}'); o = pd.Series(np.arange(len(z['row_id'])), index=z['row_id']).loc[d['row_id']].to_numpy()
            xf[j] = z; cols[f'x{j}_false'] = nlr(z['rank_false'][o]); cols[f'x{j}_true'] = nlr(z['rank_true'][o])
            for i, l in enumerate([int(x) for x in z['layers']]): cols[f'x{j}_p{l}'] = nlr(z['rank_patch'][o, i])
        kf = load_dir(R13 / 'raw/ko_false/false_0'); o = pd.Series(np.arange(len(kf['row_id'])), index=kf['row_id']).loc[d['row_id']].to_numpy()
        for i, l in enumerate([int(x) for x in kf['layers']]): cols[f'kf{l}'] = nlr(kf['rank_ko'][o, i])
        for who in ['unwritten', 'unwritten_first', 'unwritten_other', 'all authors']:
            pp = self.per_paper(d['row_id'], cols, who)
            den = lambda s: s['true'] - s['false']
            for l in ly:
                if l == 63: continue
                self.emit('11', 'E1 recovery', f'L{l}', who, self.ratio(pp, lambda s, l=l: s[f'p{l}'] - s['false'], den), 0, 0)
            for l in kl:
                if l == 64: continue
                self.emit('11', 'E2 loss', f'L{l}', who, self.ratio(pp, lambda s, l=l: s['k64'] - s[f'k{l}'], den), 0, 0)
                # X7 S = T - F
                rT = self.ratio(pp, lambda s, l=l: s['k64'] - s[f'k{l}'], den); rF = self.ratio(pp, lambda s, l=l: s['kf64'] - s[f'kf{l}'], den)
                self.emit('13', 'X7 S = T - F', f'L{l}', who, {g: (rT[g][0] - rF[g][0], rT[g][1] - rF[g][1], rT[g][2], rT[g][3]) for g in rT}, 0, 0)
            # X6: average over the 5 false titles of R(l)
            for l in [48, 50, 52, 56]:
                rs = [self.ratio(pp, lambda s, l=l: s[f'p{l}'] - s['false'], den)] + \
                     [self.ratio(pp, lambda s, l=l, j=j: s[f'x{j}_p{l}'] - s[f'x{j}_false'], lambda s, j=j: s[f'x{j}_true'] - s[f'x{j}_false']) for j in range(1, 5)]
                self.emit('13', 'X6 recovery (mean of 5 false titles)', f'L{l}', who,
                          {g: (np.mean([r[g][0] for r in rs]), np.mean([r[g][1] for r in rs], 0), rs[0][g][2], rs[0][g][3]) for g in rs[0]}, 0, 0)
            print('stage11', who, flush=True)

    def e4b(self):
        x = pd.read_parquet(R13 / 'summary_cpu_trainstd/perpaper_probe_spec.parquet')
        x = x[(x.source == 'E4b') & (x.split == 'group') & (x.excl == 'title-reuse') & ~x.dropped]
        for l, s in x.groupby('layer'):
            pp = s.set_index('paper_id')[['spec']]
            self.emit('11', 'E4b probe spec (per paper, all authors)', f'L{int(l)}', 'all authors (incl. written in C/D)', self.mean(pp, 'spec'), 0, 0,
                      'published version: training-fold standardised, team folds, title-reuse exclusion; per paper over all authors')

    # -------------------------------------------------- Stage 12
    def stage12(self):
        d = load_dir(R12 / 'raw/patch_pos'); items = [str(i) for i in d['items']]; ly = [int(x) for x in d['layers']]
        nt = nlr(d['rank_true']); Pz = nlr(d['rank_patch']); valid = d['valid']
        for who in ['unwritten', 'unwritten_first', 'unwritten_other']:
            for li, l in enumerate(ly):
                for it in ['p1', 'names', 'all']:
                    ii = items.index(it); ok = valid[:, ii]; none = Pz[:, li, items.index('none')]
                    pp = self.per_paper(d['row_id'][ok], {'num': (Pz[:, li, ii] - none)[ok], 'den': (nt - none)[ok]}, who)
                    self.emit('12', 'P1 single-position recovery', f'{it} L{l}', who, self.ratio(pp, lambda s: s['num'], lambda s: s['den']), 0, 0)
        d = load_dir(R12 / 'raw/patch_comp'); comps = [str(c) for c in d['comps']]; nt = nlr(d['rank_true']); Pc = nlr(d['rank_patch']); none = Pc[:, comps.index('none')]
        for who in ['unwritten', 'unwritten_first', 'unwritten_other']:
            for ci, c in enumerate(comps):
                if c == 'none' or int(c.lstrip('atnmlp')) < 40: continue
                pp = self.per_paper(d['row_id'], {'num': Pc[:, ci] - none, 'den': nt - none}, who)
                self.emit('12', 'P2 component recovery', c, who, self.ratio(pp, lambda s: s['num'], lambda s: s['den']), 0, 0)
        # N2 (all cohort, per token): pure / delete / true at the output
        z = load_dir(R12 / 'raw/prior_pure', ['row_id', 'final@63']); s10 = gc.load(gc.H / '10_stage10/351_stage10.py', 's10')
        ref = {}
        for c in ('true', 'delete'):
            zs = [np.load(s10.out_file(gc.R10, 'final', 63, k, c)) for k in range(72)]
            ref[c] = pd.Series(nlr(np.concatenate([q['rank'] for q in zs])), index=np.concatenate([q['row_id'] for q in zs]))
        cols = {'pure': nlr(z['final@63']), 'delete': ref['delete'].loc[z['row_id']].to_numpy(), 'true': ref['true'].loc[z['row_id']].to_numpy()}
        for who in ['unwritten', 'unwritten_first', 'unwritten_other']:
            pp = self.per_paper(z['row_id'], cols, who)
            for c in cols: self.emit('12', 'N2 output level', c, who, self.mean(pp, c), 0, 0, 'pure = name-only prompt; delete = no title; true = true title')
        # N1 (list level: the true list includes written authors for C/D)
        for c in ('delete', 'true'):
            x = pd.DataFrame({k: v for k, v in load_dir(R12 / 'raw/prior_mc' / c, ['paper_id', 'option', 'mean_nlr']).items()})
            w = x.pivot_table(index='paper_id', columns='option', values='mean_nlr').dropna()
            pp = pd.DataFrame({'margin': w[0] - w[[1, 2, 3]].mean(1), 'best': (w[0] >= w[[1, 2, 3]].max(1)).astype(float)})
            pp = pp[pp.index.isin(self.ok.index)]
            for m in ('margin', 'best'):
                self.emit('12', f'N1 {m} ({c} prompt)', 'list', 'whole list (incl. written in C/D)', self.mean(pp, m), 0, 0)
        # F2 author-prompt lens: spec = true - mean of 5 false
        base = R12 / 'raw/alens_read'; drop = set(json.loads((R12 / 'config/alens_eval_exclude.json').read_text())['paper_ids'])
        conds = [c for c in ['true'] + [f'false_{k}' for k in range(5)] if (base / c).exists()]
        zs = {c: load_dir(base / c) for c in conds}; keys = [k for k in zs['true'] if k.startswith('alens@')]
        rid = zs['true']['row_id']
        al = {}
        for c in conds:
            o = pd.Series(np.arange(len(zs[c]['row_id'])), index=zs[c]['row_id']).reindex(rid).to_numpy()
            al[c] = o
        for who in ['unwritten', 'unwritten_first', 'unwritten_other']:
            cols = {}
            for kk in keys:
                tr = nlr(zs['true'][kk]); fl = np.mean([nlr(zs[c][kk][al[c]]) for c in conds[1:]], 0); cols[kk] = tr - fl
            pp = self.per_paper(rid, cols, who); pp = pp[~pp.index.isin(drop)]
            for kk in keys:
                _, l, pos = kk.split('@')
                self.emit('12', 'F2 author-prompt lens spec', f'{pos} L{l}', who, self.mean(pp, kk), 0, 0)
        print('stage12 done', flush=True)

    # -------------------------------------------------- Stage 13 per paper
    def stage13(self):
        fw = self.ok.first_written
        # M2: held-out predictions of the 'recognised' probe; AUROC of group g vs B (plain), descriptive
        from sklearn.metrics import roc_auc_score
        for pos, l in [('title', 24), ('title', 40), ('colon', 52), ('colon', 63)]:
            f = R13 / f'summary_cpu_teamci/preds/true__{pos}__L{l}__recognised.npz'
            if not f.exists(): continue
            z = np.load(f, allow_pickle=True); pr = pd.Series(z['pred'].ravel(), index=z['paper_id']); pr = pr[pr.index.isin(self.ok.index)]
            g = self.ok.grp.reindex(pr.index)
            for a in ['A', 'C', 'D']:
                ia, ib = pr[g == a], pr[g == 'B']
                if len(ia) == 0: continue
                e = roc_auc_score(np.r_[np.ones(len(ia)), np.zeros(len(ib))], np.r_[ia, ib])
                # team bootstrap of AUROC (weighted Mann-Whitney)
                Wa, Wb = self.E.W(ia.index), self.E.W(ib.index); va, vb = ia.to_numpy(), ib.to_numpy()
                gt = (va[:, None] > vb[None, :]).astype(np.float32) + 0.5 * (va[:, None] == vb[None, :])
                boot = np.einsum('bi,ij,bj->b', Wa.astype(np.float32), gt, Wb.astype(np.float32)) / (Wa.sum(1) * Wb.sum(1))
                lo, hi = self.E.ci(boot)
                self.rows.append(dict(stage='13', measure='M2 recognised-probe AUROC vs B', item=f'{pos} L{l}', who='per paper', group=a, estimate=e, lo=lo, hi=hi,
                                      n_papers=len(ia), n_authors=np.nan, descriptive_only=True, note=f'n_B={len(ib)}; plain AUROC (no bin weighting); descriptive by plan'))
            mp = self.mean(pr.to_frame('pred'), 'pred')
            self.emit('13', 'M2 mean held-out probe prediction', f'{pos} L{l}', 'per paper', mp, 0, 0, 'descriptive')
        # X3 behaviour recovery (first author; papers whose first author was not written)
        x = pd.read_csv(R13 / 'summary_x3/x3_pairs.csv')
        x = x[x.include_primary & x.team.notna()].set_index('paper_id'); x = x[x.index.isin(self.ok.index)]
        x = x[fw.reindex(x.index) == False]                                                   # noqa: E712
        for part in ['test', 'all']:
            s = x if part == 'all' else x[x.split == 'test']
            self.emit('13', 'X3 behaviour recovery', f'{part} split', 'first author (not written)',
                      self.ratio(s, lambda q: q.score_paraphrase - q.score_lexical, lambda q: q.score_original - q.score_lexical), 0, 0)
            self.emit('13', 'X3 behaviour para - D', f'{part} split', 'first author (not written)', self.mean(s, lambda q: q.score_paraphrase - q.score_lexical), 0, 0)
        # X1 (first author) R_authors; X4 author@title D
        z = load_dir(R13 / 'raw/xpatch'); x1 = pd.DataFrame({k: v for k, v in z.items() if np.ndim(v) == 1}).set_index('paper_id')
        x1 = x1[x1.index.isin(self.ok.index)]; x1 = x1[fw.reindex(x1.index) == False]                # noqa: E712
        for part in ['test', 'all']:
            s = x1 if part == 'all' else x1[x1.split == 'test']
            for l in [24, 40, 48]:
                self.emit('13', 'X1 R_authors', f'L{l} {part}', 'first author (not written)', self.ratio(s, lambda q, l=l: q[f'authors@{l}'] - q.corrupt, lambda q: q.clean - q.corrupt), 0, 0)
        z = load_dir(R13 / 'raw/pscope'); x4 = pd.DataFrame({k: v for k, v in z.items() if np.ndim(v) == 1}).set_index('paper_id')
        x4 = x4[x4.index.isin(self.ok.index)]; x4 = x4[fw.reindex(x4.index) == False]                # noqa: E712
        for l in [8, 16, 24, 32, 40, 48]:
            self.emit('13', 'X4 author@title D = self - partner', f'L{l} all splits', 'first author (not written)',
                      self.mean(x4, lambda q, l=l: q[f'author@self@title@{l}'] - q[f'author@partner@title@{l}']), 0, 0)
        print('stage13 done', flush=True)


def main():
    for f in ('s1113_groups.csv', 's1113_contrasts.csv'):
        if (OUT / f).exists() and os.environ.get('GROUPS_OVERWRITE') != '1': raise SystemExit(f'{OUT / f} exists')
    S = S1113()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)
        for step in (S.stage11, S.e4b, S.stage12, S.stage13):
            try: step()
            except Exception as ex:                           # non-fatal: log and continue with the other measures
                import traceback; traceback.print_exc(); print(f'WARN step {step.__name__} failed: {ex!r}', flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(S.rows).to_csv(OUT / 's1113_groups.csv', index=False); pd.DataFrame(S.crows).to_csv(OUT / 's1113_contrasts.csv', index=False)
    print('wrote', len(S.rows), len(S.crows))


if __name__ == '__main__':
    main()
