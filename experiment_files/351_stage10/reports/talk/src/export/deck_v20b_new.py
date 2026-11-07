"""2026-11-06 b (deck stays v20, unpublished): deck_v20_new.SLIDES with the user-confirmed batch-1 results (PROGRESS 2026-11-06 ~13:30 a-e):
slide 72 'alltok' (surname target - control = wording a; note box: five false titles + C-3 / C-3b), slide 75 divider line 3,
slide 81 'pd5' (batch 1 done / P1-P2 running 116/194, batch 2 code ready + auto start + D12-1..3, batch 3 code in progress).
deck_v20_new.py itself is not edited; this module re-uses its SLIDES / html_section / slide_text and replaces three specs."""
from deck_v20_new import *          # noqa: F401,F403  (SLIDES, S, T, B, html_section, slide_text)
import deck_v20_new as _N

BY = {s['key']: s for s in SLIDES}
R13 = '381_stage13/reports/'

# ---- slide 72: all-token probe
a = BY['alltok']
old = [T('mainly initials and given names (positive from L24–L32, +0.02 to +0.09); surname first token ≈ 0 at L16–L52, +0.04 to +0.06 only at L56–L60'), S('(within bin; same, §3)')]
i = next(k for k, b in enumerate(a['left']) if b[0] == B('Target − control: ')); assert a['left'][i][1:] == old
a['left'][i] = [B('Target − control: '), T('mainly initials and given names (positive from L24–L32); surname first token, five false titles with per-donor exclusion: positive from L24 (L40 +0.030, L56 +0.058)'),
                S('(within bin; b1_e4b5_report.md, per-donor)'), T('; with false_0 only (fewer papers) not significant before L56')]
a['note'] = ('Five false titles (batch 1)', 'Per-donor exclusion, 4,654 papers: surname L40 +0.076, surname − initial +0.033. Without the title-reuse exclusion (C-3, C-3b) the signals are unchanged but include leakage: sensitivity only. (b1_e4b5_report.md; c13_C3b.md)')
a['notes'] = a['notes'].replace(
    '；姓的第一个 token 在 L16–L52 约为 0，L56–L60 才出现 +0.04 到 +0.06〔同上，L56 +0.058、L60 +0.043〕。',
    '；按逐个假标题排除、5 个假标题平均，姓的第一个 token 的 target − control 从 L24 起为正（L40 +0.030〔引用档内 target − control，[0.013, 0.048]，团队聚类 95% CI；'
    + R13 + 'b1_e4b5_report.md “Per-donor exclusion” 节〕，L56 +0.058〔同上，[0.039, 0.078]〕）；只用 false_0、样本较小时，L56 前不显著〔false_0 版本，1,395 篇；同一报告 V0 表〕。')
assert 'L40 +0.030' in a['notes']
a['notes'] = a['notes'].replace('不剔除标题复用的敏感性分析（补充 13 C-3）含泄漏，只作敏感性分析。',
    '批次 1 第 4 项（2026-11-06）：E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题）：L40 姓首 token +0.076 [0.068, 0.083]，姓 − 首字母 +0.033 [0.023, 0.042]，原 E4b 第一个 token +0.066；置换对照首字母仍 +0.018，其余 ≈ 0；硬检查 E4b L40 +0.0609 PASS〔'
    + R13 + 'b1_e4b5_report.md 第 2 节与 “Per-donor exclusion” 节，目标 + 对照，团队聚类 95% CI〕。不剔除标题复用的敏感性分析（补充 13 C-3、C-3b）含泄漏，只作敏感性分析，不作结论：C-3b 硬检查 PASS，L40 姓的第一个 token +0.077 [0.071, 0.084]、首字母 +0.034 [0.029, 0.039]、姓 − 首字母 +0.043 [0.035, 0.051]〔6,841 篇；'
    + R13 + 'c13_C3b.md〕，target − control 的区间几乎处处在 0 以上，与 C-3 一样。')
assert 'C-3b' in a['notes']

# ---- slide 75: divider
d = BY['pd0']
j = next(k for k, b in enumerate(d['left']) if b[0][1].startswith('3. Redo programme'))
d['left'][j] = [T('3. Redo programme (addenda 10–14): done, batch 1 (only P1 / P2 with five false titles still running), batches 2 and 3; limits that cannot be redone')]

# ---- slide 81: redo programme
p = BY['pd5']
p['left'] = [
   [B('Done: '), T('X7 with five false titles; all-token probe (addendum 9); CPU items C-1 to C-5; C-3b (no-exclusion sensitivity, includes leakage, not a conclusion)')],
   [B('Batch 1, done: '), T('X1–X4 for all authors → conclusions unchanged (X1 task-independent, small L48 author − year +0.024; X3 keeps ≈ 90%; X4 from L8; X2 moves 0.032, subspace R² ≤ 0.009, H3 still insufficient)'),
    S('(b1_xall_report.md)'), T(' · E4b minus five false titles: surname L40 +0.076 [0.068, 0.083], surname − initial +0.033'), S('(b1_e4b5_report.md)')],
   [B('Batch 1, running: '), T('P1 / P2 with five false titles — 116 / 194 units done, 78 left in three parallel chains; result after approval')],
   [B('Batch 2 (addenda 11, 12): '), T('code, tiny tests and hard-check unit tests done; starts automatically after batch 1; deviations recorded (D12-1 to D12-3; 2-7 source = year-free X4 prompt)'),
    S('(prereg_addendum12_deviations.json)')],
   [B('Batch 3 (addendum 14): '), T('3-1 Stage 10 L41–L47, L49 · 3-2 L0–L23 · 3-3 Stage 7.1B fast path: code in progress; 3-4 / 3-5 (Stage 8 GPU W) not run'), S('(prereg_addendum14.json)')],
   [B('Not done: '), T('Stage 8 GPU re-run of the original W (user decision 2026-11-06; CPU proxy C-2 instead)'), S('(c13_C2.md)')]]
p['notes'] = ('重做计划（补充 10–14，规则都在看结果前写定并锁定；复现已发表数字是每一项的硬检查）。已完成：X7 五个假标题、补充 9 全部名字 token 的 probe、CPU 项 C-1 到 C-5〔381_stage13/reports/b1_x7f_report.md、e4b_alltok.md、c13_C1.md–c13_C5.md〕；C-3b（不剔除标题复用，只作敏感性分析，含泄漏，不作结论）〔c13_C3b.md〕。'
              '批次 1 已完成：X1–X4 改为给全部作者打分（全部名字 token），并按作者排位分层。结论都不变：X1 仍与任务无关，L48 有一点小而确实的任务依赖（作者 − 年份 +0.024 [0.019, 0.030]）；X3 改写标题保留约 90% 的作者偏好，target 与 control 一样；X4 从 L8 起可解码出作者，各作者排位相同，认得出的论文在 L8–L40 更高；但只靠标题文字的基线不弱于 Qwen，仍不能排除标题文字的解释。X2 用全部作者重新拟合作者子空间后，搬动量从 0.016 升到 0.032（完整替换的约 7%），但子空间本身仍几乎解码不出作者（留出 R² ≤ 0.009），H3 仍证据不足〔补充 10 第 1 项，硬检查 PASS；381_stage13/reports/b1_xall_report.md〕。'
              'E4b 5 个假标题（偏离 D1 逐个假标题排除，保留 4,654 篇，平均 1.5 个假标题）：L40 姓首 token +0.076 [0.068, 0.083]，姓 − 首字母 +0.033 [0.023, 0.042]，原 E4b 第一个 token +0.066；置换对照首字母仍 +0.018，其余 ≈ 0；硬检查 E4b L40 +0.0609 PASS〔381_stage13/reports/b1_e4b5_report.md〕。'
              '批次 1 还在运行：P1/P2 用 5 个假标题，194 个单元已完成 116 个，其余 78 个分三条并行作业链计算，结果经用户确认后补入。'
              '批次 2（补充 11、12）：代码、tiny 测试和硬检查的单元测试都已完成，批次 1 结束后由编排作业自动开始；与预注册的出入记在补充 12 出入记录 D12-1 到 D12-3（2-1、2-2 用较省但包含原始提示逐位复现重拟合的硬检查；2-11 重建标签、论文内 AUROC、两个基线、对照组只作描述）〔381_stage13/config/prereg_addendum12_deviations.json〕，2-7 的来源改用不含年份的 X4 提示。'
              '批次 3（补充 14）：3-1、3-2、3-3 代码在写；3-4、3-5 不做（Stage 8 按原 W 的 GPU 重算，用户 2026-11-06 决定）〔381_stage13/config/prereg_addendum14.json〕。')
p['title'] = 'Redo programme (addenda 10–14)'
p['sub'] = 'All rules fixed before the results · reproducing the published numbers is a hard check for every item · status 2026-11-06 evening'
assert _N.SLIDES is SLIDES
