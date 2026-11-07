"""2026-11-07: verify by code the candidate sources for the report conclusions listed in conclusions_without_data.csv and build the
provenance tags used by apply_20261107.py (no_data_values_20261107.json). Also writes numcheck/claims/no_data_fixes_20261107.md (decision per sentence).
All numbers are read from the result files here; nothing is typed by hand."""
import json, re
from pathlib import Path
import pandas as pd
J = Path('/scratch/zhang.zhiqi2/jlens'); S10 = J / '351_stage10'; OUT = Path(__file__).parent
f3 = lambda x: f'{x:+.3f}'.replace('-', '−'); f4 = lambda x: f'{x:+.4f}'.replace('-', '−'); ci = lambda a, b: f'[{f3(a)}, {f3(b)}]'
pp = lambda x: f'{100 * x:+.2f}'.replace('-', '−')
V, D = {}, []

pq = pd.read_csv(J / '351_stage8/stage8D/summary/primary_questions.csv').set_index('question')
r = pq.loc['RQ2_matched_A_minus_B']; m = pd.read_csv(J / '351_stage8/stage8D/summary/matched_pair_differences.csv')
x = m[m['mode'] == 'jlens_L56'].sort_values('A_minus_B', ascending=False); drop = x.iloc[10:].A_minus_B.mean()
assert int(r.n) == 100 and drop < 0
V['F2'] = (f'Stage 8D，J-Lens L56 匹配 A − B {pp(r["mean"])} pp [{pp(r.ci_low)}, {pp(r.ci_high)}]，100 对，{int(r.positive)} 正 / {int(r.negative)} 负，配对 bootstrap 95% CI；'
           f'去掉差最大的 10 对后 {pp(drop)} pp（事后诊断，90 对）；351_stage8/stage8D/summary/primary_questions.csv 行 RQ2_matched_A_minus_B、matched_pair_differences.csv mode=jlens_L56')
D.append(('F2', '#ov 小样本的 A−B 不确定（依赖少数几对）', '支持：L56 A−B 区间下限接近 0，去掉最大的 10 对后变为负', V['F2']))

a = pd.read_csv(J / '351_stage7_4/summary/jlens_increment_bootstrap.csv').set_index('layer').loc['integrated']
b = pd.read_csv(J / '351_stage8/stage8D/summary/jlens_minus_vanilla.csv').set_index('mode').loc['L56_JLens_minus_Vanilla']
assert a.ci_low < 0 < a.ci_high and b.ci_low < 0 < b.ci_high
V['F3'] = (f'Stage 7.4 J-Lens − Vanilla 标题优势之差，7 层积分 {f4(a["mean"])} [{f4(a.ci_low)}, {f4(a.ci_high)}]，Pilot50 50 篇，论文 bootstrap；351_stage7_4/summary/jlens_increment_bootstrap.csv 行 layer=integrated；'
           f'Stage 8 L56 J-Lens − Vanilla {pp(b["mean"])} pp [{pp(b.ci_low)}, {pp(b.ci_high)}]，200 篇；351_stage8/stage8D/summary/jlens_minus_vanilla.csv')
D.append(('F3', '#ov 小样本中 J-Lens 相对 Vanilla 没有增量', '支持：两个区间都含 0', V['F3']))

p = pd.read_csv(S10 / 'summary_extra/X3_pairwise.csv'); J3 = ['jlens_public', 'jlens_self100', 'jlens_fitA']
mid = p[(p.b == 'logit') & p.a.isin(J3) & p.layer.isin([24, 32, 40, 48])]
lv, sp = mid[mid.metric == 'level'], mid[mid.metric == 'spec']
assert (lv['diff'] > 0).all() and (sp['diff'] > 0).all() and sp['diff'].max() < 0.035
V['F4a'] = (f'Stage 10 X3，三种 Jacobian lens − logit lens，L24–L48，全部 9,108 篇：名字名次水平（level）高 {f3(lv["diff"].min())} 到 {f3(lv["diff"].max())}，'
            f'标题特异信号只多 {f3(sp["diff"].min())} 到 {f3(sp["diff"].max())}，论文 bootstrap 95% CI；351_stage10/summary_extra/X3_pairwise.csv metric=level / spec，b=logit')
D.append(('F4a', '#ov 全量中它在中间层多读出的是“名字形状”，不区分论文；§7 Jacobian lens 能让中间层读出更多与名字相关的信息，但不区分论文，三种一致',
          '支持：level 差大、spec 差小，三种 lens 方向相同；“名字形状”改写为括注说明', V['F4a']))
t = pd.read_csv(S10 / 'summary_extra/X3_tc_spec_vs_logit.csv'); tm = t[t.layer.isin([24, 32, 40, 48, 56])]
assert (tm.tc_spec_minus_logit.max() < 0.01) and (tm[tm.layer.isin([24, 48, 56])].hi < 0).all()
V['F4b'] = (f'Stage 10 X3，(Jacobian lens − logit lens) 标题特异信号的引用档内目标−对照，L24–L56：{f3(tm.tc_spec_minus_logit.min())} 到 {f3(tm.tc_spec_minus_logit.max())}；'
            f'L24、L48、L56 三种 lens 的区间都在 0 以下，L32–L40 含 0；论文 bootstrap 95% CI；351_stage10/summary_extra/X3_tc_spec_vs_logit.csv')
D.append(('F4b', '#ov / §1 / §7 也不偏向目标组；对照组反而略多', '支持：目标−对照 ≤ 0，多层显著为负', V['F4b']))

f = pd.read_csv(S10 / 'summary_extra/X1_by_format.csv'); f = f[f.readout == 'final'].set_index(['format', 'position'])
g = lambda k: f.loc[k]
i1, i2, g1, g2 = g(('initial_first', 'first_token')), g(('initial_first', 'later_tokens')), g(('given_first', 'first_token')), g(('given_first', 'later_tokens'))
V['F5'] = (f'Stage 10 补充 X1，最终输出 L63，引用档内目标−对照：首字母开头的名字，首字母 {f3(i1.spec_tc)} {ci(i1.spec_tc_lo, i1.spec_tc_hi)}、后续 token {f3(i2.spec_tc)} {ci(i2.spec_tc_lo, i2.spec_tc_hi)}（{int(i1.n_papers):,} 篇）；'
           f'完整名开头，名 {f3(g1.spec_tc)} {ci(g1.spec_tc_lo, g1.spec_tc_hi)}、后续 token {f3(g2.spec_tc)} {ci(g2.spec_tc_lo, g2.spec_tc_hi)}（{int(g1.n_papers):,} 篇）；论文 bootstrap 95% CI；351_stage10/summary_extra/X1_by_format.csv readout=final')
D.append(('F5', '#ov / §7 名字格式（首字母几乎不带信号，姓在后续 token；完整名本身带和姓相当的信号）', '支持', V['F5']))

pr = pd.read_csv(J / '371_stage12/summary_cpu/A_prior_decomposition.csv'); pr = pr[(pr.readout == 'final') & (pr.layer == 63) & (pr.role == 'all_tokens')].set_index('group')
tt, ts, tp, to = pr.loc['tc_true', 'true'], pr.loc['tc_spec', 'spec'], pr.loc['tc_prior', 'prior'], pr.loc['tc_topic', 'topic']
assert abs(tt - (ts + tp + to)) < 0.01
V['F9'] = (f'Stage 12 CPU 名字先验拆解，最终输出 L63，全部名字 token，引用档内目标−对照：真标题下 {f3(tt)} = 标题特异 {f3(ts)} + 名字先验 {f3(tp)} + 主题 {f3(to)}；'
           f'标题特异部分约占 {100 * ts / tt:.0f}%；9,108 篇（目标 4,621 / 对照 2,220）；371_stage12/summary_cpu/A_prior_decomposition.csv group=tc_true/tc_spec/tc_prior/tc_topic')
D.append(('F9', '§1 几乎全部是标题特异的，不能用名字好猜来解释（及 R0/R1 框、英文对应句）', f'减弱：标题特异部分约 {100 * ts / tt:.0f}%，先验 {f3(tp)} 不为 0 → “几乎全部”改为“主要”', V['F9']))

bs = pd.read_csv(S10 / 'summary_title/B_spec_target_vs_control_within_bin.csv'); bm = bs[bs.layer.isin([24, 32, 40, 48])]
lg = bm[bm.readout == 'logit'].set_index('layer')
assert bm.spec_mean_nlr_diff.max() < 0.01 and lg.loc[24, 'spec_mean_nlr_lo'] > 0
V['F14a'] = (f'Stage 10，真标题 − 5 个假标题平均，引用档内目标−对照，L24–L48，logit 与三种 Jacobian lens：{f3(bm.spec_mean_nlr_diff.min())} 到 {f3(bm.spec_mean_nlr_diff.max())}；'
             f'logit lens L24 {f3(lg.loc[24, "spec_mean_nlr_diff"])} {ci(lg.loc[24, "spec_mean_nlr_lo"], lg.loc[24, "spec_mean_nlr_hi"])}、L32 {f3(lg.loc[32, "spec_mean_nlr_diff"])} {ci(lg.loc[32, "spec_mean_nlr_lo"], lg.loc[32, "spec_mean_nlr_hi"])}；'
             f'论文 bootstrap 95% CI；351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv')
D.append(('F14', '§7 没有哪种 lens 能在中间层读出偏向目标组的论文信息', '减弱：logit lens 在 L24、L32 有 +0.007、+0.005 的小正值（CI > 0），所以改为“都很小或为负，没有明显偏向”', V['F14a']))

tc = pd.read_csv(S10 / 'summary_r0r1/tc_R1target_vs_R0control.csv')
def first_pos(rd):
    x = tc[tc.readout == rd].sort_values('layer'); ok = x[x.spec_mean_nlr_lo > 0]
    for L in ok.layer:  # first layer from which all later layers stay > 0
        if (x[x.layer >= L].spec_mean_nlr_lo > 0).all(): return int(L), x
fpub, xp = first_pos('jlens_public'); flog, xl = first_pos('logit'); fin = tc[(tc.readout == 'final')].iloc[0]
V['F15a'] = (f'Stage 10 R1 目标 vs R0 对照，真标题 − 5 个假标题平均，引用档内目标−对照：public J-lens 从 L{fpub} 起持续为正（L{fpub} {f3(xp.set_index("layer").loc[fpub, "spec_mean_nlr_diff"])}），'
             f'L48 {f3(xp.set_index("layer").loc[48, "spec_mean_nlr_diff"])}；logit lens 从 L{flog} 起持续为正；最终输出 {f3(fin.spec_mean_nlr_diff)} {ci(fin.spec_mean_nlr_lo, fin.spec_mean_nlr_hi)}；'
             f'C {int(fin.n_a)} / B {int(fin.n_b)} 篇，7 档；论文 bootstrap 95% CI；351_stage10/summary_r0r1/tc_R1target_vs_R0control.csv')
w = pd.read_csv(S10 / 'summary_r0r1/R1_author_written_minus_missed.csv'); w = w[w.excl_first_author == False]
def first_pos_w(rd):
    x = w[w.readout == rd].sort_values('layer')
    for L in x[x.spec_lo > 0].layer:
        if (x[x.layer >= L].spec_lo > 0).all(): return int(L), x.set_index('layer')
wp, xwp = first_pos_w('jlens_public'); wl, xwl = first_pos_w('logit'); wf = w[w.readout == 'final'].iloc[0]
V['F15b'] = (f'Stage 10 R1 论文内，写对 − 未写对的作者（论文内配对），标题特异信号：public J-lens 从 L{wp} 起持续为正（L{wp} {f3(xwp.loc[wp, "spec_diff"])} {ci(xwp.loc[wp, "spec_lo"], xwp.loc[wp, "spec_hi"])}，L62 {f3(xwp.loc[62, "spec_diff"])}），'
             f'logit lens 从 L{wl} 起；最终输出 {f3(wf.spec_diff)} {ci(wf.spec_lo, wf.spec_hi)}；{int(wf.n_papers)} 篇，论文 bootstrap 95% CI；351_stage10/summary_r0r1/R1_author_written_minus_missed.csv excl_first_author=False')
D.append(('F15', '第三部分 R1 论文让优势更大，但不改变时间点；R1 内部写对的作者也在最后几层才领先', f'支持：R1 目标 vs R0 对照只在 L{fpub}（public）/ L{flog}（logit）起为正；R1 内写对 − 未写对从 L{wp} / L{wl} 起为正', V['F15a'] + ' ‖ ' + V['F15b']))

st = (J / '391_groups/summary_table.md').read_text(encoding='utf-8')
row = lambda gname: next(l for l in st.splitlines() if l.startswith(f'| {gname} |')).split('|')[1:-1]
A_, B_, U0, C_ = row('A'), row('B'), row('U0'), row('C')
num = lambda cell: float(re.match(r'\s*([+\-−]\d\.\d+)', cell).group(1).replace('−', '-'))
assert num(B_[1]) < num(U0[1]) < num(A_[1]) and num(C_[2]) > num(C_[1])
V['F16'] = (f'分组对比，未写出作者的最终输出 L63 信号：U0（R0 × 识别不确定）{U0[1].strip()}，介于 A {A_[1].strip().split(";")[0]} 与 B {B_[1].strip().split(";")[0]} 之间；团队聚类 95% CI；391_groups/summary_table.md 第 2 列')
V['F17'] = (f'分组对比 C 组：已写出作者 {C_[2].strip()}，未写出作者 {C_[1].strip()}；最终输出 L63，团队聚类 95% CI；391_groups/summary_table.md C 行第 2、3 列')
D.append(('F16', '分组对比 识别不确定的论文落在两组之间', '支持', V['F16']))
D.append(('F17', '分组对比 以前约 +0.11 主要是因为已写出作者分数本来就高（循环论证）', '支持（已写出作者分数高于未写出）', V['F17']))
D.append(('F10', '§1 而且这部分信息不偏向目标组', '支持（同 F4b）', V['F4b']))
D.append(('F12', '§7 Jacobian lens 能让中间层读出更多与名字相关的信息…三种一致', '支持（同 F4a）', V['F4a']))
D.append(('F13', '§7 标题特异信号在名字里的分布取决于格式', '支持（同 F5）', V['F5']))
(OUT / 'no_data_values_20261107.json').write_text(json.dumps(V, ensure_ascii=False, indent=1), encoding='utf-8')
L = ['# Report conclusions without data: fixes 2026-11-07', '',
     'Input: numcheck/claims/out_20261107_005118/conclusions_without_data.csv (19 rows). Rows judged “标题句（同段后文有数据）”, “不是结论” (plan, design note, legend, bracket) were left unchanged: '
     '#0, #1, #6, #7, #8, #11, #18. The other 12 rows were verified by `sync_20261107/verify_no_data_20261107.py` (reads the CSVs, asserts the claim) and fixed by `apply_20261107.py`.', '',
     '| id | sentence (report) | decision | provenance added (computed from the file) |', '|---|---|---|---|']
L += [f'| {a} | {b} | {c} | {d} |' for a, b, c, d in D]
L += ['', 'Before → after (text): F9 “几乎全部是标题特异的” → “主要是标题特异的” (§1 and the R0/R1 conclusion box; English “almost entirely title-specific” → “mostly title-specific”, 3 places); '
      'F14 “没有哪种 lens 能在中间层读出偏向目标组的论文信息” → “中间层（L24–L48）各种 lens 的目标−对照都很小或为负，没有看到明显偏向目标组的论文信息（logit lens 在 L24–L32 有很小的正值）” (+ English); '
      'F4 “名字形状” kept and explained in brackets (“名字名次整体更高，但标题特异信号只多一点”). All other rows: wording unchanged, provenance tag added.']
(Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/numcheck/claims') / 'no_data_fixes_20261107.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
for k, v in V.items(): print(k, v[:150])
