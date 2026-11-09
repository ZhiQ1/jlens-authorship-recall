"""Audit (2026-11-09, read-only): do the M2 five-false-title runs (stage13_m2_f5.py) need the E4b exclusions?
Uses the folds actually used (summary_m2_f5/folds_<title>.npz). For each title and each test row (target p, donor d), counts:
 (a) title reuse: another row showing the same donor title d sits in a different fold (= same title text in training);
 (b) donor in a training fold: some training row has label paper d (rows labelled with d's attributes) in another fold;
 (b2) donor's team in a training fold: a row whose label paper shares the donor's team (group id) is in another fold;
 (c) donor paper d appears as a TARGET row (its year in the prompt; label = some other paper) in another fold -- the only
     way d can be in training here; reported for information (not an E4b rule).
 (d) the E4b rule taken literally: d's TRUE title in this probe's training folds. M2 false probes train on false rows only, so 0 by design.
Split by group_tight of the target paper (target / control / other). Writes summary_m2_f5/exclusion_audit.csv."""
from pathlib import Path
import numpy as np, pandas as pd

R = Path('/scratch/zhang.zhiqi2/jlens'); D = R / '381_stage13/summary_m2_f5'
P = pd.read_parquet(R / '351_stage10/cohort/papers.parquet').set_index('paper_id')
rows = []
for k in range(5):
    z = np.load(D / f'folds_false_{k}.npz', allow_pickle=True)
    pid, lab, fold, team = z['pid'], z['lab'], z['fold'].astype(int), z['team']
    df = pd.DataFrame(dict(pid=pid, lab=lab, fold=fold, team=team))
    nf_lab = df.groupby('lab').fold.nunique()                      # folds containing rows with this donor/label
    nf_team = df.groupby('team').fold.nunique()
    a = df.lab.map(nf_lab) > 1                                    # (a) == (b): same donor title / same label paper in another fold
    b2 = df.team.map(nf_team) > 1
    tf = df.groupby('pid').fold.first()                           # fold of the row whose TARGET is a given paper
    c = np.array([(d in tf.index) and (tf[d] != f) for d, f in zip(df.lab, df.fold)])
    grp = P.loc[pid].group_tight.to_numpy()
    for g in ['target', 'control', 'all']:
        m = np.ones(len(df), bool) if g == 'all' else grp == g
        rows.append(dict(title=f'false_{k}', group=g, n_rows=int(m.sum()), a_title_reuse=int(a[m].sum()), b_donor_label_in_train=int(a[m].sum()),
                         b2_donor_team_in_train=int(b2[m].sum()), c_donor_as_target_in_train=int(c[m].sum()), d_true_title_in_train=0,
                         n_donor_titles=int(df.lab.nunique()), n_teams=int(df.team.nunique())))
T = pd.DataFrame(rows); T.to_csv(D / 'exclusion_audit.csv', index=False); print(T.to_string(index=False))
