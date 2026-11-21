"""Citation median split (exploratory) into conclusions (C36) + repo copy + repo README, 2026-11-20. Backups .before_20261120_cs."""
import shutil, os
H = os.path.expanduser('~/jlens_work/'); REPO = '/scratch/zhang.zhiqi2/jlens-authorship-recall_update/'
def edit(path, ops):
    bk = path + '.before_20261120_cs'
    if not os.path.exists(bk): shutil.copy2(path, bk)
    t = open(bk, encoding='utf-8').read()
    for a, new, mode in ops:
        assert t.count(a) == 1, (path, a[:60], t.count(a))
        t = t.replace(a, a + new if mode == 'after' else new + a if mode == 'before' else new)
    open(path, 'w', encoding='utf-8').write(t); print('edited', path)
C36 = ('### C36 〔未定（探索性，事后，未预注册）〕按引用数分半：引用多的论文信息到达名字位置略晚；target − control 的时间与引用数无关；J-lens 中间层的负值在引用多的论文中更强\n\n'
       '- **结论**：Stage 11 样本 1,186 篇按引用数中位数 31 分半（等于 31 的归低半；低半 target 297 + control 297，高半 296 + 296）。替换恢复比例 R（5 个假标题平均）L48 低半 0.865 [0.843, 0.886]、高半 0.789 [0.770, 0.808]，高 − 低 −0.076 [−0.104, −0.046]（target −0.079 [−0.111, −0.045]、control −0.073 [−0.136, −0.016]）；L52 高 − 低 −0.018 [−0.029, −0.007]。'
       'R 的 target − control 两半没有差别（L48 高 − 低 −0.006 [−0.072, +0.065]；L52 −0.016 [−0.044, +0.011]）；logit lens 的引用档内 target − control 在 L40–L56 两半没有差别。public J-lens 的 target − control 在高半更负（高半 L48–L55 区间都在 0 以下；高 − 低在 L53–L55 区间不含 0，L53 −0.073 [−0.138, −0.010]、L54 −0.076 [−0.141, −0.012]、L55 −0.073 [−0.145, −0.006]）；'
       '全队列补充分析（target / control，中位数 66）中 L40–L56 高 − 低区间都在 0 以下（L48 −0.065 [−0.093, −0.038]）。读法（探索性）：引用多的论文，信息到达略晚；target − control 的时间与引用数无关；J-lens 中间层的负值在引用多的论文中更强。\n'
       '- **出处**：`R13/summary_explore_citesplit_20261120/report.md`（A、B 节与 Supplement 表）、`recovery_by_half.csv`、`lens_tc_by_half.csv`、`info.json`；团队整群 bootstrap 2,000 次（default_rng(13)，所有比较共用一套抽样）；复现检查 R(L48) 0.8211、R(L52) 0.9955 与已发表值一致（差 1e-16）。\n'
       '- **相对 v29**：新增（探索性）。与 C02、C04 的到达时间并列，不改变它们。\n'
       '- 〔前提：事后、探索性、未预注册；单一模型；分半是按引用档分层的样本，不是总体比例；R 的 target − control 为普通差（同已发表 E1），lens 的 target − control 在引用档内；J-lens 高 − 低在 L48–L52 和 L56 的区间含 0〕\n\n')
cf = H + 'conclusions_v30_draft.md'
edit(cf, [
    ('### 进行中（只写状态，不写结果）\n', C36, 'before'),
    ('只有真标题给的 R̄_T +0.106 [0.094, 0.118]；control φ 0.770、R̄ +0.050；R_T − R_C +0.056 [0.039, 0.072] |\n',
     '| C36 | 未定（探索性，事后） | — | 时间框架 | 按引用数分半：引用多的一半 R(L48) 低 −0.076 [−0.104, −0.046]，target − control 时间两半相同；J-lens 中间层负值在引用多的一半更强（L53 −0.073 [−0.138, −0.010]） |\n', 'after'),
    ('档次仍为“部分支持”。**新增**。\n', '23. **C36 按引用数分半（2026-11-20，探索性，事后）**：引用多的论文信息到达略晚（R(L48) 高 − 低 −0.076 [−0.104, −0.046]），target − control 时间与引用数无关，J-lens 中间层负值在引用多的论文中更强。**新增（探索性）**。\n', 'after'),
])
shutil.copy2(cf, REPO + 'docs/conclusions_v30.md'); print('repo copy updated')
EN = ('**Latest (2026-11-20, exploratory).** Citation median split of the 1,186 Stage 11 papers (median 31; post hoc, not pre-registered): recovery R at L48 is slightly lower in the more-cited half (0.789 vs 0.865, high − low −0.076 [−0.104, −0.046]; L52 −0.018 [−0.029, −0.007]); '
      'target − control timing does not differ between halves (L48 −0.006 [−0.072, +0.065]); the J-lens middle-layer negativity is stronger in the more-cited half (L53 −0.073 [−0.138, −0.010]; full cohort, median 66: L48 −0.065 [−0.093, −0.038]). '
      '<sub>(381_stage13/summary_explore_citesplit_20261120/report.md; team-cluster bootstrap, 2,000 draws)</sub>\n\n')
edit(REPO + 'README.md', [('**Latest (2026-11-20).**', EN, 'before')])
