"""Addendum 18b item 2 - step-2 sensitivity rerun with a FIXED window assignment. New file 2026-11-19.

Bug in a18b_item2.py (left unchanged, frozen): mask_fn_for() looked up ONE window per layer (`win_of(l)` = first window that
contains l). With the overlapping step-2 windows (L40-43, L42-45, ..., L60-63) every window except L40-43 was therefore cut
only in its last two layers (e.g. the config labelled L46-49 blocked L48-49). The main 6-window run (non-overlapping) is not
affected. Output of the buggy run: raw/a18b_item2_step2, summary_a18b_item2_step2 (INVALID, superseded by this file's output).

Fix: every config carries its window index explicitly (CFG_WIN[i] = (edge, window index) built from CONFIGS); for layer l the
mask cuts edge e in config i iff WINDOWS[w_i][0] <= l <= WINDOWS[w_i][1]. Everything else is a18b_item2.py unchanged
(prompts, edges, S definition, 600-paper sample a18b_config/sample600.parquet, 5 false titles, batch = all configs, analysis
rule): this module imports a18b_item2 and only replaces its mask_fn_for, window set and output paths.

Commands:
  work   [--shards S]           step-2 windows (11 x 5 + none = 56 configs) -> raw/a18b_item2_step2_fix/main/shard_XXX.npz
  parity [--shards 0]           step-4 windows (31 configs, as the main run) with the FIXED mask -> raw/a18b_item2_step2_fix/
                                parity_step4/ and compares ranks with stored raw/a18b_item2/main (WARN only)
  unittest                      CPU, tiny random model: blocked-layer sets per config (fixed step-2 = full windows; fixed
                                step-4 == old step-4), plus a tiny end-to-end work/skip/analyze run in a temp root
  remaining | analyze
"""
import argparse, json, os, sys, tempfile
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import a18b_common as A
import a18b_item2 as I2

W_STEP4 = [(a, a + 3) for a in range(40, 64, 4)]
W_STEP2 = [(a, a + 3) for a in range(40, 61, 2)]
RAW_FIX = A.R13 / 'raw/a18b_item2_step2_fix'
SUM_FIX = A.R13 / 'summary_a18b_item2_step2_fix'
_orig_mask_fn_for = I2.mask_fn_for


def configs_for(windows): return ['none'] + [f'{e}@L{a}-{b}' for (a, b) in windows for e in I2.EDGES]


def use(windows, raw, summ, winset):
    """point a18b_item2's module globals at a window set (compute()/analyze() read them at call time)."""
    I2.WINDOWS = list(windows); I2.CONFIGS = configs_for(windows); I2.RAW = Path(raw); I2.SUM = Path(summ); I2.WINSET = winset


def cfg_windows(configs, windows):
    """explicit (edge, window index) per config; None for 'none'."""
    lab = {f'L{a}-{b}': i for i, (a, b) in enumerate(windows)}; out = []
    for c in configs:
        if c == 'none': out.append(None); continue
        e, ws = c.split('@'); out.append((e, lab[ws]))
    return out


def mask_fn_for_fixed(C, T_len, L, n_name_inputs):
    torch = C.torch; n = len(L['ids']); tp = list(L['tpos'])
    S = {'title': tp, 'tail': list(range(max(tp) + 1, n - 1)), 'colon': [n - 1], 'name': list(range(n, n + n_name_inputs))}
    causal = torch.ones(T_len, T_len, dtype=torch.bool).tril(); blk = {}
    for e in I2.EDGES:
        q, k = e.split('<-'); b = torch.zeros(T_len, T_len, dtype=torch.bool)
        if S[q] and S[k]: b[torch.tensor(S[q])[:, None], torch.tensor(S[k])[None, :]] = True
        blk[e] = b
    neg = torch.finfo(C.dtype).min; cache = {}; CONF = list(I2.CONFIGS); WIN = list(I2.WINDOWS); CW = cfg_windows(CONF, WIN); B = len(CONF)
    def fn(layer):
        active = tuple(i for i, (a, b) in enumerate(WIN) if a <= layer <= b)  # ALL windows containing this layer
        if active not in cache:
            allow = causal[None].repeat(B, 1, 1)
            for i, cw in enumerate(CW):
                if cw is not None and cw[1] in active: allow[i] &= ~blk[cw[0]]
            mk = torch.zeros(B, 1, T_len, T_len, dtype=C.dtype); mk.masked_fill_(~allow[:, None], neg); cache[active] = mk
        return cache[active]
    return fn


I2.mask_fn_for = mask_fn_for_fixed  # compute() looks the name up at call time


def blocked_layers(maker, C, T_len, L, n_name):
    """{config: sorted layers where its mask row differs from plain causal} for the currently selected window set."""
    torch = C.torch; fn = maker(C, T_len, L, n_name); causal = torch.ones(T_len, T_len, dtype=torch.bool).tril()
    out = {c: [] for c in I2.CONFIGS}
    for l in range(64):
        mk = fn(l)
        for i, c in enumerate(I2.CONFIGS):
            if not torch.equal(mk[i, 0] == 0, causal): out[c].append(l)
    return out


# ------------------------------------------------------------------ commands
def work(a, C=None):
    use(W_STEP2, RAW_FIX, SUM_FIX, 'step2'); return I2.work(a, C=C)


def parity(a):
    use(W_STEP4, RAW_FIX / 'parity_step4', RAW_FIX / 'parity_step4_summary', 'step4')
    ns = argparse.Namespace(shards=a.shards or '0', max_minutes=a.max_minutes); I2.work(ns)
    res = {}
    for k in A.parse_shards(ns.shards, 24):
        f_new = I2.out_path(('main', k)); f_old = A.R13 / f'raw/a18b_item2/main/shard_{k:03d}.npz'
        if not (f_new.exists() and f_old.exists()): res[k] = 'missing'; continue
        zn, zo = np.load(f_new), np.load(f_old)
        assert list(zn['configs']) == list(zo['configs']) and (zn['row_id'] == zo['row_id']).all()
        r = {}
        for c in A.CONDS:
            n, o = zn[f'rank_{c}'], zo[f'rank_{c}']
            r[c] = dict(exact_share=float((n == o).mean()), max_abs_dnlr=float(np.abs(A.nlr(n) - A.nlr(o)).max()))
        exact = all(v['exact_share'] == 1.0 for v in r.values()); res[k] = dict(status='PASS (identical ranks)' if exact else 'WARN (not identical)', **r)
        print('A18B ITEM2 FIX PARITY shard', k, json.dumps(res[k]), flush=True)
    (RAW_FIX / 'parity_step4_result.json').write_text(json.dumps(res, indent=1))
    A.write_daily(f'{A.time.strftime("%H:%M")} a18b item 2 step-2 fix: parity (fixed mask, step-4 configs) shard(s) {ns.shards} vs stored main: '
                  + '; '.join(f'{k}: {v if isinstance(v, str) else v["status"]}' for k, v in res.items()) + f' (job {os.environ.get("SLURM_JOB_ID")})')


def unittest(a):
    import pandas as pd
    ok = {}; C = A.make_ctx(tiny=True)
    pid = A.sample().paper_id.iloc[0]; ai, rids, name = C.ctx[pid][0]; L = C.layout(pid, 'true'); T_len = len(L['ids']) + len(name) - 1
    # fixed step-2: every config blocks exactly its full window
    use(W_STEP2, '/nonexistent', '/nonexistent', 'step2')
    bl = blocked_layers(mask_fn_for_fixed, C, T_len, L, len(name) - 1)
    bad = {c: v for c, v in bl.items() if c != 'none' and v != list(range(int(c.split('@L')[1].split('-')[0]), int(c.split('-')[-1]) + 1))}
    ok['fixed step-2: blocked layers == full window, all 55 configs'] = not bad and len(bl) == 56
    ok['fixed step-2: none blocks nothing'] = bl['none'] == []
    for w in W_STEP2: print('FIXED step2', f'L{w[0]}-{w[1]}', bl[f'name<-title@L{w[0]}-{w[1]}'])
    old2 = blocked_layers(_orig_mask_fn_for, C, T_len, L, len(name) - 1)
    for w in W_STEP2: print('OLD   step2', f'L{w[0]}-{w[1]}', old2[f'name<-title@L{w[0]}-{w[1]}'])
    ok['old step-2 reproduces the bug (L46-49 -> [48, 49])'] = old2['name<-title@L46-49'] == [48, 49]
    # step-4 (non-overlapping): fixed == old, and == full window
    use(W_STEP4, '/nonexistent', '/nonexistent', 'step4')
    bf = blocked_layers(mask_fn_for_fixed, C, T_len, L, len(name) - 1); bo = blocked_layers(_orig_mask_fn_for, C, T_len, L, len(name) - 1)
    ok['step-4: fixed blocked-layer sets == old, all 31 configs'] = bf == bo and len(bf) == 31
    ok['step-4: == full windows'] = all(bf[f'{e}@L{a}-{b}'] == list(range(a, b + 1)) for (a, b) in W_STEP4 for e in I2.EDGES)
    # mask tensors themselves identical (fixed vs old) for step-4 at every layer
    ff = mask_fn_for_fixed(C, T_len, L, len(name) - 1); fo = _orig_mask_fn_for(C, T_len, L, len(name) - 1)
    ok['step-4: fixed mask tensors == old at every layer'] = all(C.torch.equal(ff(l), fo(l)) for l in range(64))
    # fixed step-2 row for window w equals old step-4 row when w is a step-4 window (same edge cut in the same layers)
    use(W_STEP2, '/nonexistent', '/nonexistent', 'step2'); f2 = mask_fn_for_fixed(C, T_len, L, len(name) - 1); c2 = list(I2.CONFIGS)
    use(W_STEP4, '/nonexistent', '/nonexistent', 'step4'); c4 = list(I2.CONFIGS)
    ok['fixed step-2 rows of L40-43..L60-63 == old step-4 rows (masks)'] = all(
        C.torch.equal(f2(l)[c2.index(c)], fo(l)[c4.index(c)]) for l in range(64) for c in c4)
    # tiny end-to-end (2 papers per shard, fixed step-2): work, skip-if-done, analyze; and the parity path
    root = Path(tempfile.mkdtemp(prefix='a18b_i2fix_tiny_', dir=os.environ.get('TMPDIR', '/tmp')))
    global RAW_FIX, SUM_FIX
    RAW_FIX, SUM_FIX = root / 'raw', root / 'summary'
    sm = A.sample(); I2._SMP['m'] = pd.concat([sm[sm.shard == k].head(2) for k in range(24)])
    ns = argparse.Namespace(shards="all", max_minutes=600); miss = work(ns, C=C); ok['tiny: all units written'] = not miss
    z = np.load(I2.out_path(('main', 0))); ok['tiny: 56 configs stored'] = z['rank_true'].shape[1] == 56 and list(z['configs']) == configs_for(W_STEP2)
    ok['tiny: blocking changes ranks'] = bool((z['rank_true'][:, 1:] != z['rank_true'][:, :1]).any())
    mt = I2.out_path(('main', 0)).stat().st_mtime; work(ns, C=C); ok['tiny: skip-if-done'] = I2.out_path(('main', 0)).stat().st_mtime == mt
    try: analyze(None); ok['tiny: analysis ran'] = (SUM_FIX / 'item2_step2_fix_report.md').exists()
    except Exception: import traceback; traceback.print_exc(); ok['tiny: analysis ran'] = False
    print('tiny root', root)
    for k, v in ok.items(): print('A18B ITEM2 FIX UNITTEST', 'PASS' if v else 'FAIL', k, flush=True)
    r = all(ok.values()); print('A18B ITEM2 FIX UNITTEST', 'PASS' if r else 'FAIL', flush=True); return r


def analyze(a=None):
    import pandas as pd
    use(W_STEP2, RAW_FIX, SUM_FIX, 'step2'); I2.analyze()
    CR = pd.read_csv(SUM_FIX / 'item2_criterion.csv'); n = sum(I2.out_path(u).exists() for u in I2.all_units())
    main = pd.read_csv(A.R13 / 'summary_a18b_item2/item2_criterion.csv').set_index('window')
    bug = A.R13 / 'summary_a18b_item2_step2/item2_criterion.csv'; bug = pd.read_csv(bug).set_index('window') if bug.exists() else None
    met = lambda v: not str(v).startswith('no single')
    par = RAW_FIX / 'parity_step4_result.json'; par = json.loads(par.read_text()) if par.exists() else {}
    L = ['# Addendum 18b item 2 — step-2 sensitivity (overlapping windows, step 2), FIXED window assignment', '',
         '**Supersedes `summary_a18b_item2_step2/` (INVALID: window-assignment bug).** In `a18b_item2.py` the attention mask for a layer was '
         'built for only the first window containing that layer, so with overlapping windows every window except L40-43 was cut in its last two '
         'layers only (the config labelled L46-49 blocked L48-49). This rerun (`a18b_item2_fix.py`) passes the window of each config explicitly and '
         'cuts the edge in all 4 layers of that window. Everything else is unchanged (addendum 18b item 2, locked; prompts, edges, S, 600-paper sample, '
         '5 false titles, batch of all configs, locked rule: largest-loss edge CI > 0 and paired difference to every other edge CI > 0, team bootstrap 2,000). '
         f'Raw: `raw/a18b_item2_step2_fix/main/` ({n}/24 shards). The main 6-window run (non-overlapping) is unaffected by the bug.', '']
    if par:
        L += ['**Parity check (WARN only):** fixed mask with the main-run 31 configs on shard(s) ' + ', '.join(par) + ' vs stored main run: '
              + '; '.join(f'shard {k}: {v if isinstance(v, str) else v["status"] + ", min exact-rank share " + format(min(x["exact_share"] for x in v.values() if isinstance(x, dict)), ".4f") + ", max |Δlog10(1/rank)| " + format(max(x["max_abs_dnlr"] for x in v.values() if isinstance(x, dict)), ".4f")}' for k, v in par.items()) + '.', '']
    L += ['## Per-window verdict (fixed) vs main run and vs the invalid run', '',
          '| window | largest-loss edge | loss [95% CI] | min lower CI of paired diffs | verdict (fixed) | main run (same window) | invalid buggy run |', '|---|---|---|---|---|---|---|']
    for r in CR.itertuples():
        mr = f'{main.loc[r.window, "verdict"]}' if r.window in main.index else '—'
        br = f'{bug.loc[r.window, "verdict"]}' if bug is not None and r.window in bug.index else '—'
        L.append(f'| {r.window} | {r.top_edge} | {r.top_loss:+.4f} [{r.top_lo:+.4f}, {r.top_hi:+.4f}] | {r.min_paired_diff_lo:+.4f} | {r.verdict} | {mr} | {br} |')
    nt = CR[CR.verdict.map(met) & (CR.top_edge == 'name<-title')].window.tolist(); other = CR[CR.verdict.map(met) & (CR.top_edge != 'name<-title')]
    same = [w for w in main.index if w in set(CR.window)]; agree = all(met(CR.set_index('window').loc[w, 'verdict']) == met(main.loc[w, 'verdict'])
                                                                    and CR.set_index('window').loc[w, 'top_edge'] == main.loc[w, 'top_edge'] for w in same if met(main.loc[w, 'verdict']))
    L += ['', '## Robustness of the main-run conclusion to window placement', '',
          f'- Main run (non-overlapping 4-layer windows): rule met for name ← title in {", ".join(w for w in main.index if met(main.loc[w, "verdict"]))}.',
          f'- Fixed step-2 run: rule met for name ← title in {len(nt)} of {len(CR)} windows: {", ".join(nt) or "none"}'
          + (f'; met for another edge in: ' + ', '.join(f'{r.window} ({r.top_edge})' for r in other.itertuples()) if len(other) else '; no window is won by another edge') + '.',
          f'- The 6 step-4 windows re-measured inside the step-2 batch reproduce the main-run verdicts: {"yes" if agree else "NO (see table)"} (batch size 56 vs 31 can shift bf16 values slightly).',
          '- Conclusion: see the summary line written by the analyst below.', '',
          '## Full step-2 table (generated by a18b_item2.analyze on the fixed raw data)', '']
    L += (SUM_FIX / 'item2_report.md').read_text().split('\n')[2:]
    (SUM_FIX / 'item2_step2_fix_report.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L[:40]))
    if a is not None and not A.TINY:
        A.write_daily(f'{A.time.strftime("%H:%M")} a18b item 2 step-2 FIX analysis: {n}/24 shards -> {SUM_FIX}/item2_step2_fix_report.md (job {os.environ.get("SLURM_JOB_ID")})')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['work', 'parity', 'unittest', 'remaining', 'analyze']); ap.add_argument('--shards'); ap.add_argument('--max-minutes', type=float, default=40)
    a = ap.parse_args()
    if a.cmd == 'unittest': sys.exit(0 if unittest(a) else 1)
    if a.cmd == 'analyze': analyze(a); return
    if a.cmd == 'remaining':
        use(W_STEP2, RAW_FIX, SUM_FIX, 'step2'); m = [u for u in I2.all_units(a.shards) if not I2.out_path(u).exists()]
        print(f'REMAINING {len(m)} of {len(I2.all_units(a.shards))}'); return
    A.check_addendum()
    if a.cmd == 'parity': parity(a); return
    work(a)


if __name__ == '__main__':
    main()
