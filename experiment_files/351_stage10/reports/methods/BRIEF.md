# 《方法手册》共同规范（给每个起草者）

背景：项目 jlens，研究 Qwen3-32B 在哪一层"记住"论文作者。用户要在导师面前做方法答辩，导师会逐个实验细问做法。你负责手册的一部分，写成一个 HTML 片段文件。

## 硬规则
1. **只写查得到的事实。** 每个数字、参数、样本量、阈值都要给出出处：脚本路径 + 行号或函数名、结果文件路径（含列名/行）、作业号、git commit（仓库 `/scratch/zhang.zhiqi2/jlens-authorship-recall_update`，用 `git log --oneline -- <path>`）。查不到就写 `<span class="unk">未知/需确认：向 X 确认（原因）</span>`，X 是"组长"（标注包作者）或"用户"或"Stage N 原作者（laptop 会话）"。绝不凭记忆、推测或"通常做法"补。
2. **写实际做了什么。** 计划过没做、做了作废、被复核取代的，用 `<span class="st st-void">作废</span>` / `<span class="st st-plan">计划未做</span>` 标出并说明原因和出处。
3. 中文为主，术语保留英文（patching、ridge、Jaccard、bootstrap、knockout、logit lens 等）。宁细勿略。
4. **只读**：不要修改任何代码、结果文件、PROGRESS/STATUS；不要提交作业；不要删除任何东西。唯一允许写的是你自己的输出文件。
5. Python：`~/conda-envs/jlens/bin/python`；读 parquet/npz/csv 可以，别加载模型、别跑重计算（你在 2 CPU、8GB 的节点上）。

## 去哪找
- 代码：`~/jlens_work/<NN_stage>/`（索引 `~/jlens_work/README.md`、`~/jlens_work/STAGES.md`，各文件夹有 README）。
- 结果：`/scratch/zhang.zhiqi2/jlens/351_*`（Stage 1–10）、`361_stage11/`、`371_stage12/`、`381_stage13/`；Stage 1–8 归档 `/scratch/zhang.zhiqi2/jlens_archive_stage1_8/`。
- 状态与历史：`/scratch/zhang.zhiqi2/jlens/STATUS.md`、`~/jlens_work/PROGRESS.md`（很长，可 grep）、`~/jlens_work/HANDOFF.md`。
- 已发布报告的 HTML 副本（可当线索，但数字要回到结果文件核对）：`/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/stage1_11_report.html`。
- 预注册：`/scratch/zhang.zhiqi2/jlens/381_stage13/config/prereg*.json` 和 `.sha256`。
- git 仓库（GitHub 镜像，含 code/、experiment_files/、docs/）：`/scratch/zhang.zhiqi2/jlens-authorship-recall_update`。

## 输出格式
- 写一个 HTML 片段（不要 `<html>/<head>/<style>`），文件名由任务指定。
- 每个大节 `<section id="…">`，标题 `<h2>`，子节 `<h3 id="…">`；id 用英文小写短横线，加你的前缀避免冲突（任务里给）。
- 表格用 `<table class="t">`，表头 `<th>`；长文本放表格也行，**不要截断**。
- 出处用 `<span class="src">脚本路径:行号 · 结果文件 · 作业号 · commit</span>`，紧跟在数字或段落后面。
- 代码/提示词原文用 `<pre class="code">…</pre>`（注意 HTML 转义 &lt; &gt; &amp;）。
- 状态标签：`<span class="st st-done">已完成</span>`、`<span class="st st-rechecked">复核过</span>`、`<span class="st st-review">待复核</span>`、`<span class="st st-void">作废</span>`、`<span class="st st-plan">计划未做</span>`。
- 每个实验一节，统一 9 个小标题（用 `<h4>`）：1 问题与作用 · 2 材料 · 3 工具 · 4 步骤 · 5 公式 · 6 对照 · 7 结果 · 8 局限与质疑 · 9 状态。
- 写完后在文件末尾另起 `<!-- UNKNOWN-LIST` … `-->` 注释，逐行列出你写了"未知/需确认"的每一处（节 id + 问题 + 向谁确认）。再起 `<!-- CHECK-NUMBERS` … `-->` 列出 5 个你写的关键数字及其精确出处（文件 + 行/列），供总编核对。

## 结束时
回复里只给：输出文件路径、写了几节、"未知/需确认"的条数和最要紧的 3 条、以及你认为最可能被导师追问而你没能查实的点。
