"""Stage 13 X3 behaviour as a recovery ratio (user request 2026-10-31, task 3) + combined report with the text baseline (task 1).

recovery = (paraphrase - false) / (true - false), first-author teacher-forced score (mean log10(1/rank) of the first
author's name tokens; para_run, prompt 381_stage13.build(tok, title, 'authors', []):
   'Who are the authors of the paper titled "{t}"?\\nAuthors:'  - NO year).
"true"  = score_original (para_run).
"false" = Stage 10 false_0 would need the SAME prompt; Stage 10 (351_stage10.py PROMPT) is
   'Who are the authors of the paper titled "{title}" ({year})?\\nAuthors:'  - WITH the year, and a different scoring
   pipeline, so it is NOT used. Primary "false" = the lexical neighbour D's title in the X3 prompt (score_lexical);
   reference "false" = partner B (score_partner).
Group (target / control): pairs.parquet `group` (= Stage 11 config/sample.parquet `group` = Stage 10 cohort papers.parquet
   `group`; checked identical for all 1,178 pairs).
Estimator: ratio of means, (mean P - mean F) / (mean O - mean F), 95% team-cluster bootstrap (stage13_x3_analyze.team_w,
   SEED[(split, subset)], 2,000 draws on the whole set; group values from the same draws, so target - control is paired).
   Mean of per-paper ratios only if every |O - F| >= 0.1 (in log10-rank units); otherwise only the median is shown, with the
   share of papers whose denominator is <= 0 or < 0.1.
Outputs: summary_x3/x3_recovery.csv, reports/x3_textbase_recovery.md (also uses summary_x3/x3_textbase_*.csv, x3_gap.csv).
Usage: python stage13_x3_recovery.py [--out DIR]"""
import argparse, importlib.util, json
from pathlib import Path
import numpy as np, pandas as pd

H = Path.home() / 'jlens_work'; ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13')
SETS = {'primary': 'include_primary', 'sensitivity': 'include_sensitive'}; SUBSETS = ['all', 'd_matched']; SPLITS = ['tune', 'test', 'all']
FALSE = {'lexical_neighbour_D': 'score_lexical', 'partner_B': 'score_partner'}; SAFE = 0.1
WARN = []


def warn(m): WARN.append(m); print('WARN', m, flush=True)
def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
X3 = load(H / '13_stage13/stage13_x3_analyze.py', 'x3a')
def fm(e, lo, hi, d=3): return '-' if pd.isna(e) else f'{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]'


def recovery(df):
    rows = []
    for setn, col in SETS.items():
        for sub in SUBSETS:
            m0 = df[col].to_numpy() & df.team.notna().to_numpy()
            if sub == 'd_matched': m0 &= df.d_matched.to_numpy()
            for part in SPLITS:
                m = m0 if part == 'all' else m0 & (df.split == part).to_numpy()
                s = df[m]
                if len(s) < 2: continue
                W = X3.team_w(s.team.to_numpy(), X3.SEED[part, sub]); O = s.score_original.to_numpy(); P = s.score_paraphrase.to_numpy()
                for fname, fcol in FALSE.items():
                    F = s[fcol].to_numpy(); boot = {}
                    for grp in ('target', 'control', 'all'):
                        g = np.ones(len(s), bool) if grp == 'all' else (s.group == grp).to_numpy()
                        if g.sum() < 2: continue
                        Wg = W[:, g]; sw = Wg.sum(1)
                        with np.errstate(divide='ignore', invalid='ignore'):
                            mo, mp, mf = (Wg @ O[g]) / sw, (Wg @ P[g]) / sw, (Wg @ F[g]) / sw
                            br = (mp - mf) / (mo - mf)
                        boot[grp] = br
                        d = O[g] - F[g]; pr = (P[g] - F[g]) / np.where(d == 0, np.nan, d)
                        safe = bool((np.abs(d) >= SAFE).all())
                        r = dict(set=setn, subset=sub, split=part, false=fname, group=grp, n=int(g.sum()), n_teams=s.team[g].nunique(),
                                 true_mean=O[g].mean(), para_mean=P[g].mean(), false_mean=F[g].mean(),
                                 num=P[g].mean() - F[g].mean(), den=O[g].mean() - F[g].mean(),
                                 ratio=(P[g].mean() - F[g].mean()) / (O[g].mean() - F[g].mean()),
                                 share_den_le0=(d <= 0).mean(), share_den_small=(np.abs(d) < SAFE).mean(), median_paper_ratio=np.nanmedian(pr),
                                 mean_paper_ratio=np.nanmean(pr) if safe else np.nan, per_paper_safe=safe, boot_den_le0=float((mo - mf <= 0).mean()))
                        r['lo'], r['hi'] = X3.ci(br); r['num_lo'], r['num_hi'] = X3.ci(mp - mf); r['den_lo'], r['den_hi'] = X3.ci(mo - mf)
                        if r['boot_den_le0'] > 0: warn(f'{setn}/{sub}/{part}/{fname}/{grp}: denominator <= 0 in {r["boot_den_le0"]:.1%} of draws (CI unreliable)')
                        rows.append(r)
                    if 'target' in boot and 'control' in boot:
                        d = boot['target'] - boot['control']; t = [x for x in rows[-3:] if x['group'] in ('target', 'control')]
                        rows.append(dict(set=setn, subset=sub, split=part, false=fname, group='target_minus_control', n=len(s),
                                         ratio=t[0]['ratio'] - t[1]['ratio'], lo=X3.ci(d)[0], hi=X3.ci(d)[1]))
    return pd.DataFrame(rows)


def report(R, out, rep):
    TB = out / 'x3_textbase_gap.csv'; TR = out / 'x3_textbase_ratio.csv'
    L = ['# Stage 13 X3: text-model baseline and behaviour recovery ratio', '',
         'User request 2026-10-31 (tasks 1 and 3). Scripts: `13_stage13/stage13_x3_textbase.py` (+ .sbatch), `13_stage13/stage13_x3_recovery.py`. '
         'Data: X3 para_run (summary_x3/x3_pairs.csv, x3_cos_per_paper.csv.gz), paraphrases raw/para_gen, D = config/x3_lexical_neighbour_j2.csv. '
         'Intervals: 95% team-cluster bootstrap, 2,000 draws, the same seeds and draws as stage13_x3_analyze.py (so model-vs-Qwen differences are paired).', '']
    tb = None
    if TB.exists() and TR.exists():
        G = pd.read_csv(TB); RT = pd.read_csv(TR); meta = json.load(open(out / 'x3_textbase_meta.json')); tb = (G, RT)
        L += ['## Task 1: text-model baseline for G\'(l) = cos(orig, para) - cos(orig, D)', '',
              f'Each text (original title, Qwen paraphrase, lexical neighbour D, partner B) encoded alone, no prompt; {meta["n_papers"]} papers, {meta["n_texts"]} unique texts. '
              'bert-base-uncased: hidden layers 0..12 (L0 = embedding layer = the text baseline, analogous to Qwen L4), positions title_last (last wordpiece of the title; the token before [SEP], often the final "." when the title ends with one, as in Qwen), '
              'mean_title (mean of the title wordpieces) and cls. all-mpnet-base-v2: hidden layers 0..12, positions mean (the model\'s own pooling: mask-mean over all tokens incl. <s>, </s>), title_last, cls; '
              'layer "final" (13 in the CSV) = SentenceTransformer sentence embedding (identical in cosine to L12 mean: max |cos - 1| = ' + f'{meta["mpnet_final_check"]:.1e}). '
              'Qwen3-32B: title_last from X3 (base L4).', '',
              '**Caveat:** all-mpnet-base-v2 was trained (contrastively) on > 1 billion sentence pairs from large web and scientific corpora (incl. S2ORC title-abstract / citation pairs, SPECTER pairs), so it may have seen many of these titles, but it never saw author identities as a target. '
              'Raw cosine differences are not on a common scale across models (anisotropy, dimension), hence the ratio max_l (G\'(l) - G\'(base)) / G\'(base) as the scale-free comparison. '
              '[CLS] / <s> at L0 is the same vector for every text, so its G\'(L0) = 0 and the cls ratio is shown only relative to L1 (and is NaN for mpnet, whose <s> is still constant at L1).', '']
        if meta['warn']: L += ['WARN (textbase): ' + '; '.join(meta['warn']), '']
        def tab_layers(setn, sub, part):
            g = G[(G.set == setn) & (G.subset == sub) & (G.split == part) & (G.comparison == 'lex')]
            cols = [('bert-base-uncased', 'title_last'), ('bert-base-uncased', 'mean_title'), ('bert-base-uncased', 'cls'),
                    ('all-mpnet-base-v2', 'mean'), ('all-mpnet-base-v2', 'title_last')]
            hdr = ['BERT last', 'BERT mean', 'BERT cls', 'mpnet mean', 'mpnet last']
            o = [f'### {setn} / {sub} / {part}: G\'(l) and G\'(l) - G\'(L0)  (n = {g.n.iloc[0] if len(g) else 0})', '',
                 '| layer | ' + ' | '.join(f'{h} G\'' for h in hdr) + ' | ' + ' | '.join(f'{h} - L0' for h in hdr) + ' | BERT last - L1 | BERT mean - L1 |',
                 '|---' * (1 + 2 * len(hdr) + 2) + '|']
            for l in range(14):
                c1, c2 = [], []
                for mo, po in cols:
                    x = g[(g.model == mo) & (g.pos == po) & (g.layer == l)]
                    c1.append('-' if x.empty else f'{x.gap.iloc[0]:+.3f}'); c2.append('-' if x.empty else fm(x.gap_minus_base.iloc[0], x.dbase_lo.iloc[0], x.dbase_hi.iloc[0]))
                c3 = []
                for po in ('title_last', 'mean_title'):
                    x = g[(g.model == 'bert-base-uncased') & (g.pos == po) & (g.layer == l)]
                    c3.append('-' if x.empty else fm(x.gap_minus_base2.iloc[0], x.dbase2_lo.iloc[0], x.dbase2_hi.iloc[0]))
                if all(v == '-' for v in c1): continue
                L_ = 'final' if l == 13 else f'L{l}'
                o.append(f'| {L_} | ' + ' | '.join(c1) + ' | ' + ' | '.join(c2) + ' | ' + ' | '.join(c3) + ' |')
            q = g[(g.model == 'Qwen3-32B')]
            o += ['', f'Qwen3-32B title_last, same papers and draws (base L4): ' + '; '.join(f'L{int(r.layer)} G\' {r.gap:+.3f}, -L4 {fm(r.gap_minus_base, r.dbase_lo, r.dbase_hi)}' for r in q.itertuples()), '']
            return o
        L += tab_layers('primary', 'all', 'test') + tab_layers('primary', 'all', 'all') + tab_layers('sensitivity', 'all', 'test') + tab_layers('primary', 'd_matched', 'test') + tab_layers('primary', 'd_matched', 'all')
        L += ['### Scale-free comparison: ratio = max over l > base of (G\'(l) - G\'(base)) / G\'(base)', '',
              'argmax layer chosen on the point estimate; CI = team bootstrap at that fixed layer (re-maximised CI in the CSV). "Qwen - model" = paired difference of the ratios. Base "text_baseline" = L0 (BERT, mpnet) / L4 (Qwen); "next_layer" = L1 / L8.', '',
              '| set / subset / split | model | pos | base | G\'(base) | best layer | max (G\' - base) | ratio [CI] | Qwen - model [CI] |', '|---|---|---|---|---|---|---|---|---|']
        for setn, sub, part in (('primary', 'all', 'test'), ('primary', 'all', 'all'), ('sensitivity', 'all', 'test'), ('primary', 'd_matched', 'test'), ('primary', 'd_matched', 'all')):
            for r in RT[(RT.set == setn) & (RT.subset == sub) & (RT.split == part)].itertuples():
                bl = 'final' if r.best_layer == 13 and r.model != 'Qwen3-32B' else f'L{int(r.best_layer)}'
                L.append(f'| {setn}/{sub}/{part} | {r.model} | {r.pos} | {r.base_kind} (L{int(r.base_layer)}) | {r.gap_base:+.3f} | {bl} | {r.max_gap_minus_base:+.3f} | '
                         + fm(r.ratio, r.ratio_lo, r.ratio_hi, 2) + ' | ' + ('-' if r.model == 'Qwen3-32B' else fm(r.qwen_minus_model, r.qmm_lo, r.qmm_hi, 2)) + ' |')
        L.append('')
    else:
        L += ['## Task 1: text baseline outputs not found (x3_textbase_*.csv); run stage13_x3_textbase.sbatch first.', '']
    L += ['## Task 3: behaviour as a recovery ratio', '',
          '(paraphrase - false) / (true - false) on the first-author teacher-forced score (mean log10(1/rank) of the first author\'s name tokens). "true" = score_original from para_run.', '',
          '**Template check.** X3 para_run prompt (381_stage13.build(tok, title, \'authors\', [])): `Who are the authors of the paper titled "{t}"?\\nAuthors:` (no year). '
          'Stage 10 false_0 prompt (351_stage10.py PROMPT): `Who are the authors of the paper titled "{title}" ({year})?\\nAuthors:` (with the year). They differ, so the Stage 10 false_0 score is **not** used. '
          '"false" = the lexical neighbour D\'s title in the X3 prompt (score_lexical, primary); partner B (score_partner) shown for reference.', '',
          'Group (target / control) = `pairs.parquet` column `group` (identical to Stage 11 `config/sample.parquet` `group` and Stage 10 `cohort/papers.parquet` `group` for all 1,178 pairs). '
          f'Estimator: ratio of means; team-cluster CI. Mean of per-paper ratios only if every |true - false| >= {SAFE} (otherwise "-"; the median and the share of small/negative denominators are given).', '']
    if WARN: L += ['WARN (recovery): ' + '; '.join(WARN), '']
    L += ['| set | subset | split | false | group | n | true | para | false | ratio of means [CI] | share den <= 0 | share \\|den\\| < 0.1 | median per-paper | mean per-paper |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for r in R.itertuples():
        if r.split == 'tune': continue
        if r.group == 'target_minus_control':
            L.append(f'| {r.set} | {r.subset} | {r.split} | {r.false} | target - control | | | | | {fm(r.ratio, r.lo, r.hi)} | | | | |'); continue
        L.append(f'| {r.set} | {r.subset} | {r.split} | {r.false} | {r.group} | {r.n} | {r.true_mean:+.3f} | {r.para_mean:+.3f} | {r.false_mean:+.3f} | {fm(r.ratio, r.lo, r.hi)} | '
                 f'{r.share_den_le0:.2f} | {r.share_den_small:.2f} | {r.median_paper_ratio:+.2f} | ' + ('-' if pd.isna(r.mean_paper_ratio) else f'{r.mean_paper_ratio:+.2f}') + ' |')
    L += ['', '(Tune rows in x3_recovery.csv.)', '', '## Conclusion', '', '<!--CONCLUSION-->', '']
    rep.write_text('\n'.join(L) + '\n'); print('\n'.join(L))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out'); a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / 'summary_x3'; rep = (out / 'x3_textbase_recovery.md') if a.out else ROOT / 'reports/x3_textbase_recovery.md'
    df = pd.read_csv(ROOT / 'summary_x3/x3_pairs.csv')
    for c in ('include_primary', 'include_sensitive', 'd_matched'): df[c] = df[c].astype(bool)
    pq = pd.read_parquet(ROOT / 'config/pairs.parquet').set_index('paper_id')
    bad = (df.group != df.paper_id.map(pq.group)).sum()
    if bad: warn(f'{bad} rows: x3_pairs group != pairs.parquet group')
    R = recovery(df); out.mkdir(parents=True, exist_ok=True); R.to_csv(out / 'x3_recovery.csv', index=False)
    report(R, ROOT / 'summary_x3', rep)


if __name__ == '__main__':
    main()
