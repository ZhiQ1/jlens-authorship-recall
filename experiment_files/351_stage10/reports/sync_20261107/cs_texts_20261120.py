"""Texts for the exploratory citation median split (direction 3), 2026-11-20. Numbers from
381_stage13/summary_explore_citesplit_20261120/report.md, recovery_by_half.csv, lens_tc_by_half.csv (checked 2026-11-20)."""
SRC = '381_stage13/summary_explore_citesplit_20261120/report.md、recovery_by_half.csv、lens_tc_by_half.csv；团队整群 bootstrap 2,000 次'
SRC_EN = '381_stage13/summary_explore_citesplit_20261120/report.md, recovery_by_half.csv, lens_tc_by_half.csv; team-cluster bootstrap, 2,000 draws'
CS = ('<b>按引用数分半（探索性，事后，未预注册）：</b>把 Stage 11 样本 1,186 篇按引用数中位数 31 分成两半（等于 31 的归低半；低半 target 297 + control 297 篇，高半 296 + 296 篇）。'
      '替换恢复比例 R（5 个假标题平均）在引用多的一半略低：L48 低半 0.865 [0.843, 0.886]、高半 0.789 [0.770, 0.808]，高 − 低 −0.076 [−0.104, −0.046]（target −0.079、control −0.073）；'
      'L52 高 − 低 −0.018 [−0.029, −0.007]。R 的 target − control 两半没有差别（L48 高 − 低 −0.006 [−0.072, +0.065]）；logit lens 的 target − control 在 L40–L56 两半也没有差别。'
      'public J-lens 的 target − control 在高半更负：高半 L48–L55 区间都在 0 以下，高 − 低在 L53–L55 区间不含 0（L53 −0.073 [−0.138, −0.010]）；'
      '全队列补充分析（中位数 66）中 L40–L56 的高 − 低区间都在 0 以下（L48 −0.065 [−0.093, −0.038]）。'
      '读法（探索性）：引用多的论文，信息到达名字位置略晚；target − control 的时间与引用数无关；J-lens 中间层的负值在引用多的论文中更强。')
CSs = ('按引用数分半（探索性，事后，未预注册；Stage 11 样本，中位数 31）：引用多的一半信息到达略晚（R(L48) 0.789 对 0.865，高 − 低 −0.076 [−0.104, −0.046]；L52 −0.018 [−0.029, −0.007]），'
       'target − control 的时间与引用数无关（L48 −0.006 [−0.072, +0.065]）；J-lens 中间层的负值在引用多的论文中更强（L53 −0.073 [−0.138, −0.010]；全队列中位数 66：L48 −0.065 [−0.093, −0.038]）。')
CS_EN = ('Citation median split (exploratory, post hoc, not pre-registered): the 1,186 Stage 11 papers split at the median of 31 citations (ties to the low half; low 297 + 297, high 296 + 296 target + control). '
         'Recovery R (5-title mean) is slightly lower in the more-cited half: L48 low 0.865 [0.843, 0.886], high 0.789 [0.770, 0.808], high − low −0.076 [−0.104, −0.046] (target −0.079, control −0.073); L52 −0.018 [−0.029, −0.007]. '
         'Target − control of R does not differ between halves (L48 −0.006 [−0.072, +0.065]); nor does the logit-lens target − control at L40–L56. '
         'The public J-lens target − control is more negative in the high half (high − low CI excludes 0 at L53–L55, L53 −0.073 [−0.138, −0.010]; full-cohort supplement, median 66: L48 −0.065 [−0.093, −0.038]). '
         'Reading (exploratory): in more-cited papers the information arrives slightly later; the target − control timing does not depend on citations; the J-lens middle-layer negativity is stronger for more-cited papers.')
