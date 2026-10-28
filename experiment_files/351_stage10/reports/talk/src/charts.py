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

# ================= Stage 11 =================
R11 = Path('/scratch/zhang.zhiqi2/jlens/361_stage11/summary')
e1 = pd.read_csv(R11 / 'E1_recovery.csv'); e1t = pd.read_csv(R11 / 'E1t_recovery.csv')
e2 = pd.read_csv(R11 / 'E2_knockout.csv'); e2n = pd.read_csv(R11 / 'E2n_knockout.csv')

# C12 patching recovery and knockout loss by layer
fig, axs = plt.subplots(1, 2, figsize=(10.6, 5.0), sharey=True)
ax = axs[0]
for g, col in (('target', TGT), ('control', CTL)):
    d = e1[e1.group == g].sort_values('layer')
    ax.plot(d.layer, d.recovery, '-o', color=col, lw=2.5, ms=5, label=f'after-title tokens · {g}')
d = e1t[e1t.group == 'all'].sort_values('layer')
ax.plot(d.layer, d.recovery, '--s', color=INK, lw=2, ms=5, label='last title token only')
ax.set_title('patch true -> false title at layer l'); ax.set_xlabel('layer'); ax.set_ylabel('share of the true-false gap'); ax.set_ylim(-0.12, 1.1); ax.set_xticks([8, 16, 24, 32, 40, 48, 56, 63])
ax.legend(loc='center right', fontsize=13)
ax = axs[1]
for g, col in (('target', TGT), ('control', CTL)):
    d = e2[e2.group == g].sort_values('start_layer')
    ax.plot(d.start_layer, d.loss_fraction, '-o', color=col, lw=2.5, ms=5, label=f'all later tokens · {g}')
d = e2n[e2n.group == 'all'].sort_values('start_layer')
ax.plot(d.start_layer, d.loss_fraction, '--s', color=INK, lw=2, ms=5, label='":" + names only')
ax.set_title('block attention to the title from layer l on'); ax.set_xlabel('layer'); ax.set_xticks([0, 16, 24, 32, 40, 48, 56, 62])
ax.legend(loc='upper right', fontsize=13)
for a in axs: a.axhline(0, color=MUTE, lw=1.2, ls='--', zorder=0); a.axhline(1, color=MUTE, lw=1, ls=':', zorder=0); a.annotate('', xy=(50, -0.07), xytext=(24, -0.07), arrowprops=dict(arrowstyle='<->', color=INK, lw=1.5)); a.text(37, -0.045, 'L24-L50', ha='center', fontsize=14)
save(fig, 'c12_patch_knockout')

# C13 title position: lens vs probe (title-specific signal at the last title token)
e4 = pd.read_csv(R11 / 'E4_titlepos_lens.csv'); pr = pd.read_csv(R11 / 'E4_probe.csv')
fig, axs = plt.subplots(1, 2, figsize=(10.6, 5.0), sharey=True)
ax = axs[0]
for r, col in (('logit', CTL), ('jlens_public', TGT)):
    d = e4[(e4.kind == 'first') & (e4.readout == r) & (e4.position == 'title')].sort_values('layer')
    lab = 'logit lens' if r == 'logit' else 'public J-lens'
    ax.plot(d.layer, d.spec_target, '-o', color=col, lw=2.4, ms=5, label=f'{lab} · target')
    ax.plot(d.layer, d.spec_control, ':o', color=col, lw=2, ms=4, label=f'{lab} · control')
ax.set_title('lens readout at the last title token'); ax.set_xlabel('layer'); ax.set_ylabel('title-specific signal'); ax.legend(loc='upper left', fontsize=12)
ax = axs[1]
for g, col in (('target', TGT), ('control', CTL)):
    ax.fill_between(pr.layer, pr[f'spec_{g}_lo'], pr[f'spec_{g}_hi'], color=col, alpha=.18, lw=0); ax.plot(pr.layer, pr[f'spec_{g}'], '-o', color=col, lw=2.5, ms=5, label=g)
ax.set_title('linear probe at the last title token'); ax.set_xlabel('layer'); ax.legend(loc='upper left')
for a in axs: a.axhline(0, color=MUTE, lw=1.2, ls='--', zorder=0); a.set_xticks([16, 24, 32, 40, 48, 56, 62])
save(fig, 'c13_title_position')

# C14 author chain: gain by author position, and title-specific signal chain vs isolated
e3 = pd.read_csv(R11 / 'E3_chain.csv'); f3 = e3[e3.readout == 'final']
fig, axs = plt.subplots(1, 2, figsize=(10.6, 5.0))
xs = np.arange(1, 5); w = .36
for j, (g, col) in enumerate((('target', TGT), ('control', CTL))):
    d = f3[f3.group == g].sort_values('author_pos')
    axs[0].bar(xs + (j - .5) * w, d.gain_true, w, color=col, alpha=.85, edgecolor=INK, lw=1.2, label=g)
    axs[0].errorbar(xs + (j - .5) * w, d.gain_true, yerr=[d.gain_true - d.gain_true_lo, d.gain_true_hi - d.gain_true], fmt='none', ecolor=INK, capsize=4, lw=1.4)
    axs[1].plot(d.author_pos, d.iso_spec, ':o', color=col, lw=2, ms=6, label=f'{g} · each author alone')
    axs[1].plot(d.author_pos, d.chain_spec, '-o', color=col, lw=2.6, ms=6, label=f'{g} · after co-authors')
axs[0].set_title('previous authors help (true title)'); axs[0].set_ylabel('chain - alone'); axs[1].set_title('title-specific signal')
for a in axs: a.set_xticks(xs); a.set_xticklabels(['1st', '2nd', '3rd', '4th+']); a.set_xlabel('author position')
axs[0].axhline(0, color=MUTE, lw=1.2, ls='--'); axs[0].legend(loc='upper left'); axs[1].set_ylim(0, 0.8); axs[1].legend(loc='upper right', fontsize=12)
save(fig, 'c14_author_chain')

# ================= Stage 12 CPU: name prior, probe controls =================
R12 = Path('/scratch/zhang.zhiqi2/jlens/371_stage12/summary_cpu')
A = pd.read_csv(R12 / 'A_prior_decomposition.csv'); A = A[A.readout == 'final']
roles = [('all_tokens', 'all tokens'), ('surname_first', 'surname\n1st'), ('surname_cont', 'surname\nrest'), ('given_first', 'given\n1st'), ('initial_first', 'initial')]
fig, axs = plt.subplots(1, 2, figsize=(10.6, 5.0))
ax = axs[0]
for j, (g, col, dx) in enumerate((('target', TGT, -0.13), ('control', CTL, 0.13))):
    for i, (r, lab) in enumerate(roles):
        x = A[(A.role == r) & (A.group == g)].iloc[0]; pr, fa, tr = x.prior, x.prior + x.topic, x.true
        ax.plot([i + dx] * 2, [pr, tr], color=col, lw=2.2)
        ax.plot(i + dx, pr, 'o', color=MUTE, ms=7); ax.plot(i + dx, fa, 'x', color=INK, ms=7); ax.plot(i + dx, tr, 'o', color=col, ms=8, label=g if i == 0 else None)
ax.plot([], [], 'o', color=MUTE, label='no title (name prior)'); ax.plot([], [], 'x', color=INK, label='false title')
ax.set_xticks(range(len(roles))); ax.set_xticklabels([l for _, l in roles], fontsize=13); ax.set_ylabel('log10(1 / rank), model output'); ax.set_title('prior -> false title -> true title')
ax.set_ylim(-2.6, 0.55); ax.legend(loc='upper right', fontsize=11, ncol=2)
ax = axs[1]
parts = [('prior', 'name prior', MUTE), ('topic', 'topic', INK), ('spec', 'paper-specific', TGT)]
xs = np.arange(2); w = 0.26
for k, (key, lab, col) in enumerate(parts):
    vals = [A[(A.role == r) & (A.group == f'tc_{key}')].iloc[0] for r in ('all_tokens', 'surname_first')]
    v = [x[key] for x in vals]; lo = [x[f'{key}_lo'] for x in vals]; hi = [x[f'{key}_hi'] for x in vals]
    ax.bar(xs + (k - 1) * w, v, w, color=col, alpha=.85, edgecolor=INK, lw=1.2, label=lab)
    ax.errorbar(xs + (k - 1) * w, v, yerr=[np.array(v) - lo, np.array(hi) - v], fmt='none', ecolor=INK, capsize=4, lw=1.4)
ax.axhline(0, color=MUTE, lw=1.2, ls='--'); ax.set_xticks(xs); ax.set_xticklabels(['all tokens', 'surname 1st token']); ax.set_title('target - control, split (within bin)')
ax.legend(loc='upper left', fontsize=13)
save(fig, 'c15_name_prior')

X1 = pd.read_csv(R12 / 'X1_probe_controls.csv')
fig, ax = plt.subplots(figsize=(8.6, 4.9))
ctrls = [('probe (as in Stage 11)', 'probe', TGT), ('gold = random other paper', 'gold of another paper', MUTE), ('gold = random paper of the same field', 'gold of a same-field paper', CTL), ('probe trained on FALSE-title pairs', 'trained on false titles', GRN)]
lays = sorted(X1.layer.unique()); xs = np.arange(len(lays)); w = 0.2
for k, (c, lab, col) in enumerate(ctrls):
    d = X1[X1.control == c].set_index('layer').loc[lays]
    ax.bar(xs + (k - 1.5) * w, d.spec_all, w, color=col, alpha=.85, edgecolor=INK, lw=1.1, label=lab)
    ax.errorbar(xs + (k - 1.5) * w, d.spec_all, yerr=[d.spec_all - d.spec_all_lo, d.spec_all_hi - d.spec_all], fmt='none', ecolor=INK, capsize=3, lw=1.2)
ax.axhline(0, color=MUTE, lw=1.2, ls='--'); ax.set_xticks(xs); ax.set_xticklabels([f'L{l}' for l in lays]); ax.set_ylabel('title-specific signal at the last title token')
ax.set_ylim(-0.015, 0.135); ax.legend(loc='upper left', fontsize=12, ncol=2)
save(fig, 'c16_probe_controls')

# C17 R0 / R1 stratified: three views of target - control (left), Stage 11 patching by recall level (right)
S = R / 'summary_r0r1'
views = (('tc_R0', 'R0 view: A - B', TGT, '-o'), ('tc_R1target_vs_R0control', 'R1 view: C - B', PUR, '-^'), ('tc_pooled', 'pooled (as before)', MUTE, '--s'))
fig, axs = plt.subplots(1, 2, figsize=(10.6, 5.0))
ax = axs[0]
for f, lab, col, sty in views:
    t = pd.read_csv(S / f'{f}.csv'); d = t[(t.readout == 'logit') & (t.layer >= 40)].sort_values('layer'); o = t[t.readout == 'final'].iloc[0]
    ax.fill_between(d.layer, d.spec_mean_nlr_lo, d.spec_mean_nlr_hi, color=col, alpha=.10, lw=0)
    ax.plot(d.layer, d.spec_mean_nlr_diff, sty, color=col, lw=2.3, ms=4.5, label=lab)
    ax.errorbar([63.4], [o.spec_mean_nlr_diff], yerr=[[o.spec_mean_nlr_diff - o.spec_mean_nlr_lo], [o.spec_mean_nlr_hi - o.spec_mean_nlr_diff]], fmt='D', color=col, ms=7, capsize=3)
zero(ax); ax.set_xticks([40, 48, 52, 56, 60, 63]); ax.set_xticklabels(['40', '48', '52', '56', '60', 'out']); ax.set_xlabel('layer (logit lens; diamonds = output)')
ax.set_title('target - control, title-specific, within bin'); ax.set_ylabel('log10(1 / rank)'); ax.legend(loc='upper left', fontsize=14)
ax = axs[1]
c = pd.read_csv(Path('/scratch/zhang.zhiqi2/jlens/361_stage11/summary_r0r1/stage11_curves_by_recall.csv')); c = c[c.exp == 'E1']
for v, col, sty in (('A target R0', TGT, '-o'), ('C target R1', PUR, '-^'), ('B control R0', CTL, '-s')):
    d = c[c.view == v].sort_values('layer')
    ax.fill_between(d.layer, d.lo, d.hi, color=col, alpha=.10, lw=0)
    ax.plot(d.layer, d.value, sty, color=col, lw=2.3, ms=4.5, label=f'{v} (n={int(d.n.iloc[0])})')
ax.set_ylim(-0.05, 1.08); ax.set_xticks([24, 32, 40, 48, 52, 56, 62]); ax.set_xlabel('layer'); ax.axhline(1, color=MUTE, lw=1, ls=':', zorder=0)
ax.set_title('Stage 11 patching: share of the gap recovered'); ax.legend(loc='lower right', fontsize=13)
save(fig, 'c17_r0_r1')

# C18 inside R1 papers: authors the open answer got right vs missed, paired within paper
pa = pd.read_csv(S / 'R1_author_written_minus_missed.csv'); pa = pa[~pa.excl_first_author]
fig, axs = plt.subplots(1, 2, figsize=(10.6, 5.0))
ax = axs[0]
for r in ('logit', 'jlens_public'):
    lab, col = LENS[r]; d = pa[(pa.readout == r) & (pa.layer >= 40)].sort_values('layer')
    ax.fill_between(d.layer, d.spec_lo, d.spec_hi, color=col, alpha=.12, lw=0)
    ax.plot(d.layer, d.spec_diff, '-o', color=col, lw=2.3, ms=4.5, label=lab)
o = pa[pa.readout == 'final'].iloc[0]
ax.errorbar([63.4], [o.spec_diff], yerr=[[o.spec_diff - o.spec_lo], [o.spec_hi - o.spec_diff]], fmt='D', color=INK, ms=7, capsize=3, label='output')
zero(ax); ax.set_xticks([40, 48, 52, 56, 60, 63]); ax.set_xticklabels(['40', '48', '52', '56', '60', 'out']); ax.set_xlabel('layer')
ax.set_title('title-specific: written - missed author'); ax.set_ylabel('log10(1 / rank)'); ax.legend(loc='upper left', fontsize=14)
ax = axs[1]
d = pa[pa.readout == 'logit'].sort_values('layer'); d = d[d.layer >= 40]
ax.plot(d.layer, d.spec_hit, '-o', color=TGT, lw=2.3, ms=4.5, label='written correctly')
ax.plot(d.layer, d.spec_miss, '-s', color=CTL, lw=2.3, ms=4.5, label='missed')
ax.plot(d.layer, d.delete_diff, '--', color=MUTE, lw=2, label='no title: written - missed (prior)')
zero(ax); ax.set_xticks([40, 48, 52, 56, 60, 62]); ax.set_xlabel('layer (logit lens)'); ax.set_title('title-specific signal, logit lens'); ax.legend(loc='upper left', fontsize=13)
save(fig, 'c18_r1_authors')
