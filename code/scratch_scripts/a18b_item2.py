"""Addendum 18b item 2 - windowed attention blocking (GPU driver + CPU analysis). New file 2026-11-17.

Design (addendum 18b item 2, locked; lock amendment 2: the 6 non-overlapping windows on 600 papers; the step-2 sensitivity
(11 windows) only if this run measures under budget):
  windows   L40-43, L44-47, L48-51, L52-55, L56-59, L60-63 (4 layers each)
  edges     one edge cut (all heads) inside the window only:  name<-title, name<-tail, tail<-title, ':'<-title, name<-':'
            title = title token positions (Stage 11 rule), tail = prompt tokens after the title before ':' (closing quote, year,
            ')?\\n', 'Authors'), ':' = last prompt token, name = name inputs after ':' (teacher forcing).
  baseline  'none' = the same explicit causal 4D mask with nothing blocked (as Stage 11 E2 l = 64).
  readout   S = T - F at the final output (name tokens; F = mean of the 5 false titles; each title condition run with its own
            positions); loss = S(none) - S(config); target / control separately and within-bin T - C.
  rule      (locked) an edge whose S loss in a window has CI > 0 AND is larger than the losses of the other edges in the same
            window -> "the information in that window travels over this edge". Implemented: largest point loss with CI > 0 and
            the paired difference to every other edge of that window with CI > 0.
  intervals author-team cluster bootstrap, 2,000 draws, paired. Stored E2 / E2n / X7 are the "block from layer l on" reference.
Units ('main', k) (k = 0..23, 25 papers) -> raw/a18b_item2/main/shard_XXX.npz ; window set 'step4' (default) | 'step2' (env A18B_WIN2=step2).
Commands: work [--shards S] | remaining | tiny --root DIR | analyze
"""
import argparse, json, os, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a18b_common as A

WINSET = os.environ.get('A18B_WIN2', 'step4')
WINDOWS = [(a, a + 3) for a in range(40, 64, 4)] if WINSET == 'step4' else [(a, a + 3) for a in range(40, 61, 2)]
EDGES = ['name<-title', 'name<-tail', 'tail<-title', 'colon<-title', 'name<-colon']
CONFIGS = ['none'] + [f'{e}@L{a}-{b}' for (a, b) in WINDOWS for e in EDGES]
RAW = Path(os.environ.get('A18B_RAW2', A.R13 / ('raw/a18b_item2' + ('' if WINSET == 'step4' else '_step2'))))
SUM = Path(os.environ.get('A18B_SUM2', A.R13 / ('summary_a18b_item2' + ('' if WINSET == 'step4' else '_step2'))))
_SMP = {}


def smp():
    if 'm' not in _SMP: _SMP['m'] = A.sample()
    return _SMP['m']


def out_path(u): return RAW / u[0] / f'shard_{u[1]:03d}.npz'
def all_units(shards=None): return [('main', k) for k in A.parse_shards(shards, 24)]


def mask_fn_for(C, T_len, L, n_name_inputs):
    torch = C.torch; n = len(L['ids']); tp = list(L['tpos'])
    S = {'title': tp, 'tail': list(range(max(tp) + 1, n - 1)), 'colon': [n - 1], 'name': list(range(n, n + n_name_inputs))}
    causal = torch.ones(T_len, T_len, dtype=torch.bool).tril(); blk = {}
    for e in EDGES:
        q, k = e.split('<-'); b = torch.zeros(T_len, T_len, dtype=torch.bool)
        if S[q] and S[k]: b[torch.tensor(S[q])[:, None], torch.tensor(S[k])[None, :]] = True
        blk[e] = b
    neg = torch.finfo(C.dtype).min; cache = {}; B = len(CONFIGS)
    def win_of(l):
        for i, (a, b) in enumerate(WINDOWS):
            if a <= l <= b: return i
        return None
    def fn(layer):
        w = win_of(layer)
        if w not in cache:
            allow = causal[None].repeat(B, 1, 1)
            if w is not None:
                for i, cfg in enumerate(CONFIGS):
                    if cfg == 'none': continue
                    e, ws = cfg.split('@')
                    if ws == f'L{WINDOWS[w][0]}-{WINDOWS[w][1]}': allow[i] &= ~blk[e]
            mk = torch.zeros(B, 1, T_len, T_len, dtype=C.dtype); mk.masked_fill_(~allow[:, None], neg); cache[w] = mk
        return cache[w]
    return fn


def compute(C, u):
    torch = C.torch; sm = smp(); papers = sm[sm.shard == u[1]].paper_id.tolist(); out = {c: [] for c in A.CONDS}; rows = []
    for pid in papers:
        for ai, rids, name in C.ctx[pid]:
            rows += rids; gold = torch.tensor(name, device=C.model.input_device)
            for cond in A.CONDS:
                L = C.layout(pid, cond); T = L['ids'] + name[:-1]; pos = [len(L['ids']) - 1 + j for j in range(len(name))]
                lg = A.final_logits(C, T, pos, batch=len(CONFIGS), mask_fn=mask_fn_for(C, len(T), L, len(name) - 1))
                out[cond].append(np.stack([A.ranks(lg[i], gold, torch) for i in range(len(CONFIGS))], 1))
    d = dict(row_id=np.array(rows), configs=np.array(CONFIGS), **{f'rank_{c}': np.concatenate(v) for c, v in out.items()})
    import a18b_item4 as I4
    return d, dict(check=I4.check_vs_e1(d))


def work(a, C=None):
    miss, C = A.work(all_units(a.shards), out_path, compute, a.max_minutes, C=C, tiny=A.TINY, tag='a18b_item2'); return miss


def analyze(a=None):
    import pandas as pd
    A.check_addendum(); B = A.Boot(); SUM.mkdir(parents=True, exist_ok=True)
    have = [out_path(u) for u in all_units() if out_path(u).exists()]; Z = [np.load(f) for f in have]
    tk = pd.read_parquet(A.R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id']).set_index('row_id').paper_id
    rid = np.concatenate([z['row_id'] for z in Z]); pid = tk.reindex(rid).to_numpy()
    PM = {c: pd.DataFrame(A.nlr(np.concatenate([z[f'rank_{c}'] for z in Z])), columns=CONFIGS).groupby(pid).mean() for c in A.CONDS}
    pids = PM['true'].index.to_numpy(); g = B.meta.group_tight.reindex(pids).to_numpy()
    S = PM['true'] - sum(PM[c] for c in A.FALSES) / 5
    rows, boots = [], {}
    e0, b0 = B.mean(pids, S['none'].to_numpy())
    for cfg in CONFIGS[1:]:
        v = (S['none'] - S[cfg]).to_numpy(); e, b = B.mean(pids, v); et, bt = B.mean(pids[g == 'target'], v[g == 'target']); ec, bc = B.mean(pids[g == 'control'], v[g == 'control'])
        t, tb, _ = B.tc(pids, v); boots[cfg] = b
        per = [((PM['true']['none'] - PM[f]['none']) - (PM['true'][cfg] - PM[f][cfg])).mean() for f in A.FALSES]
        ed, w = cfg.split('@')
        rows.append(dict(window=w, edge=ed, loss=e, lo=B.ci(b)[0], hi=B.ci(b)[1], share_of_S=e / e0, target=et, t_lo=B.ci(bt)[0], t_hi=B.ci(bt)[1],
                         control=ec, c_lo=B.ci(bc)[0], c_hi=B.ci(bc)[1], tc=t, tc_lo=B.ci(tb)[0], tc_hi=B.ci(tb)[1], loss_min_false=min(per), loss_max_false=max(per)))
    T = pd.DataFrame(rows); crit = []
    for w, x in T.groupby('window', sort=False):
        top = x.sort_values('loss', ascending=False).iloc[0]; diffs = []
        for r in x.itertuples():
            if r.edge == top.edge: continue
            bb = boots[f'{top.edge}@{w}'] - boots[f'{r.edge}@{w}']; diffs.append((r.edge, float(top.loss - r.loss), *B.ci(bb)))
        ok = top.lo > 0 and all(d[2] > 0 for d in diffs)
        crit.append(dict(window=w, top_edge=top.edge, top_loss=top.loss, top_lo=top.lo, top_hi=top.hi,
                         min_paired_diff_lo=min(d[2] for d in diffs), vs=';'.join(f'{d[0]} {d[1]:+.4f} [{d[2]:+.4f}, {d[3]:+.4f}]' for d in diffs),
                         verdict=f'information in {w} travels over {top.edge}' if ok else 'no single edge (rule not met)'))
    CR = pd.DataFrame(crit); T.to_csv(SUM / 'item2_table.csv', index=False); CR.to_csv(SUM / 'item2_criterion.csv', index=False)
    f = lambda e, lo, hi: f'{e:+.4f} [{lo:+.4f}, {hi:+.4f}]' + ('*' if (lo > 0 or hi < 0) else '')
    chk = [json.loads(str(z['meta'])).get('check', {}) for z in Z]
    L = ['# Addendum 18b item 2 — windowed attention blocking' + ('' if WINSET == 'step4' else ' (step-2 sensitivity, 11 windows)'), '',
         f'**Pre-registered (addendum 18b, locked 2026-11-17, sha256 {A.ADDENDUM_SHA[:12]}…); decision rule fixed by the lock.** 600-paper subsample (seed {A.SEED}); '
         f'{len(have)}/24 shards, {len(pids)} papers. One edge (all heads) cut inside one 4-layer window; S = true − mean of 5 false titles (final output, paper means of '
         f'log10(1/rank)); loss = S(none) − S(config); S(none) = {f(e0, *B.ci(b0))}. Author-team cluster bootstrap 2,000 draws (paired); T − C within citation bin. * = CI excludes 0.', '',
         '## Rule per window', '', '| window | largest-loss edge | loss | paired difference to the other edges | verdict |', '|---|---|---|---|---|']
    for r in CR.itertuples(): L.append(f'| {r.window} | {r.top_edge} | {f(r.top_loss, r.top_lo, r.top_hi)} | {r.vs} | {r.verdict} |')
    L += ['', '## All cells', '', '| window | edge | loss (all) | share of S | target | control | T − C | min / max over false titles |', '|---|---|---|---|---|---|---|---|']
    for r in T.itertuples():
        L.append(f'| {r.window} | {r.edge} | {f(r.loss, r.lo, r.hi)} | {r.share_of_S:.3f} | {f(r.target, r.t_lo, r.t_hi)} | {f(r.control, r.c_lo, r.c_hi)} | {f(r.tc, r.tc_lo, r.tc_hi)} | {r.loss_min_false:+.4f} / {r.loss_max_false:+.4f} |')
    L += ['', 'Reference ("block from layer l on", stored): Stage 11 E2 loss 0.14 (L40) → 0.06 (L48) → 0 (L52 on); E2n ≤ 0.15, 0 by L52; X7 (5 false titles) in summary_x7.',
          '', '## Checks (WARN only)', '', f'- unblocked true / false_0 ranks (explicit-mask baseline) vs stored Stage 11 E1 rows (default mask): '
          + str(pd.Series([c.get('status') for c in chk]).value_counts().to_dict()) + f'; min exact share true {min([c.get("eq_true", 1) for c in chk]):.3f}, false_0 {min([c.get("eq_false0", 1) for c in chk]):.3f} (threshold 0.95).']
    (SUM / 'item2_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L))


def tiny(a):
    global RAW, SUM
    import pandas as pd
    root = Path(a.root); RAW = root / 'raw'; SUM = root / 'summary'; ok = {}
    C = A.make_ctx(tiny=True); sm = A.sample(); _SMP['m'] = pd.concat([sm[sm.shard == k].head(2) for k in range(24)])
    ns = argparse.Namespace(shards='all', max_minutes=600); miss = work(ns, C=C); ok['all units written'] = not miss
    z = np.load(out_path(('main', 0))); R = z['rank_true']
    ok['configs'] = R.shape[1] == len(CONFIGS)
    pid = _SMP['m'][_SMP['m'].shard == 0].paper_id.iloc[0]; ai, rids, name = C.ctx[pid][0]; Lt = C.layout(pid, 'true')
    r0 = A.ranks(A.final_logits(C, Lt['ids'] + name[:-1], [len(Lt['ids']) - 1 + j for j in range(len(name))])[0], C.torch.tensor(name), C.torch)
    ok['none (explicit mask) = default causal run (fp32)'] = bool((R[:len(name), 0] == r0).all())
    ok['blocking changes ranks'] = bool((R[:, 1:] != R[:, :1]).any())
    # name<-* edges cannot change the first name token (predicted at ':')
    first = np.zeros(len(R), bool); i = 0
    for pid in _SMP['m'][_SMP['m'].shard == 0].paper_id:
        for ai, rids, name in C.ctx[pid]: first[i] = True; i += len(rids)
    nm = [j for j, c in enumerate(CONFIGS) if c.startswith('name<-')]
    # tolerance: +-1 rank (fp32 batch-kernel near-ties; tiny run 11952307 had 1 of 15 x 5 values off by one rank)
    ok['name<- edges leave the first token unchanged (+-1 rank)'] = bool((np.abs(R[first][:, nm].astype(np.int64) - R[first][:, :1]) <= 1).all())
    mt = out_path(('main', 0)).stat().st_mtime; work(ns, C=C); ok['skip-if-done'] = out_path(('main', 0)).stat().st_mtime == mt
    try: analyze(); ok['analysis ran'] = (SUM / 'item2_report.md').exists()
    except Exception: import traceback; traceback.print_exc(); ok['analysis ran'] = False
    for k, v in ok.items(): print('A18B ITEM2 TINY CHECK', 'PASS' if v else 'FAIL', k, flush=True)
    r = all(ok.values()); print('A18B ITEM2 TINY', 'PASS' if r else 'FAIL', flush=True); return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'remaining', 'tiny', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    ap.add_argument('--root'); a = ap.parse_args()
    if a.cmd == 'tiny': sys.exit(0 if tiny(a) else 1)
    if a.cmd == 'analyze': analyze(a); return
    if a.cmd == 'remaining':
        m = [u for u in all_units(a.shards) if not out_path(u).exists()]; print(f'REMAINING {len(m)} of {len(all_units(a.shards))}'); return
    A.check_addendum(); work(a)


if __name__ == '__main__':
    main()
