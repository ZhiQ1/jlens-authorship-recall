"""Batch 2 group A: unit tests of every hard check (identical input -> PASS, perturbed input -> FAIL), CPU, real data where possible.
  H1   addendum 11 A hard check 1 (rel. norm, tol 0.05): raw/allTok_L63 shard 0 vs itself; vs +10% / noise perturbation
  H2   addendum 11 A hard check 2 (stage13_b2_np_lens.hard_check2): Stage 10 lens table of shards 0-1 vs published per-paper
       values -> PASS; spec5 + 0.01 -> FAIL; one paper's spec5 + 1.0 (a mean shift > 0.005) -> FAIL
  P1   2-7 hard check: stage13_b2_ps_analyze.d_table on the PUBLISHED raw/pscope (all 24 shards) reproduces the published
       x4_decodability.csv (title rows) -> PASS (validates the re-implemented estimator on real data); self + 0.01 -> FAIL;
       a missing reference row -> FAIL; named value test/author/title/L8 0.046 -> PASS, +0.006 -> FAIL
  P2   2-9 hard check: stage13_b2_ps_analyze.x4tok on the PUBLISHED followup/x4tok2 (b7) reproduces x4_rolesplit.csv (L8, L40)
       -> PASS; self tokens + 0.01 -> FAIL; n mismatch -> FAIL
Exit 0 only if every test behaves as expected. Output: summary_b2A_hcunit.json in 381_stage13/b2_np_tiny/.
"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; B = Path('/scratch/zhang.zhiqi2/jlens'); R10 = B / '351_stage10'; R13 = B / '381_stage13'


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


K = load(H / '13_stage13/stage13_b2A_cols.py', 'b2A_cols'); CK = load(H / '13_stage13/stage13_b2A_checks.py', 'b2A_checks')
res = []
def expect(name, got, want):
    ok = got['status'] == want; res.append(dict(test=name, expected=want, got=got['status'], ok=ok, detail={k: v for k, v in got.items() if k not in ('parts', 'info')}))
    print(('OK  ' if ok else 'BAD '), name, '-> expected', want, 'got', got['status'], json.dumps({k: v for k, v in got.items() if k in ('rel_max', 'max_abs_diff', 'abs_diff', 'n', 'n_missing')}, default=str), flush=True)


# ---------------- H1
z = np.load(R13 / 'raw/allTok_L63/shard_000.npz'); X = z['resid'][:500]
expect('H1 identical', CK.rel_norm_check(X, X, K.NP_HARD1_TOL), 'PASS')
expect('H1 +10% scale', CK.rel_norm_check((X.astype(np.float32) * 1.1).astype(np.float16), X, K.NP_HARD1_TOL), 'FAIL')
rng = np.random.default_rng(0); Xn = X.astype(np.float32); Xn[7] += rng.standard_normal(Xn.shape[1]).astype(np.float32) * np.linalg.norm(Xn[7]) * 0.1 / np.sqrt(Xn.shape[1])
expect('H1 one row +10% noise', CK.rel_norm_check(Xn, X, K.NP_HARD1_TOL), 'FAIL')
expect('H1 bf16-level noise (1e-3 rel)', CK.rel_norm_check(X.astype(np.float32) * (1 + 1e-3), X, K.NP_HARD1_TOL), 'PASS')
expect('H1 shape mismatch', CK.rel_norm_check(X[:10], X[:11], K.NP_HARD1_TOL), 'FAIL')

# ---------------- H2
NL = load(H / '13_stage13/stage13_b2_np_lens.py', 'np_lens')
papers = pd.read_parquet(R10 / 'cohort/papers.parquet', columns=['paper_id', 'group_tight', 'citation_bin', 'shard'])
tok = pd.read_parquet(R10 / 'cohort/name_tokens.parquet', columns=['row_id', 'paper_id', 'shard', 'author_index', 'token_index', 'token_id', 'role'])
tok = tok[tok.shard.isin([0, 1])].reset_index(drop=True)
ranks = NL.S10L.load_ranks(tok, readouts=[(ro, l) for ro in K.NP_LENS_READOUTS for l in K.NP_HARD2_LAYERS], conds=K.CONDS)
LT = NL.lens_table(tok, ranks, K.NP_HARD2_LAYERS, K.NP_LENS_READOUTS)
expect('H2 identical (Stage 10 ranks vs published per-paper)', NL.hard_check2(LT, papers, full=False), 'PASS')
expect('H2 spec5 + 0.01', NL.hard_check2(LT.assign(spec5=LT.spec5 + 0.01), papers, full=False), 'FAIL')
LT2 = LT.copy(); i = LT2.index[(LT2.run == 'surname_first') & (LT2.readout == 'logit') & (LT2.layer == 40)][0]; LT2.loc[i, 'spec5'] += 1.0
expect('H2 one paper spec5 + 1.0 (surname_first logit L40)', NL.hard_check2(LT2, papers, full=False), 'FAIL')

# ---------------- P1 / P2 (published raw -> published csv)
PA = load(H / '13_stage13/stage13_b2_ps_analyze.py', 'ps_an')
pairs = pd.read_parquet(R13 / 'config/pairs.parquet'); cbin = papers[['paper_id', 'citation_bin']]
zs = [np.load(f) for f in sorted((R13 / 'raw/pscope').glob('shard_*.npz'))]
ref = pd.concat([pd.DataFrame({c: z[c] for c in z.files if c != 'meta'}) for z in zs]).merge(pairs[['paper_id', 'team', 'split', 'group']], on='paper_id').merge(cbin, on='paper_id', how='left')
pub = pd.read_csv(R13 / 'summary_x1x4/x4_decodability.csv'); keys = ['split', 'answer', 'pos', 'layer']
D = PA.d_table(ref, K.PS_LAYERS).rename(columns={'src': 'pos'})
expect('P1 d_table(published raw) == published x4_decodability (title)', CK.value_table_check(D[D.pos == 'title'], pub[pub.pos == 'title'], keys, 'D', K.PS_HARD_TOL), 'PASS')
ci_diff = D.merge(pub, on=keys, suffixes=('', '_p')); print('    (info) CI bounds identical too: max |lo diff|', float((ci_diff.lo - ci_diff.lo_p).abs().max()), 'max |hi diff|', float((ci_diff.hi - ci_diff.hi_p).abs().max()))
ref2 = ref.copy(); c = [x for x in ref2.columns if '@self@title@' in x]; ref2[c] = ref2[c] + 0.01
D2 = PA.d_table(ref2, K.PS_LAYERS).rename(columns={'src': 'pos'})
expect('P1 self + 0.01', CK.value_table_check(D2[D2.pos == 'title'], pub[pub.pos == 'title'], keys, 'D', K.PS_HARD_TOL), 'FAIL')
expect('P1 missing row', CK.value_table_check(D[(D.pos == 'title') & ~((D.layer == 8) & (D.split == 'test') & (D.answer == 'author'))], pub[pub.pos == 'title'], keys, 'D', K.PS_HARD_TOL), 'FAIL')
r = K.PS_HARD_REF; v = float(D[(D.split == r['split']) & (D.answer == r['answer']) & (D.pos == r['pos']) & (D.layer == r['layer'])].D.iloc[0])
expect('P1 named value', CK.scalar_check(v, r['D'], K.PS_HARD_TOL), 'PASS')
expect('P1 named value + 0.006', CK.scalar_check(v + 0.006, r['D'], K.PS_HARD_TOL), 'FAIL')
x4o = pd.concat([pd.read_csv(f) for f in sorted((R13 / 'followup/x4tok2').glob('shard_*.csv'))]); x4o = x4o[x4o.batch == 'b7']
R4 = x4o.rename(columns={'source': 'who', 'token_j': 'ans_j', 'role': 'ans_role'}).assign(target='author', src_kind='title')
ps = pd.read_csv(R13 / 'summary_x1x4/x4_textbase2_perpaper.csv').set_index('paper_id')
pubR = pd.read_csv(R13 / 'summary_x1x4/x4_rolesplit.csv'); pubR = pubR[pubR.measure == 'qwen']; pubR['layer'] = pubR.layer.astype(int)
XT = PA.x4tok(R4, ps, K.X4TOK_HARD_LAYERS, srcs=('title',))
expect('P2 x4tok(published x4tok2 b7) == published x4_rolesplit', CK.value_table_check(XT, pubR, ['layer', 'role'], 'mean', K.PS_HARD_TOL), 'PASS')
cc = XT.merge(pubR, on=['layer', 'role'], suffixes=('', '_p')); print('    (info) rolesplit CI identical: max |lo diff|', float((cc.lo - cc.lo_p).abs().max()))
expect('P2 n equal', CK.value_table_check(XT, pubR, ['layer', 'role'], 'n', 0), 'PASS')
R4b = R4.copy(); R4b.loc[R4b.who == 'self', 'nlr'] += 0.01
expect('P2 self tokens + 0.01', CK.value_table_check(PA.x4tok(R4b, ps, K.X4TOK_HARD_LAYERS, srcs=('title',)), pubR, ['layer', 'role'], 'mean', K.PS_HARD_TOL), 'FAIL')
expect('P2 n mismatch', CK.value_table_check(XT.assign(n=XT.n - 1), pubR, ['layer', 'role'], 'n', 0), 'FAIL')

ok = all(x['ok'] for x in res)
out = R13 / 'b2_np_tiny/summary_b2A_hcunit.json'; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(res, indent=1, default=str))
print(f'HARD-CHECK UNIT TESTS {"ALL OK" if ok else "SOME FAILED"}: {sum(x["ok"] for x in res)}/{len(res)}', flush=True)
sys.exit(0 if ok else 1)
