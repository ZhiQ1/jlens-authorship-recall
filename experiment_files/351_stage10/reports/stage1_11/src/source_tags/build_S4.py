import json,sys
sys.path.insert(0,'/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags')
from segs import bounds
D='/tmp/claude-103706/-home-zhang-zhiqi2-jlens-work/32eac6b6-5b2f-4d30-b044-a14d510db11a/scratchpad/tags/'
s=open(D+'report_v26_readonly.html',encoding='utf-8').read()
a,b=bounds(s)['S4']; t=s[a:b]
def Z(x): return '<span class="src">（'+x+'）</span>'
def E(x): return '<span class="src">('+x+')</span>'
E1='361_stage11/summary/E1_recovery.csv'
S11='Stage 11 样本 593+593 篇'
S11e='Stage 11 sample 593+593'
P4ZH='probe 只打分第一个名字 token'
P4EN='probe, first name token only'
L=[]
def add(old,tag,new=None,fix=False):
    e={'old':old,'new':(new if new is not None else old)+tag}
    if fix: e['fix']=True
    L.append(e)
# ---------- 6.11 intro
add('593 篇目标组和 593 篇对照组论文，在引用档内配平',Z('Stage 11 抽样，10 个可比引用档；361_stage11/config/protocol.json sample、config/sample.parquet；reports/stage11_report.md 第 3 行'))
add('标题位置读出和作者连写两项用全部 9,108 篇论文',Z('Stage 11 E3 连写、E4 标题位置读出；全部队列 9,108 篇，351_stage10/config/manifest.json n_papers；E3 表中目标 4,621、对照 2,220 篇；361_stage11/summary/E3_chain.csv 列 n_papers'))
add('The sample is 593 target and 593 control papers, balanced within citation bins',E('Stage 11 sampling, 10 comparable citation bins; 361_stage11/config/protocol.json sample, config/sample.parquet; reports/stage11_report.md line 3'))
add('the title-position readout and the author chain use all 9,108 papers',E('Stage 11 E3 chain and E4 title-position readout; whole cohort, 351_stage10/config/manifest.json n_papers; E3 rows have 4,621 target and 2,220 control; 361_stage11/summary/E3_chain.csv n_papers'))
# design
add('共 593 + 593 篇，每 50 篇一个 shard。',Z('设计常量：361_stage11.py:56, 108–117（default_rng(11)）；config/protocol.json sample；9 档各 120 篇、513-1024 档 106 篇，共 24 shard；方法手册 D 第 0 节'))
add('没有对 5 个假标题取平均。',Z('361_stage11.py:57 FALSE_FOR_PATCH'))
add('l = 64 表示什么都不挡、只走同一套显式掩码路径，作为基线。',Z('361_stage11.py:210–216, 254–270 ko_mask()；E2n：config/protocol_amendment_1.json "E2n knockout_name"'))
add('593 + 593 in total, 50 papers per shard.',E('design constants: 361_stage11.py:56, 108–117 (default_rng(11)); config/protocol.json sample; 9 bins x 120 and 106 in 513-1024, 24 shards'))
add('not the mean of the 5.',E('361_stage11.py:57 FALSE_FOR_PATCH'))
add('l = 64 blocks nothing but uses the same explicit-mask path, as the baseline.',E('361_stage11.py:210–216, 254–270 ko_mask(); E2n: config/protocol_amendment_1.json "E2n knockout_name"'))
# patching
add('L52 起达到 1.00</strong>',Z('Stage 11 E1 替换，真标题→false_0，标题之后全部位置，逐层；最终输出名字 token 恢复比例；目标/对照各 593 篇；论文 bootstrap 95% CI；§6.11 恢复比例图与替换表；'+E1))
add('只替换标题的最后一个 token 时，恢复比例只有约 0.12（L8–L40），到 L56 降为 0',Z('Stage 11 E1t，只替换标题最后一个 token，真标题→false_0；最终输出恢复比例；全部 1,186 篇 L8–L40 为 0.12–0.15（目标 0.11–0.13），L56 0.004；§6.11 恢复比例图虚线、替换表 E1t 行；361_stage11/summary/E1t_recovery.csv'))
add('1.00 from L52</strong>',E('Stage 11 E1 patching, true → false_0, all tokens after the title, one layer at a time; final-output recovery share of name tokens; 593 target + 593 control; paper bootstrap 95% CI; §6.11 recovery figure and patching table; '+E1))
add('Patching only the last title token recovers about 0.12 (L8–L40) and nothing from L56',E('Stage 11 E1t, last title token only, true → false_0; final-output recovery; all 1,186 papers 0.12–0.15 at L8–L40 (target 0.11–0.13), 0.004 at L56; §6.11 recovery figure dashed line, E1t table row; 361_stage11/summary/E1t_recovery.csv'))
# knockout
add('从 L52 开始约为 0</strong>',Z('Stage 11 E2 阻断，真标题，标题之后全部位置从第 l 层起不能注意标题；最终输出损失比例（÷ 真标题−false_0 差距）；目标/对照各 593 篇；论文 bootstrap 95% CI；§6.11 阻断图与阻断表；361_stage11/summary/E2_knockout.csv'))
add('如果只阻断 ":" 和名字两个位置，最多只损失 0.15，到 L52 也降为 0',Z('Stage 11 E2n，只阻断 ":" 和名字位置；全部 1,186 篇 L0 0.153，L52 0.006；§6.11 阻断图虚线、阻断表 E2n 行；361_stage11/summary/E2n_knockout.csv'))
add('from L52 about 0</strong>',E('Stage 11 E2 knockout, true title, all tokens after the title blocked from the title from layer l on; final-output loss share (÷ true − false_0 gap); 593 target + 593 control; paper bootstrap 95% CI; §6.11 knockout figure and table; 361_stage11/summary/E2_knockout.csv'))
add('Blocking only ":" and the name positions removes at most 0.15, also 0 by L52',E('Stage 11 E2n, ":" and name positions only; all 1,186 papers 0.153 at L0, 0.006 at L52; §6.11 knockout figure dashed line, E2n table row; 361_stage11/summary/E2n_knockout.csv'))
# E4 title position
add('标题特异信号只有约 0.01–0.03，而且中间层目标组和对照组没有差别',Z('Stage 11 E4，标题最后一个 token，logit lens 与 public J-lens L16–L62，第一个名字 token，真标题 − 5 个假标题平均；目标 4,621、对照 2,220 篇，引用档内目标−对照；§6.11 标题位置表；361_stage11/summary/E4_titlepos_lens.csv'))
add('73% 的作者名以首字母开头',Z('Stage 10 名字格式，24,739 / 33,780 个作者上下文以首字母开头；351_stage10/summary_extra/X1_cond_by_first_role.csv 列 n_contexts（readout=final）'))
add('其中目标 896、对照 499',Z('Stage 13 E4b 复核，团队分折 + 剔除标题复用；目标 R0 788 + R1 108，对照 491 + 8，另 excluded 433、guard 35；381_stage13/summary_cpu_trainstd/E4b_4configs.csv 列 T0_n/T1_n/C0_n/C1_n；PROGRESS.md 2026-10-28 17:55'))
add('（+0.050 / +0.061 / +0.075）',Z('Stage 13 E4b 复核（训练折内标准化），标题最后一个 token，'+P4ZH+'，真标题 − false_0；全部 1,863 篇；论文 bootstrap 95% CI；381_stage13/reports/e4b_trainstd_compare.md Confirmatory 第一张表；summary_cpu_trainstd/compare_E4b_allpapers.csv'))
add('L44 下界 +0.000 在边界上）',Z('Stage 13 E4b 复核，'+P4ZH+'，真标题 − false_0；L24–L60 为 +0.035–+0.078；引用档内目标−对照，目标 896、对照 499 篇；论文 bootstrap 95% CI；381_stage13/reports/e4b_trainstd_compare.md Confirmatory 第二张表；summary_cpu_trainstd/compare_E4b.csv'))
add('没有任何区间从“不含 0”变成“含 0”',Z('指确认版配置（团队分折 + 剔除标题复用）；全部 4 种配置中只有团队分折、未剔除的 L16 一个区间由不含 0 变为含 0；381_stage13/reports/e4b_trainstd_compare.md "Max |new - orig|" 行与 All 4 configurations 表'))
add('目标组高 +0.02 到 +0.04（下表）',Z('Stage 11 E4b 原始，论文分折、未剔除，'+P4ZH+'，真标题 − false_0；目标组 L16 +0.043、L52–56 +0.080/+0.082；引用档内目标−对照 +0.019–+0.039；论文 bootstrap 95% CI；§6.11 标题位置表 probe 行；361_stage11/summary/E4_probe.csv'))
add('about 0.01–0.03 title-specific signal, with no target − control difference in middle layers',E('Stage 11 E4, last title token, logit lens and public J-lens L16–L62, first name token, true − mean of 5 false titles; 4,621 target, 2,220 control, within-bin target − control; §6.11 title-position table; 361_stage11/summary/E4_titlepos_lens.csv'))
add('(+0.050 / +0.061 / +0.075)',E('Stage 13 E4b re-check (training-fold standardisation), last title token, '+P4EN+', true − false_0; all 1,863 papers; paper bootstrap 95% CI; 381_stage13/reports/e4b_trainstd_compare.md, Confirmatory first table; summary_cpu_trainstd/compare_E4b_allpapers.csv'))
add('the L44 lower bound is +0.000)',E('Stage 13 E4b re-check, '+P4EN+', true − false_0; +0.035 to +0.078 at L24–L60; within-bin target − control, 896 target vs 499 control; paper bootstrap 95% CI; 381_stage13/reports/e4b_trainstd_compare.md, Confirmatory second table; summary_cpu_trainstd/compare_E4b.csv'))
add('Largest change 0.0075, no CI changes whether it contains 0.',E('confirmatory configuration; across all 4 configurations one CI (team folds, no exclusion, L16) moves to include 0; 381_stage13/reports/e4b_trainstd_compare.md "Max |new - orig|" line and All 4 configurations table'))
add('73% of names start with an initial',E('Stage 10 name format, 24,739 of 33,780 author contexts; 351_stage10/summary_extra/X1_cond_by_first_role.csv n_contexts (readout=final)'))
# E3 chain
add('目标组 +0.17 到 +0.23，对照组 +0.12 到 +0.18',Z('Stage 11 E3 连写 − 单独打分，真标题，最终输出 L63，作者位置 2 到 4+；目标 4,621、对照 2,220 篇；论文 bootstrap 95% CI；§6.11 连写表 gain 列；361_stage11/summary/E3_chain.csv'))
add('例如目标组第 4 位起的作者从 0.42 降到 0.26',Z('Stage 11 E3，标题特异（真标题 − 5 个假标题平均），单独 +0.421 → 连写 +0.260，最终输出；§6.11 连写表 4+ · target 行；361_stage11/summary/E3_chain.csv'))
add('在引用档内，目标组仍高于对照组 +0.11 到 +0.15',Z('Stage 11 E3 连写，标题特异，引用档内目标−对照，作者位置 2 到 4+（+0.151 / +0.124 / +0.114）；§6.11 连写表；361_stage11/summary/E3_chain.csv'))
add('+0.17 to +0.23 for target, +0.12 to +0.18 for control',E('Stage 11 E3 chain − isolated, true title, final L63, author positions 2 to 4+; 4,621 target, 2,220 control; paper bootstrap 95% CI; §6.11 chain table, gain column; 361_stage11/summary/E3_chain.csv'))
add('(target authors 4+: 0.42 → 0.26)',E('Stage 11 E3, title-specific (true − mean of 5 false titles), isolated +0.421 → chain +0.260, final output; §6.11 chain table; 361_stage11/summary/E3_chain.csv'))
add('target still exceeds control by +0.11 to +0.15',E('Stage 11 E3 chain, title-specific, within-bin target − control, author positions 2 to 4+ (+0.151 / +0.124 / +0.114); §6.11 chain table; 361_stage11/summary/E3_chain.csv'))
# summary
add('（注意力在 L48 读入，MLP 在 L52–56 接手）',Z('Stage 12 P2，标题之后全部位置只替换单层 attention 或 MLP 输出，恢复比例：attention L48 +0.231，MLP L52 +0.178、L56 +0.224；371_stage12/reports/stage12_report.md P2；summary/P2_patch_comp.csv'))
add('早了约 5–10 层',Z('由 Stage 11 E1/E2 的层位与 Stage 10 名字位置 lens 曲线（标题特异目标−对照 L56–L62 上升）对照得出；351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv'))
add('（真假差距 0.42 对 0.21）',Z('Stage 11 E1 分母，最终输出 真标题 − false_0：目标 0.418、对照 0.214；593+593 篇；361_stage11/summary/E1_recovery.csv 列 true_minus_false'))
add('GPU 自检里有两项一致性核对略低于阈值',Z('361_stage11/reports/smoke.json status WARN：ko_baseline_matches_stage10 = 0.704、patch_title_L63_equals_false = 0.704'))
add('L63 的替换恰好恢复 1（标题之后的位置）和 0（标题最后一个 token）',Z('Stage 11 E1 / E1t L63 行：+1.000 [1.000, 1.000] / +0.000 [0.000, 0.000]；§6.11 替换表；361_stage11/summary/E1_recovery.csv、E1t_recovery.csv'))
add('(attention reads it in at L48, MLPs take over at L52–56)',E('Stage 12 P2, single-layer attention or MLP output patched on all tokens after the title, recovery: attention L48 +0.231, MLP L52 +0.178, L56 +0.224; 371_stage12/reports/stage12_report.md P2; summary/P2_patch_comp.csv'))
add('about five to ten layers before it becomes readable',E('from the Stage 11 E1/E2 layers vs the Stage 10 name-position lens curves (title-specific target − control rising at L56–L62); 351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv'))
add('(true − false gap 0.42 vs 0.21)',E('Stage 11 E1 denominator, final output true − false_0: target 0.418, control 0.214; 593+593; 361_stage11/summary/E1_recovery.csv true_minus_false'))
add('Two agreement checks in the GPU smoke test fell slightly below threshold',E('361_stage11/reports/smoke.json status WARN: ko_baseline_matches_stage10 = 0.704, patch_title_L63_equals_false = 0.704'))
add('as patching at L63 recovers exactly 1 (tokens after the title) and 0 (last title token)',E('Stage 11 E1 / E1t L63 rows: +1.000 [1.000, 1.000] / +0.000 [0.000, 0.000]; §6.11 patching table; 361_stage11/summary/E1_recovery.csv, E1t_recovery.csv'))
# ---------- 6.12
A='371_stage12/summary_cpu/A_prior_decomposition.csv'
add('不给标题时，正确名字平均已排在第 12 名左右（−1.09）',Z('Stage 12 名字先验，不给标题，最终输出 L63，全部 9,108 篇、全部名字 token，log10(1/名次) 均值 −1.089 ≈ 第 12.3 名；371_stage12/reports/stage12_cpu_report.md A；'+A+' all_tokens/all'))
add('真标题让平均名次再好约 2.4 倍',Z('Stage 12 A，全部 9,108 篇：真标题 − 假标题 +0.378 → 10^0.378 ≈ 2.4 倍；相对不给标题为 +0.278 ≈ 1.9 倍；'+A+' all_tokens/all'))
add('目标组从约第 146 名提高到约第 24 名',Z('Stage 12 A，姓的第一个 token，目标 4,621 篇，不给标题 −2.164 → 真标题 −1.380（log10(1/名次)）；§6.12 第一张表；'+A))
add('The name prior is large, but concentrated on easy tokens.</b> With no title the correct name already ranks about 12th on average (−1.09)',E('Stage 12 name prior, no title, final L63, all 9,108 papers, all name tokens, mean log10(1/rank) −1.089 ≈ rank 12.3; 371_stage12/reports/stage12_cpu_report.md A; '+A+' all_tokens/all'))
add('The true title improves the average rank by about 2.4×',E('Stage 12 A, all 9,108 papers: true − false +0.378 → 10^0.378 ≈ 2.4×; versus no title +0.278 ≈ 1.9×; '+A+' all_tokens/all'))
add('for target papers from about rank 146 to rank 24',E('Stage 12 A, first surname token, 4,621 target papers, no title −2.164 → true title −1.380 (log10(1/rank)); §6.12 first table; '+A))
add('主题 −0.047（假标题把一部分拉回），论文特有 +0.207',Z('Stage 12 A，全部 token，最终输出 L63，引用档内目标−对照（目标 4,621、对照 2,220 篇），论文 bootstrap 95% CI；§6.12 第二张表；'+A+' tc_* 行'))
add('先验约占差距的三分之一',Z('+0.087 / +0.247 = 0.35；'+A))
add('先验差距约为 0（+0.022，区间跨过 0），论文特有 +0.42',Z('Stage 12 A，姓的第一个 token，引用档内目标−对照：先验 +0.022 [−0.019, +0.063]，论文特有 +0.423 [+0.393, +0.454]；§6.12 第二张表；'+A))
add('topic −0.047 (false titles take part of it back), and paper-specific +0.207',E('Stage 12 A, all tokens, final L63, within-bin target − control (4,621 target, 2,220 control), paper bootstrap 95% CI; §6.12 second table; '+A+' tc_* rows'))
add('the prior is about a third of the gap',E('+0.087 / +0.247 = 0.35; '+A))
add('the prior gap is about 0 (+0.022, CI includes 0) and the paper-specific part is +0.42',E('Stage 12 A, first surname token, within-bin target − control: prior +0.022 [−0.019, +0.063], paper-specific +0.423 [+0.393, +0.454]; §6.12 second table; '+A))
add('而论文特有部分是 +0.329 [+0.312, +0.346]',Z('Stage 12 B，R0/R1 论文 8,894 篇，引用档内中心化，与多选题答对次数（0–4）的 Spearman 相关，bootstrap 95% CI；371_stage12/summary_cpu/B_prior_vs_recognition.csv'))
add('与先验呈负相关（ρ = -0.215）',Z('Stage 12 C，全部 9,108 篇，姓在队列作者中出现次数的 log10 均值与先验的 Spearman；371_stage12/summary_cpu/C_surname_commonness.csv'))
add('目标组的姓反而略不常见',Z('引用档内目标−对照 −0.199 [−0.233, −0.166]；371_stage12/summary_cpu/C_surname_commonness.csv'))
add('against +0.329 [+0.312, +0.346] for the paper-specific part',E('Stage 12 B, 8,894 R0/R1 papers, centred within bins, Spearman with multiple-choice orders right (0–4), bootstrap 95% CI; 371_stage12/summary_cpu/B_prior_vs_recognition.csv'))
add('correlates negatively with the prior (ρ = -0.215)',E('Stage 12 C, all 9,108 papers, Spearman of mean log10 surname count with the prior; 371_stage12/summary_cpu/C_surname_commonness.csv'))
add('and target surnames are slightly less common',E('within-bin target − control −0.199 [−0.233, −0.166]; 371_stage12/summary_cpu/C_surname_commonness.csv'))
add('换成同领域另一篇论文的作者，信号都降为 0',Z('Stage 12 X1 对照，标题最后一个 token，'+P4ZH+'；L24/L40/L56 为 −0.004 到 +0.002，复核后 −0.0045 到 +0.0065，区间都含 0；§6.12 对照表；371_stage12/summary_cpu/X1_probe_controls.csv；381_stage13/summary_cpu_trainstd/X1controls_4configs.csv'))
add('与普通 probe 的 +0.050、+0.066、+0.080 相当或略低',Z('Stage 13 复核，团队分折 + 剔除标题复用，'+P4ZH+'，真标题 − false_0，全部论文（只用假标题训练一行保留 1,568 篇）；381_stage13/reports/e4b_trainstd_compare.md Controls (X1) 表；summary_cpu_trainstd/X1controls_4configs.csv；PROGRESS.md 2026-10-28 17:55'))
add('两种置换对照在复核后仍约为 0',Z('复核后 L24/L40/L56 为 −0.0045 到 +0.0065，区间都含 0；381_stage13/reports/e4b_trainstd_compare.md Controls (X1) 表'))
add('or of a random paper in the same field, drops the signal to 0; training the probe only on false-title pairs makes it stronger.',
    E('Stage 13 re-check, team folds + title reuse removed, '+P4EN+', true − false_0; 381_stage13/reports/e4b_trainstd_compare.md Controls (X1) tables; summary_cpu_trainstd/X1controls_4configs.csv'),
    new='or of a random paper in the same field, drops the signal to 0<span class="src">(Stage 12 X1 controls, last title token, '+P4EN+'; −0.004 to +0.002 at L24/L40/L56, −0.0045 to +0.0065 after the re-check, all CIs include 0; §6.12 controls table; 371_stage12/summary_cpu/X1_probe_controls.csv)</span>; training the probe only on false-title pairs gives a similar signal (re-checked with team folds and title reuse removed: L24 +0.050, L40 +0.057, L56 +0.074, against +0.050, +0.066, +0.080 for the ordinary probe; the earlier "stronger" result came from leakage, the same borrowed title in training and test).',
    fix=True)
# ---------- 6.13
R='351_stage10/reports/r0_sensitivity.md'
add('R1 在目标组有 511 篇（11%），在对照组只有 34 篇（1.5%）',Z('队列 group_tight × recall_level：目标 4,621 = R0 4,110 + R1 511，对照 2,220 = R0 2,186 + R1 34；'+R+' 第一张表'))
add('引用档内可比较的为 3,423 / 2,151）',Z(R+' 第一张表与 Stage 10 表 n 列'))
add('（约小 4%）',Z('Stage 10 R0-only，真标题 − 5 个假标题平均，最终输出 L63，引用档内目标−对照，论文 bootstrap 95% CI；§6.13 表；'+R+'；351_stage10/summary_r0/B_spec_target_vs_control_within_bin_R0.csv'))
add('L62 各读出 +0.22',Z('Stage 10 R0-only，L62：logit +0.220、public +0.221、fitA +0.219、self100 +0.222；'+R))
add('L24–L48 仍约为 0 或略负',Z('Stage 10 R0-only，四种读出 L24–L48 为 −0.049 到 +0.011；'+R))
add('去掉 0-4 低档后为 +0.204',Z('Stage 10 R0-only，去掉 0-2、3-4 档，最终输出，+0.204 [+0.190, +0.217]；'+R+'；351_stage10/summary_r0/B_sens_drop_low_bins_R0.csv'))
add('也只从 +0.247 变为 +0.239',Z('Stage 10 只看真标题，最终输出，引用档内目标−对照：+0.247 [0.230, 0.266] → R0-only +0.239 [0.219, 0.258]；'+R+'；351_stage10/summary_r0/B_true_target_vs_control_within_bin_R0.csv'))
add('R1 makes up 511 targets (11%) but only 34 controls (1.5%)',E('cohort group_tight × recall_level: target 4,621 = R0 4,110 + R1 511, control 2,220 = R0 2,186 + R1 34; '+R+' first table'))
add('3,423 / 2,151 in comparable bins)',E(R+' first table and n column of the Stage 10 table'))
add('(about 4% smaller)',E('Stage 10 R0-only, true − mean of 5 false titles, final L63, within-bin target − control, paper bootstrap 95% CI; §6.13 table; '+R+'; 351_stage10/summary_r0/B_spec_target_vs_control_within_bin_R0.csv'))
add('+0.22 at L62 for every readout',E('Stage 10 R0-only, L62: logit +0.220, public +0.221, fitA +0.219, self100 +0.222; '+R))
add('L24–L48 stay about zero or slightly negative',E('Stage 10 R0-only, four readouts −0.049 to +0.011 at L24–L48; '+R))
add('+0.204 without bins 0-4',E('Stage 10 R0-only, bins 0-2 and 3-4 dropped, final output, +0.204 [+0.190, +0.217]; '+R+'; 351_stage10/summary_r0/B_sens_drop_low_bins_R0.csv'))
add('it goes from +0.247 to +0.239',E('Stage 10 true title only, final output, within-bin target − control: +0.247 [0.230, 0.266] → R0-only +0.239 [0.219, 0.258]; '+R+'; 351_stage10/summary_r0/B_true_target_vs_control_within_bin_R0.csv'))
add('高 <b>+0.110 [0.086, 0.135]</b>',Z('Stage 10，目标组内 R1 − R0，标题特异，最终输出，引用档内（每格 ≥10 篇），R1 485 / R0 3,204 篇，论文 bootstrap 95% CI；'+R+'；351_stage10/summary_r0/target_R1_minus_R0_within_bin.csv'))
add('对组间差的影响约 0.01',Z('+0.207 − +0.199 = 0.008；'+R))
add('R1 只有 41 篇（目标 36、对照 5）',Z(R+' "Stage 11 sample by recall level"'))
add('<b>L52 起 0.99–1.00</b>',Z('Stage 11 E1 R0-only，最终输出恢复比例，目标 557、对照 588 篇；论文 bootstrap 95% CI；'+R+' E1 表；361_stage11/summary_r0/E1_recovery.csv'))
add('从 L0 阻断损失 0.84 / 0.81，从 L52 起约 0',Z('Stage 11 E2 R0-only，最终输出损失比例：L0 0.843 / 0.810，L52 0.004 / 0.010；'+R+' E2 表；361_stage11/summary_r0/E2_knockout.csv'))
add('<b>+0.110 [0.086, 0.135]</b> above R0',E('Stage 10, within target R1 − R0, title-specific, final output, within bins (≥10 per cell), R1 485 / R0 3,204, paper bootstrap 95% CI; '+R+'; 351_stage10/summary_r0/target_R1_minus_R0_within_bin.csv'))
add('so they move the group difference by about 0.01',E('+0.207 − +0.199 = 0.008; '+R))
add('only 41 R1 papers (36 target, 5 control)',E(R+' "Stage 11 sample by recall level"'))
add('<b>0.99–1.00 from L52</b>',E('Stage 11 E1 R0-only, final-output recovery, 557 target, 588 control; paper bootstrap 95% CI; '+R+' E1 table; 361_stage11/summary_r0/E1_recovery.csv'))
add('knockout from L0 loses 0.84 / 0.81, about 0 from L52',E('Stage 11 E2 R0-only, final-output loss share: L0 0.843 / 0.810, L52 0.004 / 0.010; '+R+' E2 table; 361_stage11/summary_r0/E2_knockout.csv'))
# ---------- 7
BS='351_stage10/summary_title/B_spec_target_vs_control_within_bin.csv'
add('在 L62 和输出处最强。',Z('Stage 10，真标题 − 5 个假标题平均，名字位置 logit lens / public J-lens 细层 L50–L62 与最终输出，引用档内目标−对照（3,734 vs 2,182 篇）；logit L50 +0.007，L56 +0.065，L60 +0.178，L62 +0.229，输出 +0.207；§6.4；'+BS))
add('strongest at L62 and the output.',E('Stage 10, true − mean of 5 false titles, name positions, logit lens / public J-lens fine layers L50–L62 and final output, within-bin target − control (3,734 vs 2,182); logit L50 +0.007, L56 +0.065, L60 +0.178, L62 +0.229, output +0.207; §6.4; '+BS))
add('（control 组到 L54–56；对 5 个假标题都成立）',Z('Stage 11 E2 与 Stage 13 X7 阻断，论文特有损失 S(L52)：目标 +0.018、对照 +0.051、对照 S(L54) +0.018、S(L56) +0.000；Stage 13 X6 用 5 个假标题替换，各假标题 R(L52) 0.984–1.017；381_stage13/reports/x7_report.md、x6_report.md'))
add('(L54–56 for control; the same for all 5 false titles)',E('Stage 11 E2 and Stage 13 X7 knockout, paper-specific loss S(L52): target +0.018, control +0.051, control S(L54) +0.018, S(L56) +0.000; Stage 13 X6 patching with each of 5 false titles, R(L52) 0.984–1.017; 381_stage13/reports/x7_report.md, x6_report.md'))
add('相对对照组的优势只出现在最后两层',Z('Stage 10 主轮层 L24–L62 与最终输出，名字位置，标题特异引用档内目标−对照，三种 J-lens 在 L56 约为 0（+0.003 到 +0.009）、L62 约 +0.23，输出 +0.207；logit lens 在 L56 已有 +0.065 [0.050, 0.080]；§6.4；'+BS+'；R0+R1 数值见 '+R))
add('（+0.05 到 +0.08）',Z('Stage 13 E4b 复核，团队分折 + 剔除标题复用，'+P4ZH+'，真标题 − false_0，全部 1,863 篇，L24–L60；381_stage13/reports/e4b_trainstd_compare.md Confirmatory 第一张表'))
add('目标组比对照组高（+0.04 到 +0.08，置信区间在 0 以上）',
    Z('Stage 13 E4b 复核，'+P4ZH+'，引用档内目标−对照，目标 896、对照 499 篇，L24–L60 为 +0.035–+0.078，论文 bootstrap 95% CI；381_stage13/reports/e4b_trainstd_compare.md Confirmatory 第二张表'),
    new='目标组比对照组高（+0.03 到 +0.08，置信区间在 0 以上）',fix=True)
add('their advantage over control appears only in the last two layers',E('Stage 10 main-round layers L24–L62 and final output, name positions, title-specific within-bin target − control, the three J-lenses are about 0 at L56 (+0.003 to +0.009) and about +0.23 at L62, output +0.207; the logit lens already gives +0.065 [0.050, 0.080] at L56; §6.4; '+BS))
add('from L24 on (+0.05 to +0.08)',E('Stage 13 E4b re-check, team folds + title reuse removed, '+P4EN+', true − false_0, all 1,863 papers, L24–L60; 381_stage13/reports/e4b_trainstd_compare.md, Confirmatory first table'))
add('(target − control +0.04 to +0.08, CIs above zero; re-checked with team folds and title reuse removed)',
    E('Stage 13 E4b re-check, '+P4EN+', within-bin target − control, 896 target vs 499 control, +0.035 to +0.078 at L24–L60, paper bootstrap 95% CI; 381_stage13/reports/e4b_trainstd_compare.md, Confirmatory second table'),
    new='(target − control +0.03 to +0.08, CIs above zero; re-checked with team folds and title reuse removed)',fix=True)
add('输出处的差从 +0.207 变为 +0.199，结论不变（§6.13）。',Z('Stage 10，真标题 − 5 个假标题平均，最终输出 L63，引用档内目标−对照，R0-only 3,423 vs 2,151 篇；'+R))
add('it goes from +0.207 to +0.199 at the output',E('Stage 10, true − mean of 5 false titles, final L63, within-bin target − control, R0-only 3,423 vs 2,151; '+R))
add('三种 Jacobian lens 的结论一致。',Z('Stage 10 X3：public、self100、fitA 三种 J-lens 与 logit lens，主轮 6 层，全部论文；351_stage10/summary_extra/X3_means.csv、X3_tc_spec_vs_logit.csv'))
add('all three Jacobian lenses agree.',E('Stage 10 X3: public, self100 and fitA J-lenses vs logit lens, 6 main-round layers, all papers; 351_stage10/summary_extra/X3_means.csv, X3_tc_spec_vs_logit.csv'))
add('后续 token 总体只容易一点（+0.04）',Z('Stage 10 §6.7 X1_cond，最终输出，全部论文 33,780 个作者上下文，第 1 个 token 进前 10 与否的后续 token 均值差 +0.041 [0.029, 0.052]；351_stage10/summary_extra/X1_cond.csv（unit=token, group=all）'))
add('姓明显更容易（+0.22）',Z('Stage 10 §6.7，完整的名开头的 8,876 个上下文，最终输出，差 +0.222 [0.165, 0.275]；首字母开头 −0.009 [−0.031, +0.013]；351_stage10/summary_extra/X1_cond_by_first_role.csv'))
add('only slightly easier overall (+0.04)',E('Stage 10 §6.7 X1_cond, final output, 33,780 author contexts, later-token mean if first token in top 10 vs not, +0.041 [0.029, 0.052]; 351_stage10/summary_extra/X1_cond.csv (unit=token, group=all)'))
add('makes the surname clearly easier (+0.22)',E('Stage 10 §6.7, 8,876 contexts starting with a full given name, final output, +0.222 [0.165, 0.275]; initial first −0.009 [−0.031, +0.013]; 351_stage10/summary_extra/X1_cond_by_first_role.csv'))
add('（目标组从 +0.35 到 +0.64）',Z('Stage 10，真标题 − 5 个假标题平均，最终输出，目标组各引用档均值，0-2 档 +0.347 到 4097+ 档 +0.644；351_stage10/summary_title/A_group_bin_layer.csv（readout=final）；组内 Spearman 见 summary_title/E_citation_within_group.csv'))
add('(target group from +0.35 to +0.64)',E('Stage 10, true − mean of 5 false titles, final output, target mean per citation bin, +0.347 in 0-2 to +0.644 in 4097+; 351_stage10/summary_title/A_group_bin_layer.csv (readout=final); within-group Spearman in summary_title/E_citation_within_group.csv'))
# ---------- 8
add('从 0.25 放宽到 0.5',Z('Stage 10 parity：final@L63 最大 |logit 差| 0.367；351_stage10/reports/parity.json tolerance_amendment、runs[1].max_abs_logit_diff'))
add('raised from 0.25 to 0.5',E('Stage 10 parity: final@L63 max |logit diff| 0.367; 351_stage10/reports/parity.json tolerance_amendment, runs[1].max_abs_logit_diff'))
add('（4097+ 档为 0）',Z('队列 group_tight × 引用档：4097+ 档目标 84、对照 0，2049-4096 档 264 / 9；cohort/papers.parquet；方法手册 B3'))
add('(none in 4097+)',E('cohort group_tight × citation bin: 4097+ has 84 target, 0 control; 2049-4096 264 / 9; cohort/papers.parquet; methods handbook B3'))
add('目标组 11% 是 R1（写对少数作者）、对照组只有 1.5%',Z('目标 511 / 4,621、对照 34 / 2,220；'+R+' 第一张表'))
add('11% of target papers are R1 (a few authors right) against 1.5% of controls',E('target 511 / 4,621, control 34 / 2,220; '+R+' first table'))
add('通过与否的一致率为 83.6%（kappa 0.63），也就是约六分之一论文的分组会变',Z('标注包 team_b，500 篇第二套干扰团队；1 − 0.836 ≈ 1/6；labels_20261015/.../label_README.md:8-9'))
add('the pass label agrees 83.6% of the time (kappa 0.63), so about one paper in six would change group',E('label package team_b, 500 papers with a second distractor draw; 1 − 0.836 ≈ 1/6; labels_20261015/.../label_README.md:8-9'))
add('（self100 和 fitA 只拟合了 6–7 个层，要加细层需要重新拟合）',Z('351_stage10/config/lenses.json source_layers：self100 6 层（L24–L62），fitA 7 层（L16–L62）'))
add('只用了主轮的 6 个层',Z('351_stage10.py:42 DEFAULT_LAYERS（L24, 32, 40, 48, 56, 62）；351_stage10/summary_extra/'))
add('(self100 and fitA were fitted at 6–7 layers, so fine layers would need new fits)',E('351_stage10/config/lenses.json source_layers: self100 6 layers (L24–L62), fitA 7 layers (L16–L62)'))
add('use the 6 main-round layers',E('351_stage10.py:42 DEFAULT_LAYERS (L24, 32, 40, 48, 56, 62); 351_stage10/summary_extra/'))
json.dump(L,open(D+'S4.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for i,e in enumerate(L):
    c=t.count(e['old'])
    if c!=1: print('COUNT',c,i,e['old'][:60])
print(len(L))
