"""X3 prereg addendum 5 (2026-10-30, user-approved): lexical neighbour D chosen with the corrected word overlap (jaccard2)
and the inclusion table for the two X3 analyses. CPU only; run BEFORE para_run (381_stage13.py reads the output if it exists).

jaccard2 = stage13_para_nli.words2/jac: lowercase, punctuation -> space, sklearn English stop words removed, tokens of any
length, light suffix stemming. D rule unchanged otherwise (addendum 4): a different paper of the same field, no shared
surname, jaccard2(A, D) >= jaccard2(A, paraphrase), the closest above; else the highest available.

Output config/x3_lexical_neighbour_j2.csv, one row per paraphrase (1,186):
  paper_id, para_jaccard2, lexical_neighbour_j2, lexical_jaccard2, d_matched (D's overlap >= the paraphrase's),
  identical, auto_ok, nli_both, manual_label (40 reviewed items, else ''),
  include_primary   = auto_ok and not identical
  include_sensitive = include_primary and nli_both and manual_label != 'changed'
Usage: python stage13_x3_neighbour_j2.py [--tiny]   (--tiny: 20 papers, writes to followup_tiny/)"""
import hashlib, importlib.util, sys
from pathlib import Path
import pandas as pd

H = Path.home() / 'jlens_work'; ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); R10 = Path('/scratch/zhang.zhiqi2/jlens/351_stage10')
TINY = '--tiny' in sys.argv
OUT = (ROOT / 'followup_tiny' if TINY else ROOT / 'config') / 'x3_lexical_neighbour_j2.csv'
sp = importlib.util.spec_from_file_location('pnli', H / '13_stage13/stage13_para_nli.py'); pnli = importlib.util.module_from_spec(sp); sp.loader.exec_module(pnli)


def main():
    papers = pd.read_parquet(R10 / 'cohort/papers.parquet'); P = papers.set_index('paper_id')
    d = pd.read_csv(ROOT / 'summary_x3/para_nli.csv')
    if TINY: d = d.head(20)
    lab = pd.concat([pd.read_csv(ROOT / f'logs/{f}')[['paper_id', 'human_label']] for f in
                     ('para_review_sample20_labels.csv', 'para_review_sample20_b_labels.csv')])
    assert lab.paper_id.is_unique, 'a paper was labelled twice'
    lab = dict(zip(lab.paper_id, lab.human_label))
    W = {q: pnli.words2(t) for q, t in zip(papers.paper_id, papers.title)}
    sur = lambda x: {y.split()[-1].lower() for y in str(P.loc[x].authors).split('; ') if y.strip()}
    by_field = {f: g.paper_id.tolist() for f, g in papers.groupby('field')}
    rows = []
    for r in d.itertuples():
        a = W[r.paper_id]; tj = pnli.jac(a, pnli.words2(r.paraphrase)); sa = sur(r.paper_id); best = None
        for q in by_field[P.loc[r.paper_id].field]:
            if q == r.paper_id: continue
            j = pnli.jac(a, W[q])
            if sur(q) & sa: continue
            key = (0, j - tj) if j >= tj else (1, -j)
            if best is None or key < best[0]: best = (key, q, j)
        ml = lab.get(r.paper_id, '')
        inc = bool(r.auto_ok) and not bool(r.identical)
        rows.append(dict(paper_id=r.paper_id, para_jaccard2=tj, lexical_neighbour_j2=best[1], lexical_jaccard2=best[2], d_matched=best[2] >= tj,
                         identical=bool(r.identical), auto_ok=bool(r.auto_ok), nli_both=bool(r.nli_both), manual_label=ml,
                         include_primary=inc, include_sensitive=inc and bool(r.nli_both) and ml != 'changed'))
    o = pd.DataFrame(rows); OUT.parent.mkdir(parents=True, exist_ok=True); o.to_csv(OUT, index=False)
    # self-checks (WARN only): jaccard2 here equals the one in para_nli.csv; D is never A and never shares a surname
    w1 = (o.para_jaccard2 - d.jaccard2.values).abs().max()
    print(f'{"OK" if w1 < 1e-12 else "WARN"} para_jaccard2 equals para_nli.csv jaccard2 (max diff {w1:.2e})')
    print(f'{"OK" if (o.lexical_neighbour_j2 != o.paper_id).all() else "WARN"} D differs from A')
    print(f'rows {len(o)} | primary {o.include_primary.sum()} | sensitive {o.include_sensitive.sum()} | D matched {o.d_matched.mean():.3f} '
          f'| manual labels {(o.manual_label != "").sum()} (changed {(o.manual_label == "changed").sum()})')
    print('sha256', hashlib.sha256(OUT.read_bytes()).hexdigest(), OUT)


if __name__ == '__main__':
    main()
