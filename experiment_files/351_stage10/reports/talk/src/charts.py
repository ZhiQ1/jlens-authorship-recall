"""Hand-drawn style charts for the Stage 10 talk (matplotlib xkcd mode + Patrick Hand font). Reads the Stage 10 CSVs."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np, pandas as pd
from pathlib import Path

HERE = Path(__file__).parent; OUT = HERE / 'charts'; OUT.mkdir(exist_ok=True)
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10')
for f in (HERE / 'fonts').glob('*.ttf'): font_manager.fontManager.addfont(str(f))
INK, TGT, CTL, MUTE, GRN, PUR = '#2b2d42', '#e07a2f', '#3a6ea5', '#8d8f9e', '#3c8d5a', '#8a4fa3'
LENS = {'jlens_fitA': ('fitA', GRN), 'jlens_public': ('public', TGT), 'jlens_self100': ('self100', PUR), 'logit': ('logit lens', CTL)}
LAY = [24, 32, 40, 48, 56, 62]

plt.xkcd(scale=0.5, length=120, randomness=1.5)
plt.rcParams.update({'font.family': 'Patrick Hand', 'font.size': 17, 'axes.edgecolor': INK, 'axes.labelcolor': INK,
                     'xtick.color': INK, 'ytick.color': INK, 'text.color': INK, 'axes.linewidth': 1.5,
                     'path.effects': [], 'figure.facecolor': 'none', 'axes.facecolor': 'none', 'savefig.transparent': True,
                     'legend.frameon': False})


def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / f'{name}.png', dpi=200); plt.close(fig); print('wrote', name)


def zero(ax): ax.axhline(0, color=MUTE, lw=1.2, ls='--', zorder=0)


# C1 readout level by layer (all papers)
m = pd.read_csv(R / 'summary_extra/X3_means.csv')
fig, ax = plt.subplots(figsize=(8.4, 5.2))
for r, (lab, col) in LENS.items():
    d = m[(m.metric == 'level') & (m.readout == r)].sort_values('layer')
    ax.plot(d.layer, d['mean'], '-o', color=col, lw=2.5, ms=6, label=lab)
ax.set_xticks(LAY); ax.set_xlabel('layer'); ax.set_ylabel('log10(1 / rank)   (0 = rank 1)')
ax.set_ylim(-4.8, -0.6); ax.legend(loc='upper left', fontsize=16)
ax.annotate('rank ~ 10,000+', xy=(24, -4.55), xytext=(30, -4.75), fontsize=14, color=MUTE)
ax.annotate('rank ~ 10', xy=(62, -1.05), xytext=(49.5, -1.15), fontsize=14, color=MUTE, arrowprops=dict(arrowstyle='->', color=MUTE))
save(fig, 'c1_level_by_layer')

# C2 title-specific signal by layer, target vs control (jlens_public; final as marker)
a = pd.read_csv(R / 'summary_title/A_group_layer.csv')
fig, ax = plt.subplots(figsize=(8.4, 5.2))
for g, col in (('target', TGT), ('control', CTL)):
    d = a[(a.group_tight == g) & (a.readout == 'jlens_public')].sort_values('layer')
    ax.fill_between(d.layer, d.spec_mean_nlr_lo, d.spec_mean_nlr_hi, color=col, alpha=.18, lw=0)
    ax.plot(d.layer, d.spec_mean_nlr_mean, '-o', color=col, lw=2.6, ms=6, label=g)
    f = a[(a.group_tight == g) & (a.readout == 'final')].iloc[0]
    ax.plot([66.5], [f.spec_mean_nlr_mean], 'D', color=col, ms=9)
zero(ax); ax.set_xticks(LAY + [66.5]); ax.set_xticklabels([str(l) for l in LAY] + ['out'])
ax.set_xlabel('layer'); ax.set_ylabel('true title  -  false titles'); ax.legend(loc='upper left')
ax.annotate('flat until L48', xy=(40, 0.03), xytext=(29, 0.2), fontsize=15, arrowprops=dict(arrowstyle='->', color=INK))
save(fig, 'c2_spec_by_layer')

# C3 target - control within citation bin: true title vs title-specific
b1 = pd.read_csv(R / 'summary/B_target_vs_control_within_bin.csv'); b2 = pd.read_csv(R / 'summary_title/B_spec_target_vs_control_within_bin.csv')
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.9), sharey=True)
for ax, (b, col, title) in zip(axs, ((b1, 'mean_nlr', 'true title'), (b2, 'spec_mean_nlr', 'title-specific'))):
    for r in ('jlens_public', 'logit'):
        lab, c = LENS[r]; d = b[b.readout == r].sort_values('layer')
        ax.fill_between(d.layer, d[f'{col}_lo'], d[f'{col}_hi'], color=c, alpha=.18, lw=0)
        ax.plot(d.layer, d[f'{col}_diff'], '-o', color=c, lw=2.5, ms=6, label=lab)
    f = b[b.readout == 'final'].iloc[0]; ax.plot([66.5], [f[f'{col}_diff']], 'D', color=INK, ms=9, label='model output')
    zero(ax); ax.set_xticks(LAY + [66.5]); ax.set_xticklabels([str(l) for l in LAY] + ['out']); ax.set_title(title); ax.set_xlabel('layer')
axs[0].set_ylabel('target  -  control'); axs[0].legend(loc='upper left', fontsize=15)
save(fig, 'c3_tc_by_layer')

# C4 lens comparison: level gap to logit lens and top-10 share
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.9))
for r, (lab, col) in LENS.items():
    d = m[(m.metric == 'top10_share') & (m.readout == r)].sort_values('layer')
    axs[1].plot(d.layer, 100 * d['mean'], '-o', color=col, lw=2.5, ms=6, label=lab)
    d = m[(m.metric == 'level') & (m.readout == r)].sort_values('layer')
    axs[0].plot(d.layer, d['mean'], '-o', color=col, lw=2.5, ms=6, label=lab)
axs[0].set_title('readout level'); axs[0].set_ylabel('log10(1 / rank)'); axs[1].set_title('gold token in top 10'); axs[1].set_ylabel('% of tokens')
for ax in axs: ax.set_xticks(LAY); ax.set_xlabel('layer')
axs[1].legend(loc='upper left', fontsize=15)
save(fig, 'c4_lens_quality')

# C5 extra title-specific signal of each lens over the logit lens, and its target - control difference
pw = pd.read_csv(R / 'summary_extra/X3_pairwise.csv'); dd = pd.read_csv(R / 'summary_extra/X3_tc_spec_vs_logit.csv')
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.9), sharey=True)
off = {'jlens_fitA': -0.9, 'jlens_public': 0, 'jlens_self100': 0.9}
for r in ('jlens_fitA', 'jlens_public', 'jlens_self100'):
    lab, col = LENS[r]
    d = pw[(pw.metric == 'spec') & (pw.a == r) & (pw.b == 'logit')].sort_values('layer')
    axs[0].errorbar(d.layer + off[r], d['diff'], yerr=[d['diff'] - d.lo, d.hi - d['diff']], fmt='o', color=col, ms=7, lw=2, capsize=3, label=lab)
    d = dd[dd.lens == r].sort_values('layer')
    axs[1].errorbar(d.layer + off[r], d.tc_spec_minus_logit, yerr=[d.tc_spec_minus_logit - d.lo, d.hi - d.tc_spec_minus_logit], fmt='o', color=col, ms=7, lw=2, capsize=3)
for ax in axs: zero(ax); ax.set_xticks(LAY); ax.set_xlabel('layer')
axs[0].set_title('extra title-specific signal\n(lens - logit lens), all papers'); axs[1].set_title('...is it bigger for target?\n(target - control of that extra)')
axs[0].set_ylabel('log10(1 / rank)'); axs[0].legend(loc='lower left', fontsize=15)
save(fig, 'c5_lens_extra')

# C6 citation bins: title-specific signal at the model output
x2 = pd.read_csv(R / 'summary_extra/X2_by_bin.csv'); bins = list(x2[(x2.readout == 'final') & (x2.group == 'target')].citation_bin)
fig, axs = plt.subplots(1, 2, figsize=(10.8, 5.0))
for ax, col_, title in ((axs[0], 'level', 'readout level (model output)'), (axs[1], 'spec', 'title-specific signal (model output)')):
    for g, col in (('target', TGT), ('control', CTL)):
        d = x2[(x2.readout == 'final') & (x2.group == g)].reset_index(drop=True); d = d[d.n_papers >= 10]
        ax.fill_between(d.index, d[f'{col_}_lo'], d[f'{col_}_hi'], color=col, alpha=.18, lw=0)
        ax.plot(d.index, d[col_], '-o', color=col, lw=2.4, ms=5, label=g)
    ax.set_xticks(range(len(bins))); ax.set_xticklabels(bins, rotation=55, fontsize=12); ax.set_title(title); ax.set_xlabel('citation bin')
axs[0].set_ylabel('log10(1 / rank)'); axs[1].legend(loc='upper left')
save(fig, 'c6_citation')

# C7 name format x position: title-specific signal and target - control at the model output
fx = pd.read_csv(R / 'summary_extra/X1_by_format.csv'); fx = fx[fx.readout == 'final']
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.9), sharey=True)
xs = np.arange(2); w = 0.36
for ax, (col_, title) in zip(axs, (('spec', 'title-specific signal'), ('spec_tc', 'target - control'))):
    for j, (pos, lab, col) in enumerate((('first_token', '1st token', TGT), ('later_tokens', 'later tokens', CTL))):
        d = fx[fx.position == pos].set_index('format').loc[['initial_first', 'given_first']]
        ax.bar(xs + (j - .5) * w, d[col_], w, color=col, alpha=.85, label=lab, edgecolor=INK, lw=1.2)
        ax.errorbar(xs + (j - .5) * w, d[col_], yerr=[d[col_] - d[f'{col_}_lo'], d[f'{col_}_hi'] - d[col_]], fmt='none', ecolor=INK, capsize=4, lw=1.5)
    ax.set_xticks(xs); ax.set_xticklabels(['starts with initial\n("S. Bree")', 'starts with given name\n("Yan Zhao")']); ax.set_title(title)
axs[0].set_ylabel('log10(1 / rank)'); axs[1].legend(loc='upper right', fontsize=15)
save(fig, 'c7_format_position')

# C8 does knowing the first word help the rest? (true title; later words, first word in top 10 vs not)
cr = pd.read_csv(R / 'summary_extra/X1_cond_by_first_role.csv')
fig, ax = plt.subplots(figsize=(8.4, 5.0))
rl = [('final', 63, 'model output'), ('logit', 62, 'logit L62'), ('jlens_public', 62, 'public L62')]
for j, (role, lab, col) in enumerate((('initial_first', 'initial', CTL), ('given_first', 'full given name', TGT))):
    d = pd.concat([cr[(cr.readout == r) & (cr.layer == l) & (cr.first_role == role)] for r, l, _ in rl])
    xx = np.arange(3) + (j - .5) * w
    ax.bar(xx, d['diff'], w, color=col, alpha=.85, edgecolor=INK, lw=1.2, label=lab)
    ax.errorbar(xx, d['diff'], yerr=[d['diff'] - d.lo, d.hi - d['diff']], fmt='none', ecolor=INK, capsize=4, lw=1.5)
zero(ax); ax.set_xticks(range(3)); ax.set_xticklabels([t for _, _, t in rl]); ax.set_ylabel('later words: (first word in top 10) - (not)')
ax.legend(loc='upper left', title='first word is', fontsize=15)
save(fig, 'c8_first_word_helps')

# C9 roles: title-specific signal by token role at the model output (punctuation = negative control)
nc = pd.read_csv(R / 'summary_title/negative_control_by_role.csv'); f = nc[nc.readout == 'final'].iloc[0]
roles = [('surname_first', 'surname\n1st token'), ('surname_cont', 'surname\nrest'), ('given_first', 'given name\n1st token'), ('initial_first', 'initial'), ('punct', 'punctuation\n(control)')]
fig, ax = plt.subplots(figsize=(8.4, 5.0))
vals = [f[f'spec_mean_nlr_{r}_mean'] for r, _ in roles]; lo = [f[f'spec_mean_nlr_{r}_lo'] for r, _ in roles]; hi = [f[f'spec_mean_nlr_{r}_hi'] for r, _ in roles]
ax.bar(range(5), vals, 0.6, color=[TGT, TGT, GRN, CTL, MUTE], alpha=.85, edgecolor=INK, lw=1.2)
ax.errorbar(range(5), vals, yerr=[np.array(vals) - lo, np.array(hi) - vals], fmt='none', ecolor=INK, capsize=4, lw=1.5)
for i, v in enumerate(vals): ax.text(i, v + 0.03, f'{v:+.2f}', ha='center', fontsize=19)
ax.set_xticks(range(5)); ax.set_xticklabels([t for _, t in roles], fontsize=16); ax.set_ylabel('title-specific signal (model output)')
save(fig, 'c9_roles')

# C10 graded: model output by number of multiple-choice orders right
g = pd.read_csv(R / 'summary/C_graded_mc_team_a.csv'); g = g[(g.readout == 'final') & (g.metric == 'mean_nlr')].iloc[0]
fig, ax = plt.subplots(figsize=(6.4, 4.6))
v = [g[f'a{k}_centred_mean'] for k in range(5)]
ax.plot(range(5), v, '-o', color=TGT, lw=2.8, ms=9); zero(ax)
ax.set_xticks(range(5)); ax.set_xlabel('multiple-choice orders right (of 4)'); ax.set_ylabel('model output, centred in bin')
save(fig, 'c10_graded')

# C11 fine layers L48-L62: title-specific signal by group (logit lens) and target - control (logit, public)
bt = pd.read_csv(R / 'summary_title/B_spec_target_vs_control_within_bin.csv'); at = pd.read_csv(R / 'summary_title/A_group_layer.csv')
fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.9))
for g, col in (('target', TGT), ('control', CTL)):
    d = at[(at.group_tight == g) & (at.readout == 'logit') & (at.layer >= 40)].sort_values('layer')
    axs[0].fill_between(d.layer, d.spec_mean_nlr_lo, d.spec_mean_nlr_hi, color=col, alpha=.18, lw=0)
    axs[0].plot(d.layer, d.spec_mean_nlr_mean, '-o', color=col, lw=2.4, ms=4.5, label=g)
for r in ('logit', 'jlens_public'):
    lab, col = LENS[r]; d = bt[(bt.readout == r) & (bt.layer >= 40)].sort_values('layer')
    axs[1].fill_between(d.layer, d.spec_mean_nlr_lo, d.spec_mean_nlr_hi, color=col, alpha=.18, lw=0)
    axs[1].plot(d.layer, d.spec_mean_nlr_diff, '-o', color=col, lw=2.4, ms=4.5, label=lab)
for ax in axs: zero(ax); ax.set_xticks([40, 48, 50, 52, 54, 56, 58, 60, 62]); ax.set_xlabel('layer'); ax.axvspan(56.5, 61.5, color=MUTE, alpha=.08, lw=0)
axs[0].set_title('title-specific signal (logit lens)'); axs[1].set_title('target - control (title-specific)')
axs[0].set_ylabel('log10(1 / rank)'); axs[0].legend(loc='upper left'); axs[1].legend(loc='upper left', fontsize=15)
axs[1].annotate('steepest\nL57-L61', xy=(59, 0.12), xytext=(50.5, 0.15), fontsize=15, arrowprops=dict(arrowstyle='->', color=INK))
save(fig, 'c11_fine_layers')
