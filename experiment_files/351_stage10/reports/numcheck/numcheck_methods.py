"""How each result file was computed (prose only, no numbers copied from results).
Taken from STATUS.md §2–§3, the earlier check page (PPT v19 -> v20) and the file/column names. First matching pattern wins.
"""
import re

M = [
    (r'351_stage10/summary_title/B_spec_target_vs_control_within_bin', 'Stage 10 标题特异信号（真标题 − 5 个假标题平均，log10(1/名次)，名字 token 平均再论文平均）的引用档内 target − control；≥30 篇的 10 个档，权重 n_t·n_c/(n_t+n_c)；论文 bootstrap B=2000'),
    (r'351_stage10/summary_title/A_group', 'Stage 10 各组（target/control/guard）各层标题特异信号均值，论文 bootstrap 95% CI'),
    (r'351_stage10/summary_title/negative_control', 'Stage 10 标点 token 上的标题特异信号（负对照），按 token 角色'),
    (r'351_stage10/summary_title/C_graded', 'Stage 10 输出信号对多选对数 0–4 的分级（Spearman）'),
    (r'351_stage10/summary_title/E_citation', 'Stage 10 组内标题特异信号随引用档变化'),
    (r'351_stage10/summary_title/', 'Stage 10 标题特异信号汇总（真 − 5 假平均）'),
    (r'351_stage10/summary/B_target_vs_control_within_bin', 'Stage 10 真标题 log10(1/名次) 的引用档内 target − control（非标题特异），论文 bootstrap B=2000'),
    (r'351_stage10/summary/', 'Stage 10 真标题读出汇总（log10(1/名次)，名字 token 平均再论文平均）'),
    (r'351_stage10/summary_extra/X1', 'Stage 10 补充 X1：名字格式/首 token 角色（首字母 vs 完整名）条件分析'),
    (r'351_stage10/summary_extra/X2', 'Stage 10 补充 X2：标题特异信号与 log10(引用+1) 的 Spearman，bootstrap CI'),
    (r'351_stage10/summary_extra/X3', 'Stage 10 补充 X3：各读出（logit/public/self100/fitA）均值、前 10 命中率与两两差'),
    (r'351_stage10/summary_r0r1', 'Stage 10 R0/R1 分层（A=target R0, B=control R0, C=target R1, D=control R1），档内差，论文 bootstrap'),
    (r'351_stage10/summary_r0', 'Stage 10 只用 R0 的敏感性分析（档内 target − control），论文 bootstrap'),
    (r'351_stage10/reports/parity', 'Stage 10 fast path 与逐前缀参考的 parity（max |Δlogit|、容差修订记录）'),
    (r'351_stage10/reports/crosscheck_stage6', 'Stage 10 与 Stage 6 的逐 token 交叉核对'),
    (r'351_stage10/reports/.*\.md', 'Stage 10 分析脚本写出的 md 报告（二手，数字来自同目录 summary*/）'),
    (r'351_stage10/cohort', 'Stage 10 冻结队列表（论文/作者上下文/名字 token），计数为本工具直接数行'),
    (r'351_stage10/config', 'Stage 10 冻结配置（protocol/manifest/analysis_plan）'),
    (r'361_stage11/summary.*/E1', 'Stage 11 E1 替换：真标题运行标题之后全部位置的 block 输出换进 false_0 运行；R = mean(替换 − 假) ÷ mean(真 − 假)；论文 bootstrap'),
    (r'361_stage11/summary.*/E2', 'Stage 11 E2 阻断：从第 l 层起禁止标题之后位置注意标题；损失 = mean(基线 − 阻断) ÷ mean(真 − 假)'),
    (r'361_stage11/summary.*/E3', 'Stage 11 E3：全部作者放进一条链 "Authors: A1, A2, …" 的读出'),
    (r'361_stage11/summary.*/E4', 'Stage 11 E4 probe：标题最后 token 第 l 层残差 → ridge → ":" 处 L63 状态；真标题 − false_0'),
    (r'361_stage11/', 'Stage 11 因果/上下文后续实验输出'),
    (r'371_stage12/summary.*/P1', 'Stage 12 P1 单位置替换（真 → false_0），同 E1 的恢复比例 R'),
    (r'371_stage12/summary.*/P2', 'Stage 12 P2 只替换单层 attention（o_proj 后）或 MLP（down_proj 后）输出，同一 R'),
    (r'371_stage12/summary_cpu/A_prior', 'Stage 12 CPU 名字先验拆解：真标题差 = 先验 + 主题 + 论文特有；引用档内 target − control'),
    (r'371_stage12/summary.*/N[12]', 'Stage 12 N1/N2 实验汇总'),
    (r'371_stage12/summary.*/F[12]', 'Stage 12 F1/F2（author-lens 拟合）汇总'),
    (r'371_stage12/', 'Stage 12 输出'),
    (r'381_stage13/.*e4b|381_stage13/summary_cpu_trainstd', 'Stage 13 E4b 复核：团队分折 + 剔除标题复用 + 训练折标准化的 probe'),
    (r'381_stage13/.*x2', 'Stage 13 X2：只替换子空间分量 h_B + P_S(h_A − h_B)，R 同 X1；调参集选层、测试集确认'),
    (r'381_stage13/.*x3', 'Stage 13 X3：身份信号检验（文本基线 + target/control），团队聚类 CI'),
    (r'381_stage13/.*x4', 'Stage 13 X4：第一作者/年份/领域在各层的可读性，团队聚类 CI'),
    (r'381_stage13/.*x5', 'Stage 13 X5：层顺序与 top-1 检索'),
    (r'381_stage13/.*x6', 'Stage 13 X6：用 false_1..4 重做 E1'),
    (r'381_stage13/.*x7', 'Stage 13 X7 对照'),
    (r'381_stage13/.*x1', 'Stage 13 X1：任务无关性检验'),
    (r'381_stage13/.*m3', 'Stage 13 M3：与 L4 文本水平比较'),
    (r'381_stage13/.*(m1|m2)', 'Stage 13 M1/M2（团队聚类 CI）'),
    (r'381_stage13/.*b1_xall', 'Stage 13 补充 10 第 1 项：X1–X4 给全部作者打分（全部名字 token），按作者排位分层，团队聚类 95% CI'),
    (r'381_stage13/.*alltok', 'Stage 13 全部 token 版本复算'),
    (r'381_stage13/.*c13', 'Stage 13 C1–C5 补充检查'),
    (r'381_stage13/.*cluster_ci', 'Stage 13 团队聚类 bootstrap CI 复算'),
    (r'381_stage13/', 'Stage 13 输出'),
    (r'391_groups/primary', '分组对比（A/B/C/U0）预注册主对比：final L63 标题特异，档内差，团队 bootstrap 2,000，Holm 校正'),
    (r'391_groups/.*e1_num_den', '分组对比：E1 恢复比例的分子/分母拆分（未写出作者）'),
    (r'391_groups/.*p1_p2_num_den', '分组对比：P1/P2 分子/分母 B/A 比'),
    (r'391_groups/', '分组对比（R0/R1 × target/control，未写出作者）输出'),
    (r'351_stage8', 'Stage 8（200 篇新论文，J-Lens L56 主终点、RQ1/RQ2、Holm、LOPO）'),
    (r'351_stage7_4', 'Stage 7.4 J-Lens − Vanilla 积分增量 bootstrap'),
    (r'351_stage7_3', 'Stage 7.3 Pilot50 真标题 − 20 个错误标题（含 2026-10-30 区间重算）'),
    (r'351_stage7_2', 'Stage 7.2 候选打分'),
    (r'351_stage7_1', 'Stage 7.1 JMRR 7 层积分 A − B（20 对）'),
    (r'351_stage6', 'Stage 6 逐 token 打分'),
    (r'351_stage5', 'Stage 5 Pilot50 交叉设计'),
    (r'351_stage4|351_all', 'Stage 4 Benchmark20 / 早期全量日志与审计'),
    (r'351_stage9', 'Stage 9 lens 拟合（Fit A/B）'),
    (r'labels_20261015', '标注包（组长提供）：group_tight 等标签，计数为本工具直接数行'),
    (r'351_self100', 'self100 lens 验证/split-half'),
    (r'351_provenance_audit|audit_', '出处审计'),
]
CM = [(re.compile(p, re.I), d) for p, d in M]


def method_for(rel):
    for p, d in CM:
        if p.search(rel):
            return d
    return '结果文件数值（脚本输出，未重算）'
