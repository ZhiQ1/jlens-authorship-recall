"""Addendum 20 into conclusions_v30_draft.md (C35, H2 status, table row, change list) + repo copy + repo README (2026-11-20).
Backups .before_20261120_a20; rebuild from backup each run."""
import shutil, os
H = os.path.expanduser('~/jlens_work/')
REPO = '/scratch/zhang.zhiqi2/jlens-authorship-recall_update/'
V = 'H2 部分支持——存在真实论文成分，但大部分信号可由语义相似解释'


def edit(path, ops):
    bk = path + '.before_20261120_a20'
    if not os.path.exists(bk):
        shutil.copy2(path, bk)
    t = open(bk, encoding='utf-8').read()
    for anchor, new, mode in ops:
        assert t.count(anchor) == 1, (path, anchor[:60], t.count(anchor))
        t = t.replace(anchor, anchor + new if mode == 'after' else new + anchor if mode == 'before' else new)
    open(path, 'w', encoding='utf-8').write(t)
    print('edited', path)


C35 = ('### C35 〔确认（补充 20，锁定的确认性检验，2026-11-20）〕' + V + '：意思相近但不存在的虚构标题恢复“真 − 假标题差距”的 75%（φ_T = 0.751 [0.723, 0.778]），只有真标题才给的部分 R̄_T = +0.106 [0.094, 0.118]\n\n'
       '- **结论**：为 Stage 11 样本中的 1,127 篇论文（566 target、561 control；59 篇按生成规则事先排除）各写一个意思相近、但不存在的虚构标题（Qwen3-32B 生成；与队列标题和 Crossref 检索结果都不重合；与真标题 mpnet 余弦中位数 0.65，假标题 0.09，X3 同义改写 0.97），同一提示、同一年份打分。'
       'target 组最终输出（L63）：φ_T = ΣA/ΣG = 0.751 [0.723, 0.778]（A = 虚构 − 5 个假标题平均，G = 真 − 5 个假标题平均），R̄_T = mean(真 − 虚构) = +0.106 [0.094, 0.118]（Ḡ_T 0.425 [0.406, 0.445]，Ā_T 0.319 [0.301, 0.338]）。'
       '按锁定规则（R̄_T 区间全部大于 0、φ̂_T ≥ 0.5）判为“' + V + '”；φ_T 区间不跨 0.3 或 0.5，不是临界。\n'
       '- **数字**（次要，描述性）：control φ_C 0.770 [0.727, 0.814]、R̄_C +0.050 [0.039, 0.061]（561 篇）；同一引用档内 R_T − R_C +0.056 [0.039, 0.072]（H2 预测的方向），φ_T − φ_C −0.022 [−0.081, 0.033]；'
       'R̄ 只在 L56–L63 明显大于 0（logit L62 +0.089 [0.073, 0.105]，J-lens L62 +0.115 [0.101, 0.131]）；以虚构标题为供体的尾部替换从 L52 起恢复约 0.745，真标题 1.00（L54 差 +0.255 [0.227, 0.284]）；'
       '标题位置 probe 真 − 虚构 +0.02 到 +0.04，真 − false_0 +0.06 到 +0.10（target）；M2：领域准确率不变，L48 引用数 R² 0.36 → 0.10（全部 1,127 篇，Δ +0.26 [0.20, 0.33]）；'
       '语义剂量：按余弦三分位 φ_T 0.722 / 0.740 / 0.794（第 3 − 第 1 分位 +0.072 [0.002, 0.140]）；敏感性 a–f 中 φ_T 0.708–0.778，R̄_T 都大于 0，判定不变；标题 token 平均 log 概率 真 − 虚构 target −0.12、control −0.25（虚构标题更“典型”）。\n'
       '- **出处**：`R391/summary_a20/a20_report.md`、`primary_secondary_sensitivity.csv`、`perpaper_final63.csv`、`S3_layer_profile.csv`、`S4_E1_fict_donor.csv`、`S5_E4b_probe.csv`、`S6_M2_attributes.csv`、`a20_results.json`；'
       'GPU 作业 12015462、12015463（H200），分析 `~/jlens_work/15_h2fict/h2_main_analyze.py`；团队整群 bootstrap 2,000 次（seed 20261120）；规则 `R391/config/prereg_addendum20.md`（sha256 fee691de…，2026-11-20 锁定）；标题集 `R391/h2_fictitious/v3/selected_v3b.csv`（sha256 7b8dd31d…）。\n'
       '- **相对 v29**：新增。H2 的总体判断由“部分支持但未确立”改写为“部分支持：存在真实论文成分，但大部分信号可由语义相似解释”（同一档“部分支持”，依据改为锁定检验）。\n'
       '- 〔前提：单一模型；S_真、S_假 用已存 A100 Stage 10 值，S_虚构 用本次 H200 运行，一致性检查 WARN（名次完全相同比例 0.55–0.66 < 0.75，平均 |Δlog10 名次| ≤ 0.014）；'
       '虚构标题由同一模型生成，可能更典型；0.5 和 0.3 的界限是在知道 X3 结果后定的；标题位置 probe 和 M2 读出按已发表设置重拟合（原未存权重）；第一次运行的冻结脚本把真标题当作虚构标题（φ = 1、R = 0），已作废并修正重跑，GPU 共 1.08 小时，其中无效 0.55〕\n\n')

cf = H + 'conclusions_v30_draft.md'
edit(cf, [
    ('### 进行中（只写状态，不写结果）\n', C35, 'before'),
    ('- **补充 19**（瓶颈 F 曝光门槛）：', '- **补充 20**（H2 虚构标题）：2026-11-20 锁定（`R391/config/prereg_addendum20.md`，sha256 fee691de…），已完成（GPU 1.08 小时，含无效的第一次运行 0.55），见 C35。\n', 'before'),
    ('H1 在 ":" 和名字位置成立；H2 部分支持但未确立；', 'H1 在 ":" 和名字位置成立；' + V + '（补充 20，锁定的确认性检验，2026-11-20：φ_T 0.751 [0.723, 0.778]，R̄_T +0.106 [0.094, 0.118]）；', 'replace'),
    ('当前总体判断（2026-11-09、2026-11-14 更新 H3）', '当前总体判断（2026-11-09、2026-11-14 更新 H3；2026-11-20 更新 H2）', 'replace'),
    ('意思比字面重要，分不开论文身份 |\n', '| C35 | 确认（补充 20，锁定的确认性检验） | H2 | 部分支持（存在真实论文成分，但语义相似解释大部分） | 虚构标题恢复 φ_T 0.751 [0.723, 0.778]；只有真标题给的 R̄_T +0.106 [0.094, 0.118]；control φ 0.770、R̄ +0.050；R_T − R_C +0.056 [0.039, 0.072] |\n', 'after'),
    ('数字不变。**措辞**。\n', '22. **C35 H2 虚构标题（2026-11-20，补充 20 锁定的确认性检验）**：φ_T = 0.751 [0.723, 0.778]，R̄_T = +0.106 [0.094, 0.118] → ' + V + '。H2 的总体判断措辞随之改写，档次仍为“部分支持”。**新增**。\n', 'after'),
])
shutil.copy2(cf, REPO + 'docs/conclusions_v30.md'); print('copied to repo docs/conclusions_v30.md')

rd = REPO + 'README.md'
EN = ('**Latest (2026-11-20).** **H2 fictitious titles (addendum 20, locked confirmatory test, 2026-11-20):** each of 1,127 papers of the Stage 11 sample (566 target, 561 control) got a fictitious title close in meaning to the real one that does not exist '
      '(median mpnet cosine 0.65 vs 0.09 for the false titles). In the target group (final L63) it recovers φ_T = 0.751 [0.723, 0.778] of the true − false-title gap; what only the real title gives is R̄_T = +0.106 [0.094, 0.118]. '
      'By the locked rule: **H2 partly supported — a real-paper component exists, but meaning similarity explains most of the signal** (not borderline; unchanged in all sensitivity analyses, φ_T 0.708–0.778). '
      'Control φ_C 0.770 [0.727, 0.814], R̄_C +0.050 [0.039, 0.061]; within-bin R_T − R_C +0.056 [0.039, 0.072]. Parity WARN (exact-rank share 0.55–0.66 < 0.75), numbers kept. '
      '<sub>(391_groups/summary_a20/a20_report.md; team-cluster bootstrap, 2,000 draws)</sub>\n\n')
edit(rd, [
    ('**Latest (2026-11-19).**', EN, 'before'),
    ('H2 partly supported, not established;', 'H2 partly supported: a real-paper component exists, but meaning similarity explains most of the signal (addendum 20, locked, 2026-11-20: φ_T 0.751 [0.723, 0.778], R̄_T +0.106 [0.094, 0.118]);', 'replace'),
    ('| Addendum 18b |', '| Addendum 20 (H2) | fictitious titles close in meaning: real paper vs title meaning | φ_T 0.751 [0.723, 0.778], R̄_T +0.106 [0.094, 0.118]: H2 partly supported, meaning similarity explains most | done (locked confirmatory test, 2026-11-20) | 391_groups/summary_a20/ |\n', 'before'),
])
