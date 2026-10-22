# ARCHIVE NOTES — Archive, Audit, and Reproduction Maintenance

[English](ARCHIVE_NOTES.md) | [简体中文](ARCHIVE_NOTES.zh-CN.md)

## 1. Archive Root: Where to Find Files

All paths are relative to the unzipped `jlens_archive_stage1_8/`.

| Path | Purpose |
|---|---|
| `README.md`, `ARCHIVE_NOTES.md` | Learning entry point and this audit note; place in the archive root |
| `docs/assets/` | The two PNGs referenced by the README; must be placed together with the README |
| `home_project/` | Early full project migrated from home; keeps the src/config/data/tests/tools layout |
| `code/scratch_scripts/` | Standalone Runners, validation code, protocols, and notes for the current 3.5.1 |
| `experiment_files/` | Experiment files that keep the original `/scratch/$USER/jlens/` relative paths |
| `manifests/ARCHIVE_SCOPE.txt` | Inclusion and exclusion scope |
| `manifests/file_structure_audit/home_script_manifest.csv` | Source path, target path, size, SHA, and copy status of the 25 home scripts/notes |
| `manifests/file_structure_audit/script_path_evidence.txt` | Evidence of input/output paths found in the source code |
| `manifests/jlens_historical_root_files.txt` | List of collected historical root-directory files |
| `manifests/SHA256SUMS.txt` | Checksum list of archive files generated before this README was added |
| `manifests/verified_file_map.csv` | Partial list left by an earlier interrupted copy; not the final complete list |
| `manifests/final_missing_files.csv` | The 50 missing items from the path/size check all belong to the excluded, still-running 7.1B; not a hash-verification report |

### Current Source Code → Corresponding Experiment Outputs

Source code is by default in `code/scratch_scripts/`; outputs are by default in `experiment_files/`.

| Module | Source files | Output location |
|---|---|---|
| Cohort | `351_prepare_all.py` | `351_all/`; input labels are in `labels_20261015/` |
| Public validation | `351_public_jlens_smoke.py`, `351_public_lens_fidelity.py`, `351_paper_prompt_fidelity_offload.py`, `351_validate_public_lens*.py` | Corresponding validation JSONL and Logs in `351_all/` |
| Author specificity | `351_author_specificity.py` | `351_all/351_author_specificity.jsonl` |
| Self100 validation | `351_self_jlens_validation.py` | `351_self100_validation/` |
| Gold/False validation | `351_self_gold_false.py` | `351_self100_gold_false/` |
| Historical Split-half | `351_self_jlens_split_half.py`, `351_split_readout_compare.py` | `351_self100_split_half/` |
| Provenance | `351_jlens_provenance_audit.py` | `351_provenance_audit/` |
| Stage 4 | `351_stage4_readout.py`, `351_stage4_audit.py` | `351_all/351_stage4_artifacts/`; the readout JSONL/Log is at the same level |
| Stage 5 | `351_stage5.py` | `351_stage5_crossed_v2/` |
| Stage 6 | `351_stage6.py` | `351_stage6/` |
| Stage 7.1 | **`351_stage7.py`** | `351_stage7_1/` |
| Stage 7.2 | `351_stage7_2.py`, `351_stage7_2_score.py` | `351_stage7_2/` |
| Stage 7.3 | `351_stage7_3.py`, `351_stage7_3_score.py` | `351_stage7_3/` |
| Stage 7.4 | `351_stage7_4.py` | `351_stage7_4/` |
| Stage 8A | `351_stage8.py`, `351_stage8_README.md` | `351_stage8/cohort/`, `matching/`, `config/` |
| Stage 8B | `351_stage8B.py` | `351_stage8/controls/` |
| Stage 8C | `351_stage8C.py` | `351_stage8/raw/stage8C_context_scores.jsonl` |
| Stage 8D | `351_stage8D.py` | `351_stage8/stage8D/` |

This table records which source files and results belong together as found; it does not guarantee that the current source is character-for-character the version used at run time. Execution identity must be supported by each run's logs, Config, and Hash.

### How to Read Each Stage

- `config/`: Frozen protocol, model, layers, Seed, run topology, and Manifest. Read first.
- `cohort/`, `matching/`: Target papers and A/B pair IDs.
- `controls/`, `candidates/`, `titles/`: Sources of Gold/False and replacement titles, and their Token IDs.
- `raw/`: Scoring records; keep unchanged. For reanalysis, create a separate output directory.
- `summary/`: Paper-, pair-, layer-, group-, and citation-stratum statistics computed from Raw.
- `figures/`: PNG/PDF; every figure must be traceable to its CSV and script.
- `reports/`, `audit/`: Result interpretation, integrity checks, and limitations.
- Logs may be inside the Stage directory or kept in the `experiment_files/` root; search by the original file name.

Stage 5 contains cohort/controls/matching; Stage 6 contains the per-author token tables; Stage 7.2 has candidates; Stage 7.3 has titles. Do not rename these original directories just to make them uniform.


## 2. Early Project: Kept for Background, Numbering Not to Be Mixed

The `01–08` in `home_project/` is the early script order; it must not be taken as the current Stage 4–8.

| Early code (under home_project) | Corresponding materials (under experiment_files) |
|---|---|
| `01_prepare_recognition.py`, `02_run_qwen3_recognition.py` | `recognition_primary_random_field_1000*`; official result 772/1000, Parse failed 0 |
| `03_run_title_hidden.py` | `title_hidden_random_field_772_results.jsonl`; the final completion statistics must be verified from the output |
| `04_build_matched_cohorts.py`, `04_optimize_matching*.py`, `04_freeze_consistent_splits.py` | `matched_*` historical matching and Split versions |
| `05_prepare_jlens_corpus.py`, `05_fit_jlens_prelim_100.py`, Smoke scripts | `fitting_corpus/`, `qwen32b_jlens_prelim_100*`, Smoke outputs |
| `06_jlens_quick_demo.py`, `07_jlens_authorship_pilot.py`, `08_jlens_authorship_29pairs.py` | `jlens_quick_demo*`, `jlens_authorship_*` |
| `run_group_jlens.py`, `run_group_jlens_surname.py`, etc. | `group_jlens_*.csv`, `mini_step1_pilot30.csv` |

Invalid, rightpad backup, Smoke, and the different matching versions are kept as historical evidence and must not be spliced into analyses of the official outputs. The early 1,000-paper Recognition result does not replace the current 9,108-label source.


## 3. Where to Find the Lens Files

| Path relative to experiment_files | Content |
|---|---|
| `fitting_corpus/wikitext103_qwen32b_1000.jsonl`, `manifest.json` | Historical frozen fitting text and its source |
| `fitting_corpus/source/` | Raw WikiText Parquet |
| `qwen32b_jlens_prelim_100.pt`, same-prefix Checkpoint/Config/Log | Historical Self100 fitting artifacts |
| `public_neuronpedia/qwen3-32b/jlens/Salesforce-wikitext/` | Public Lens, Convergence CSV, Config |
| `351_self100_split_half/fits/` | Historical A50/B50 Checkpoints and Lenses |
| `351_self100_split_half/readout_comparison/` | Functional comparison of the two historical Lenses |
| `qwen32b_fit_test/`, `pilot1_qwen3_32b/` | Early Smoke and Embedding materials |

Historical fitting A/B, behavior-group A/B, and the new Stage 9 Fit A/B are three different labelings; do not conflate them. Do not identify a Public80, Public557, or Self100 version by file name alone; check the artifact metadata and Hash.


## 4. Work Not Yet Included in This Package

- **Stage 7.1B:** `351_stage7_1B_terminal/` was still running at archive time and is not included; do not merge it with the completed 7.1 CPU decomposition.
- **Stage 9:** The new A100/B100 and Holdout100 work is archived separately and is not in this package; the historical Self100 Split-half is still in this package.
- **Stage 8E:** Confirmed by the experiment lead, Zhiqi Zhang, as not executed; to be done later (planned date to be filled in). If old drafts contain 8E Token-deduplication or continuous Title-length numbers, they must not be labeled completed/reproducible; they need an actual future script, inputs, and outputs.
- Caches and some duplicate archives are outside the scope of this file-coverage check; this package is not a mirror of the whole HPC account.
