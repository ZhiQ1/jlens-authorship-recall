"""User request 2026-10-29 (item 5): are the title states under the three questions (authors / year / field) simply
near-identical? If they are, X1's "task-independent" recovery is trivial. Uses the M3 cache (all 9,108 papers):
summary_m3/resid_cache.f16 [paper, task, layer, pos, 5120], pos 0 = last title token (X1 patches the whole title span;
its last token is the one every later title token is compared with here), pos 1 = final ':' for contrast.
Per layer and task pair: mean raw cosine of the SAME paper under two questions; mean relative distance
||a - b|| / ||a||; and, as scale, the mean cosine between DIFFERENT papers under the same question (random pairing) and
the relative distance between different papers. 'Question share' = distance(same paper, two questions) / distance
(two papers, same question): 0 = the question changes nothing, 1 = changing the question moves the state as far as
changing the paper. Output: summary_m3/x1_similarity.csv, reports/x1_similarity.md"""
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path('/scratch/zhang.zhiqi2/jlens/381_stage13'); S = ROOT / 'summary_m3'
LAYERS = [4, 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 62, 63]; TASKS = ['authors', 'year', 'field']


def main():
    pids = np.load(S / 'resid_cache_pids.npy'); n = len(pids)
    X = np.memmap(S / 'resid_cache.f16', np.float16, 'r', shape=(n, 3, len(LAYERS), 2, 5120))
    perm = np.random.default_rng(5).permutation(n); rows = []
    for li, l in enumerate(LAYERS):
        for pi, pos in enumerate(('title_last', 'colon')):
            A = np.asarray(X[:, :, li, pi, :], dtype=np.float32); nr = np.linalg.norm(A, axis=2)
            U = A / (nr[..., None] + 1e-9)
            for a, b in ((0, 1), (0, 2), (1, 2)):
                cos_same = (U[:, a] * U[:, b]).sum(1); dist_same = np.linalg.norm(A[:, a] - A[:, b], axis=1) / nr[:, a]
                cos_diff = (U[:, a] * U[perm, a]).sum(1); dist_diff = np.linalg.norm(A[:, a] - A[perm, a], axis=1) / nr[:, a]
                rows.append(dict(layer=l, pos=pos, pair=f'{TASKS[a]}-{TASKS[b]}', cos_same_paper=cos_same.mean(), cos_same_p05=np.percentile(cos_same, 5),
                                 reldist_same_paper=dist_same.mean(), cos_diff_paper=cos_diff.mean(), reldist_diff_paper=dist_diff.mean(),
                                 question_share=dist_same.mean() / dist_diff.mean()))
        print('layer', l, flush=True)
    D = pd.DataFrame(rows); D.to_csv(S / 'x1_similarity.csv', index=False)
    G = D.groupby(['pos', 'layer'])[['cos_same_paper', 'cos_same_p05', 'cos_diff_paper', 'reldist_same_paper', 'reldist_diff_paper', 'question_share']].mean().reset_index()
    L = ['# X1 check: how similar are the title states under the three questions? (user request 2026-10-29, item 5)', '',
         f'{n} papers; values averaged over the 3 question pairs. cos = raw cosine (not centred). question share = ||a_q1 - a_q2|| / ||a_q1 - a_other paper||.', '']
    for pos in ('title_last', 'colon'):
        L += [f'## {pos}', '', '| layer | cos, same paper, two questions (5th pct) | cos, two papers, same question | rel. distance: question change | rel. distance: paper change | question share |', '|---|---|---|---|---|---|']
        for r in G[G.pos == pos].itertuples():
            L.append(f'| L{r.layer} | {r.cos_same_paper:.4f} ({r.cos_same_p05:.4f}) | {r.cos_diff_paper:.4f} | {r.reldist_same_paper:.3f} | {r.reldist_diff_paper:.3f} | {r.question_share:.3f} |')
        L.append('')
    (ROOT / 'reports/x1_similarity.md').write_text('\n'.join(L) + '\n'); print('\n'.join(L)); print('\nX1SIM ANALYZED')


if __name__ == '__main__':
    main()
