# ARCHIVE NOTES — 归档、审计与复现维护

## 1. 归档根目录：从哪里找文件

所有路径从解压后的 `jlens_archive_stage1_8/` 算起。

| 路径 | 用途 |
|---|---|
| `README_FIRST.md`、`ARCHIVE_NOTES.md` | 学习入口与本审计说明；放到归档根目录 |
| `docs/assets/` | README引用的两张PNG；须与README一起放置 |
| `home_project/` | 已从home迁移的早期完整工程；保留src/config/data/tests/tools布局 |
| `code/scratch_scripts/` | 当前3.5.1独立Runner、验证代码、协议和说明 |
| `experiment_files/` | 保留原 `/scratch/$USER/jlens/` 相对路径的实验文件 |
| `manifests/ARCHIVE_SCOPE.txt` | 包含和排除范围 |
| `manifests/file_structure_audit/home_script_manifest.csv` | 25个home脚本/说明的源路径、目标路径、大小、SHA与复制状态 |
| `manifests/file_structure_audit/script_path_evidence.txt` | 源码中输入/输出路径证据 |
| `manifests/jlens_historical_root_files.txt` | 收集的历史根目录文件列表 |
| `manifests/SHA256SUMS.txt` | 添加本README前生成的归档文件校验清单 |
| `manifests/verified_file_map.csv` | 早期被中断复制留下的部分清单，不是最终完整清单 |
| `manifests/final_missing_files.csv` | 路径/大小检查中50个漏项均属排除的运行中7.1B；不是Hash验证报告 |

### 当前源码 → 对应实验输出

源码默认在 `code/scratch_scripts/`，输出默认在 `experiment_files/`。

| 模块 | 源码文件 | 输出位置 |
|---|---|---|
| Cohort | `351_prepare_all.py` | `351_all/`；输入标签见 `labels_20261015/` |
| Public验证 | `351_public_jlens_smoke.py`、`351_public_lens_fidelity.py`、`351_paper_prompt_fidelity_offload.py`、`351_validate_public_lens*.py` | `351_all/` 中对应验证JSONL和Log |
| Author specificity | `351_author_specificity.py` | `351_all/351_author_specificity.jsonl` |
| Self100 validation | `351_self_jlens_validation.py` | `351_self100_validation/` |
| Gold/False validation | `351_self_gold_false.py` | `351_self100_gold_false/` |
| 历史Split-half | `351_self_jlens_split_half.py`、`351_split_readout_compare.py` | `351_self100_split_half/` |
| Provenance | `351_jlens_provenance_audit.py` | `351_provenance_audit/` |
| Stage4 | `351_stage4_readout.py`、`351_stage4_audit.py` | `351_all/351_stage4_artifacts/`；同级有readout JSONL/Log |
| Stage5 | `351_stage5.py` | `351_stage5_crossed_v2/` |
| Stage6 | `351_stage6.py` | `351_stage6/` |
| Stage7.1 | **`351_stage7.py`** | `351_stage7_1/` |
| Stage7.2 | `351_stage7_2.py`、`351_stage7_2_score.py` | `351_stage7_2/` |
| Stage7.3 | `351_stage7_3.py`、`351_stage7_3_score.py` | `351_stage7_3/` |
| Stage7.4 | `351_stage7_4.py` | `351_stage7_4/` |
| Stage8A | `351_stage8.py`、`351_stage8_README.md` | `351_stage8/cohort/`、`matching/`、`config/` |
| Stage8B | `351_stage8B.py` | `351_stage8/controls/` |
| Stage8C | `351_stage8C.py` | `351_stage8/raw/stage8C_context_scores.jsonl` |
| Stage8D | `351_stage8D.py` | `351_stage8/stage8D/` |

这张表表示已找到的源码与结果归属，不保证当前源码逐字等于历史运行时版本；执行身份需要各run的日志、Config与Hash支持。

### 每个Stage怎样读

- `config/`：冻结协议、模型、层、Seed、运行拓扑与Manifest。先读。
- `cohort/`、`matching/`：目标论文与A/B pair IDs。
- `controls/`、`candidates/`、`titles/`：Gold/False与替换标题来源及Token IDs。
- `raw/`：评分记录，保留不改；需要重分析时另建输出目录。
- `summary/`：由Raw计算的论文、配对、层、组和引用分层统计。
- `figures/`：PNG/PDF；图必须追溯到对应CSV与脚本。
- `reports/`、`audit/`：结果解释、完整性检查、局限。
- Log可能在Stage目录内，也可能保留在 `experiment_files/` 根目录；按原文件名检索。

Stage5包含cohort/controls/matching；Stage6包含逐作者Token表；Stage7.2有candidates；Stage7.3有titles。不要为了形式整齐而重命名这些原目录。


## 2. 早期工程：保留背景，不混用编号

`home_project/` 内 `01–08` 是早期脚本顺序；不能当作当前Stage4–8。

| 早期代码（home_project下） | 对应材料（experiment_files下） |
|---|---|
| `01_prepare_recognition.py`、`02_run_qwen3_recognition.py` | `recognition_primary_random_field_1000*`；正式结果772/1000，Parse failed 0 |
| `03_run_title_hidden.py` | `title_hidden_random_field_772_results.jsonl`；最终完成统计需从输出核实 |
| `04_build_matched_cohorts.py`、`04_optimize_matching*.py`、`04_freeze_consistent_splits.py` | `matched_*`历史匹配和Split版本 |
| `05_prepare_jlens_corpus.py`、`05_fit_jlens_prelim_100.py`、Smoke脚本 | `fitting_corpus/`、`qwen32b_jlens_prelim_100*`、Smoke产物 |
| `06_jlens_quick_demo.py`、`07_jlens_authorship_pilot.py`、`08_jlens_authorship_29pairs.py` | `jlens_quick_demo*`、`jlens_authorship_*` |
| `run_group_jlens.py`、`run_group_jlens_surname.py`等 | `group_jlens_*.csv`、`mini_step1_pilot30.csv` |

Invalid、rightpad backup、Smoke、不同匹配版本保留为历史证据，不得与正式输出拼接分析。早期1000篇Recognition结果不替代当前9108标签来源。


## 3. Lens文件从哪里找

| 相对experiment_files的路径 | 内容 |
|---|---|
| `fitting_corpus/wikitext103_qwen32b_1000.jsonl`、`manifest.json` | 历史冻结拟合文本与来源 |
| `fitting_corpus/source/` | WikiText原始Parquet |
| `qwen32b_jlens_prelim_100.pt`、同前缀Checkpoint/Config/Log | 历史Self100拟合产物 |
| `public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/` | Public Lens、Convergence CSV、Config |
| `351_self100_split_half/fits/` | 历史A50/B50 Checkpoint与Lens |
| `351_self100_split_half/readout_comparison/` | 历史两套Lens功能比较 |
| `qwen32b_fit_test/`、`pilot1_qwen3_32b/` | 早期Smoke与Embedding材料 |

历史拟合A/B、行为组A/B、新Stage9 Fit A/B是三套不同标签。不要混称。不能仅凭文件名判断Public80、Public557或Self100版本；核对产物元数据和Hash。


## 4. 本包还未纳入的工作

- **Stage7.1B：** `351_stage7_1B_terminal/` 归档时正在运行，未纳入；不要把它与已完成的7.1 CPU分解合并。
- **Stage9：** 新A100/B100与Holdout100工作另行归档，不在本包；历史Self100 Split-half仍在本包。
- **Stage8E：** 由实验负责人Zhiqi Zhang确认未执行，后续补做（计划日期待补）。旧草稿若出现8E Token去重或连续Title-length的数值，不能据此标为已完成/可复现；需未来实际脚本、输入和输出支持。
- 缓存、部分重复压缩包不属于本次文件覆盖检查范围；本包不是整个HPC账户的镜像。
