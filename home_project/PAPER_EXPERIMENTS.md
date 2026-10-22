# Dreaming Up Authors: experiments and the code behind them

This file maps each experiment in the camera-ready paper to the code that runs it.
It follows the paper's order. Each main-text section is paired with its appendix
counterpart. Links point to line ranges in this repository.

**Numbering note.** Docstrings, CLI help, and `README.md` still use the
pre-camera-ready appendix numbers. The headings here use the camera-ready ones.

| Camera-ready | Code / docstrings |
|---|---|
| A4.3.4 HR decomposition | A6.3 |
| A4.4 evaluation-method comparison | A6.5–A6.6 |
| A5.x additional analyses | A6.x |
| A6.x multiple-choice recognition | A7.x |
| A7 mechanistic evidence, Tables A37–A44 | A8, Tables A18–A25 |

**What needs what.**
- Credentials or external services: corpus filtering, sampling, proxy APIs, response collection, MC recognition.
- A GPU: probing stage 1, and steering stages 14–24.
- Nothing extra: everything else runs from `data/release/`.

---

## 1. The paper in one paragraph

The paper asks whether LLMs hallucinate more about facts that appear less often in their training data. It asks three closed models (GPT-4o, DeepSeek-R1, Claude Sonnet 4.5) for the authors of 9,108 papers. Citation count serves as the prevalence proxy. Hallucination rate (HR2) falls steadily as citations rise, in all 24 field–model pairs (§5). GPT-4o recognises the right author list in a multiple-choice test even when it can't recall it, so the failures are about retrieval (§6). Hidden states in two open models (Qwen3-32B, Mistral-Small-3.2-24B) encode prevalence before generation starts. That internal signal mediates much of the citation–hallucination link, and steering against it causes hallucinations (§7). Controls for author position, author count, title length, prompt wording, and name ethnicity leave the main result intact (§8).

---

## 2. Dataset (§2, A2)

### §2.1 / A2.1 — Five-stage quality filter
The OAG pool of 10M papers is filtered down to 1,921,209 papers. Removal rates at each stage, relative to the previous stage's survivors:

| Stage | Removed |
|---|---|
| Document type | 56.9% |
| Author count (1–20) | 0.3% |
| Language (English) | 47.9% |
| Name patterns | 0.8% |
| Semantic Scholar title/author match | 13.5% |

- **Thresholds** (journal/conference, 1–20 authors, FastText conf ≥ 0.8) → [`filters.py:L20-L33`](src/dua/data/filters.py#L20-L33)
- **Document type** → [`filters.py:L115-L125`](src/dua/data/filters.py#L115-L125) (`filter_doc_type`)
- **Author count** → [`filters.py:L128-L138`](src/dua/data/filters.py#L128-L138) (`filter_author_count`)
- **Language (FastText)** → [`filters.py:L141-L162`](src/dua/data/filters.py#L141-L162) (`filter_language`)
- **Name-pattern classifier** → [`filters.py:L78-L105`](src/dua/data/filters.py#L78-L105) (`classify_name`)
- **Name-pattern filter** → [`filters.py:L165-L183`](src/dua/data/filters.py#L165-L183) (`filter_author_name_patterns`)
- **Title and first-author match against Semantic Scholar** → [`filters.py:L186-L210`](src/dua/data/filters.py#L186-L210) (`filter_title_match`)
- **Chain the stages and count removals** → [`filters.py:L248-L303`](src/dua/data/filters.py#L248-L303) (`Funnel`, `apply_filters`)
- **Stream the NDJSON corpus** → [`filters.py:L306-L326`](src/dua/data/filters.py#L306-L326) (`filter_corpus`)
- **Outputs:** the filtered corpus and funnel counts (Figure 2). Run with `make corpus-filter`. It needs `DUA_OAG_POOL`. The 7.3 GB pool itself is not in the repo.

### §2.2 / A2.2 — Dataset characteristics
Corpus statistics for field, year, author count, and citation distribution.
- **Per-record accumulation** → [`distributions.py:L43-L139`](src/dua/data/distributions.py#L43-L139) (`CorpusStats`)
- **Cumulative tables** → [`distributions.py:L153-L165`](src/dua/data/distributions.py#L153-L165) (`_cumulative_table`)
- **Driver** → [`distributions.py:L168-L220`](src/dua/data/distributions.py#L168-L220) (`run`)
- **Outputs:** the §2.2 and A2.2 tables. Run with `make distributions`. It needs `DUA_CORPUS`.

---

## 3. Citation count as the prevalence proxy (§3, A3)

### §3.1 / A3.1 — Google search hits
The query is the quoted title plus the author names. Mean hits rise with the citation bin. Papers above the 80th percentile of hits are dropped, because short titles match unrelated pages.
- **Build the query** → [`google_hits.py:L30-L38`](src/dua/proxy/google_hits.py#L30-L38) (`build_query`, `query_length`)
- **Fetch hits, with a cache** → [`google_hits.py:L70-L140`](src/dua/proxy/google_hits.py#L70-L140) (`GoogleHitsClient`)
- **Parse the hit count** → [`google_hits.py:L44-L67`](src/dua/proxy/google_hits.py#L44-L67) (`parse_hit_count`)
- **Collect** → [`google_hits.py:L143-L163`](src/dua/proxy/google_hits.py#L143-L163) (`collect`)
- **Subsample** → [`subsample.py:L23-L49`](src/dua/proxy/subsample.py#L23-L49) (`draw`)
- **Drop outliers above the 80th percentile** → [`analyze.py:L20-L42`](src/dua/proxy/analyze.py#L20-L42) (`filter_outliers`)
- **Per-bin tables** → [`analyze.py:L45-L86`](src/dua/proxy/analyze.py#L45-L86) (`summarize_by_bin`, `table_google_hits`, `table_query_length`)
- **Outputs:** Figure 1 (left) and the Google-hits tables. Run with `dua proxy`. It needs a paid API or the cache.

### §3.2 / A3.2 — Infini-gram corpus occurrence
Counts of title plus first author across 6,048 papers, in OLMo2 (6.1T tokens) and RedPajama (1.4T tokens). Two capitalisation variants are queried. Counts are near zero in the low bins and rise above 128 citations.
- **Query variants** → [`infinigram.py:L28-L42`](src/dua/proxy/infinigram.py#L28-L42) (`capitalize_variant`, `camel_variant`, `build_query`)
- **API client, with a cache** → [`infinigram.py:L45-L103`](src/dua/proxy/infinigram.py#L45-L103) (`InfiniGramClient`)
- **Collect** → [`infinigram.py:L106-L126`](src/dua/proxy/infinigram.py#L106-L126) (`collect`)
- **Tables and Figure 1** → [`analyze.py:L89-L151`](src/dua/proxy/analyze.py#L89-L151) (`table_infinigram`, `figure_proxy_means`, `run_all`)

### §3.3 — Why citation count
This section is an argument, not an experiment. Google hits and Infini-gram counts are noisy and sensitive to how the query is formatted. Citation count is used instead.
- **Citation count from Semantic Scholar** → [`stratified.py:L24-L36`](src/dua/sampling/stratified.py#L24-L36) (`citation_count`)
- **Citation bins** → [`bins.py:L12-L31`](src/dua/bins.py#L12-L31) (`bin_label`, `bin_index`). The bin edges are `citation_bins` in `config/config.yaml`.

---

## 4. Experiment setup (§4, A4)

### §4.1 / A4.1 — Stratified sampling
The design is 8 fields × 13 exponential citation bins, with up to 100 papers per stratum. That gives 9,108 papers against a maximum of 10,400. The shortfall comes from sparse high-citation strata. The code is a seeded redraw. The original draw used `RANDOM_SEED=None`, so the shipped sample can't be reproduced exactly.
- **Field assignment** → [`stratified.py:L39-L79`](src/dua/sampling/stratified.py#L39-L79) (`primary_field`, `paper_field`)
- **Index strata by file offset** → [`stratified.py:L82-L90`](src/dua/sampling/stratified.py#L82-L90) (`index_strata`)
- **Seeded draw per stratum** → [`stratified.py:L93-L129`](src/dua/sampling/stratified.py#L93-L129) (`select_offsets`)
- **Emit release rows** → [`stratified.py:L132-L186`](src/dua/sampling/stratified.py#L132-L186) (`collect_selected`, `to_release_row`, `draw`)
- **Compare the redraw with the shipped sample** → [`stratified.py:L189-L217`](src/dua/sampling/stratified.py#L189-L217) (`verify_against`)
- **A4.1.2 stratum stability and shortfall** → [`stratum_stability.py:L23-L82`](src/dua/analysis/stratum_stability.py#L23-L82) (`stratum_table`, `shortfall_table`)
- **Outputs:** Table 2 and the A4.1 tables. Run with `make resample`.

### §4.2 / A4.2 — Prompt design
A few-shot prompt asks for the full author list, given the title and year.
- **Templates:**
  - [`authorship_fewshot_paper.txt`](config/prompts/authorship_fewshot_paper.txt) (GPT-4o)
  - [`authorship_fewshot_openrouter.txt`](config/prompts/authorship_fewshot_openrouter.txt) (OpenRouter)
  - [`config/prompts/README.md`](config/prompts/README.md) notes where the two differ.
- **Build the question** → [`authorship.py:L24-L25`](src/dua/collect/authorship.py#L24-L25) (`build_question`)
- **A4.2.1 prompt validation:** _not in repo._

### §4.3 — LLMs tested
The models are GPT-4o, DeepSeek-R1, and Claude Sonnet 4.5, all at temperature 0.
- **Model IDs and decoding parameters** → [`config/models.yaml`](config/models.yaml) (`behavioral:`). The model aliases float over time, so responses won't reproduce token for token.
- **API client with a response cache** → [`client.py:L68-L202`](src/dua/collect/client.py#L68-L202) (`ResponseCache`, `ChatClient.call`)
- **Resumable collection loop** → [`authorship.py:L28-L104`](src/dua/collect/authorship.py#L28-L104) (`collect`)
- **Outputs:** `data/release/responses/*.csv.gz`. Run with `make collect`. It needs an API key.

### §4.4 / A4.3 — Hallucination-rate definitions
Each answer gives M (matched), H (hallucinated), and U (unretrieved). There are three rates:
- **HR1:** max-normalised.
- **HR2:** Jaccard, (H+U)/(M+H+U). This is the primary rate.
- **HR3:** harmonic.

All three correlate about −0.48 with citations.
- **HR1 / HR2 / HR3** → [`metrics.py:L30-L45`](src/dua/evaluate/metrics.py#L30-L45) (`hr1`, `hr2`, `hr3`)
- **Parse (M, H, U) and add rate columns** → [`metrics.py:L79-L110`](src/dua/evaluate/metrics.py#L79-L110) (`parse_counts`, `add_rates`)
- **Mean with 95% CI (the error bars)** → [`metrics.py:L113-L131`](src/dua/evaluate/metrics.py#L113-L131) (`mean_ci`)
- **A4.3.1–A4.3.3 relationships between the metrics** → [`hr_decomposition.py:L23-L61`](src/dua/analysis/hr_decomposition.py#L23-L61) (`table_spearman_hr`, `table_pearson_hr`)

### A4.3.4 — Decomposing HR2 into fabrication (HR4) and omission (HR5)
This checks whether HR2 hides two trends that move in opposite directions. It doesn't: HR4 and HR5 stay within 0.022 of each other in every bin.
- **HR4 / HR5** → [`metrics.py:L48-L57`](src/dua/evaluate/metrics.py#L48-L57) (`hr4`, `hr5`)
- **Per-bin table** → [`hr_decomposition.py:L64-L87`](src/dua/analysis/hr_decomposition.py#L64-L87) (`table_hr4_hr5_binwise`)

### §4.5 — Evaluation pipeline (name matching)
Names are matched greedily at these levels:

| Level | Match | Counts as |
|---|---|---|
| L1 | exact | correct |
| L2 | Unicode-folded | correct |
| L3 | alpha-only | correct |
| L3.5 | surname and full first name | correct |
| L4 | surname and first initial | correct |
| L5 | surname only | hallucinated, and the true author as missed |

- **Ground-truth names** → [`ground_truth.py:L26-L99`](src/dua/evaluate/ground_truth.py#L26-L99) (`extract_author_names`, `ground_truth_list`)
- **Split the LLM's author string** → [`splitter.py:L17-L314`](src/dua/evaluate/splitter.py#L17-L314) (`NameSplitter.split`)
- **Parse a single name** → [`matcher.py:L40-L108`](src/dua/evaluate/matcher.py#L40-L108) (`_strip_particles`, `_parse_single_name`)
- **L1–L5 match decision** → [`matcher.py:L110-L178`](src/dua/evaluate/matcher.py#L110-L178) (`_get_match`)
- **Swapped and bibliographic name orders** → [`matcher.py:L180-L254`](src/dua/evaluate/matcher.py#L180-L254)
- **Greedy one-to-one matching** → [`matcher.py:L256-L360`](src/dua/evaluate/matcher.py#L256-L360) (`find_matches`)
- **L4 threshold → (M, H, U)** → [`pipeline.py:L64-L105`](src/dua/evaluate/pipeline.py#L64-L105) (`Evaluator.evaluate`). The threshold is `match_level_threshold: 4` in `config/config.yaml`.

### A4.4 — Matcher vs. LLM-as-judge
The two evaluators score the same GPT-4o answers (N = 9,107). The matcher is chosen for its stability (A4.4.4).
- **Judge prompt** → [`self_eval.txt`](config/prompts/self_eval.txt). The code that ran the judge is _not in repo_; its scores ship in the release CSVs.
- **Agreement stats and table** → [`eval_agreement.py:L25-L68`](src/dua/analysis/eval_agreement.py#L25-L68) (`agreement_stats`, `table_eval_agreement`)
- **A4.4.3 variance comparison** → [`eval_agreement.py:L71-L83`](src/dua/analysis/eval_agreement.py#L71-L83) (`table_variance_comparison`)
- **Agreement figure** → [`eval_agreement.py:L86-L103`](src/dua/analysis/eval_agreement.py#L86-L103) (`figure_eval_agreement`)

---

## 5. Hallucination rate vs. citation count (§5, A5.1)

HR2 falls steadily with citations for all three models. In the top bin it is about 0.36 for GPT-4o and DeepSeek-R1. Spearman ρ is negative and significant in all 24 field–model pairs. Chemistry and Psychology are the hardest fields. Claude has the lowest overall rate.
- **Load responses and recompute HR1–HR5** → [`loaders.py:L46-L94`](src/dua/analysis/loaders.py#L46-L94) (`_add_rates`, `load_responses`)
- **Mean HR and 95% CI per bin (Figure 3)** → [`results.py:L39-L93`](src/dua/analysis/results.py#L39-L93) (`rate_by_bin`, `figure_hr_by_citation`)
- **Spearman ρ per field × model (Table 3)** → [`results.py:L94-L130`](src/dua/analysis/results.py#L94-L130) (`spearman_by_field`, `table_spearman_all_models`)
- **HR2 distribution per field (Figure 4)** → [`results.py:L131-L164`](src/dua/analysis/results.py#L131-L164) (`figure_field_variance_radar`)
- **HR2 per bin, one line per field (Figure 5)** → [`results.py:L165-L197`](src/dua/analysis/results.py#L165-L197) (`figure_gpt4o_field_by_citation`)
- **A5.1 tables under all three HR definitions** → [`results.py:L198-L254`](src/dua/analysis/results.py#L198-L254) (`table_multi_llm_summary`, `table_detailed_gpt4o`)
- **Headline numbers** → [`results.py:L313-L331`](src/dua/analysis/results.py#L313-L331) (`headline_numbers`), collected by [`metrics_report.py:L34-L131`](src/dua/metrics_report.py#L34-L131) (`collect`)
- **Run:** `make analysis`

---

## 6. Multiple-choice recognition (§6, A6)

> **Not byte-identical to the paper.** `dua.recognition` was reimplemented from the appendix description, because no code for §6 existed in either original source tree. It meets every integrity check the appendix states, but distractor sampling is seeded differently, GPT-4o at temperature 0 is not deterministic, and the collaborator swap reads Semantic Scholar records that drift. No MC results are shipped, so a re-run should land close to the numbers below, not on them. The recall side comes from the shipped responses and is exact.

### §6 / A6.1–A6.2 — Recognition vs. recall (GPT-4o)
Each paper becomes a 4-option item: the true author list plus three same-field distractor teams of the same size. Chance-corrected accuracy is about 79% even at 0–2 citations. 93.9% of papers with HR2 > 0.5 are still recognised. The gap between recognition and recall has an inverted-U shape across citation bins.
- **Pools of author teams per field** → [`distractors.py:L70-L84`](src/dua/recognition/distractors.py#L70-L84) (`build_field_pools`)
- **Random same-field distractors** → [`distractors.py:L85-L184`](src/dua/recognition/distractors.py#L85-L184) (`DistractorBuilder.random_field`)
- **Item verification** → [`distractors.py:L232-L270`](src/dua/recognition/distractors.py#L232-L270) (`verify_items`)
- **Query the model and parse its choice** → [`run.py:L21-L99`](src/dua/recognition/run.py#L21-L99) (`parse_choice`, `build_items`, `run`)
- **Chance correction and merge with recall** → [`analyze.py:L28-L54`](src/dua/recognition/analyze.py#L28-L54) (`chance_corrected`, `merge_with_recall`)
- **Gap by bin (Figure 6)** → [`analyze.py:L55-L69`](src/dua/recognition/analyze.py#L55-L69) (`gap_by_bin`), [`L120-L166`](src/dua/recognition/analyze.py#L120-L166) (`figure_recall_recognition_gap`)
- **Residual recognition among recall failures** → [`analyze.py:L70-L119`](src/dua/recognition/analyze.py#L70-L119) (`residual_recognition`, `table_residual_knowledge`)
- **Run:** `make recognise-build`, then `make recognise`

### §6 / A6.3 — Harder distractors
Two harder versions:
- **One-author swap:** a distractor keeps k−1 of the k true authors. Accuracy barely moves (0.789 → 0.782 in the 0–2 bin).
- **Collaborator swap:** a real collaborator replaces a true author. Accuracy drops but stays well above chance.

Code:
- **One-author swap** → [`distractors.py:L186-L197`](src/dua/recognition/distractors.py#L186-L197) (`same_field_swap`)
- **Collaborator swap** → [`distractors.py:L198-L231`](src/dua/recognition/distractors.py#L198-L231) (`collaborator_swap`)
- **Semantic Scholar collaborator index** → [`collaborators.py:L25-L121`](src/dua/recognition/collaborators.py#L25-L121) (`CollaboratorIndex`)
- **Side-by-side table** → [`analyze.py:L204-L243`](src/dua/recognition/analyze.py#L204-L243) (`table_hard_distractors`)
- **Run:** `make recognise MODE=same_field_swap` or `MODE=collaborator_swap`

### A6.4 — Binary perfect recall
Recall is scored as all-or-nothing (H = U = 0), to match the binary MC score. Under this stricter score the gap grows.
- **Perfect-recall flag** → [`loaders.py:L55-L57`](src/dua/analysis/loaders.py#L55-L57)
- **Gap figure** → [`analyze.py:L167-L203`](src/dua/recognition/analyze.py#L167-L203) (`figure_perfect_recall_gap`)

---

## 7. Mechanistic evidence (§7, A7)

The open models are Qwen3-32B (peak layer 48) and Mistral-Small-3.2-24B (peak layer 22). Both run on the same 9,108 papers.

### Pipeline order

| Step | Stages | Hardware |
|---|---|---|
| Setup | [`prompts.py`](src/dua/probing/prompts.py) (`make probing-prompts`), [`rundir.py`](src/dua/probing/rundir.py) (`make probing-rundir`) | CPU |
| Extraction | 1 | GPU |
| Scoring and probes | 2 score · 3 SVD/probe · 4 citation OLS · 5 first ridge + Baron–Kenny · 6 follow-ups · 7 figures · 8 validated appendix battery · 9 R mediation · 12 P9 checks · 13 title-only baselines | CPU |
| Steering | 14 diff-of-means · 15 one norm-matched control · 16 direction cosines (CPU) · 17 graded band · 18 induce layer sweep · 19 causal tracing · 20 fix layer sweep · 22 norm-relative fix · 23 log-prob readout · 24 position/probe/5-seed controls | GPU |
| Post-hoc | `analyze_steering_paired_stats`, `analyze_steering_name_recall`, `analyze_localization_vs_editing` | CPU |
| Tables | [`tables.py`](src/dua/probing/tables.py) (`make probing-tables`) | CPU |

Every stage is a plain `python -m dua.probing.stages.<stage>` CLI, so run it directly or wrap it in your own scheduler. Stage 8's experiments each live in their own module under [`stages/prevalence/`](src/dua/probing/stages/prevalence/).

**Superseded and exploratory stages.**
- **Stage 15** is replaced by Stage 24's five-seed control, which is what Table A43 quotes.
- **Stages 17, 18, 20, and 22** probe why "fix" steering fails. None of them feeds a camera-ready table.
- **Stage 23**'s readout was invalidated by a contamination artifact. Its docstring says nothing in the camera-ready depends on it.
- **Stage 19** (causal tracing) and `analyze_localization_vs_editing` are descriptive. They are not reported in the paper.

### §7 / A7 — Hidden-state extraction (stage 1)
There is one greedy generation pass per paper. It saves the residual stream at every target layer, for six token positions. Generation and extraction are combined because P2, P3, P5, and P9 only exist during decoding.
- **Model registry and auto-detected layers** → [`stage1_generate.py:L73`](src/dua/probing/stages/stage1_generate.py#L73) (`MODEL_REGISTRY`), [`L145-L158`](src/dua/probing/stages/stage1_generate.py#L145-L158) (`detect_model_config`)
- **Prompt** → [`stage1_generate.py:L244-L252`](src/dua/probing/stages/stage1_generate.py#L244-L252) (`_user_text`, `build_prompt`)
- **Prompt-only forward pass with `output_hidden_states=True`** → [`stage1_generate.py:L739-L746`](src/dua/probing/stages/stage1_generate.py#L739-L746)
- **P1 (last prompt token) and P4 (mean over the prompt)** → [`stage1_generate.py:L435-L453`](src/dua/probing/stages/stage1_generate.py#L435-L453) (`extract_prompt_states`). `hidden_states[l+1]` is the output of block `l`.
- **Greedy `generate` with hidden states** → [`stage1_generate.py:L748-L759`](src/dua/probing/stages/stage1_generate.py#L748-L759)
- **Prefill offset (transformers 4.x vs. 5.x)** → [`stage1_generate.py:L456-L462`](src/dua/probing/stages/stage1_generate.py#L456-L462) (`_decode_offset`)
- **P2 (first generated), P3 (last generated), P5 (mean over the answer)** → [`stage1_generate.py:L465-L499`](src/dua/probing/stages/stage1_generate.py#L465-L499) (`extract_gen_states`)
- **P9 (last token of each generated name):**
  - Delimiter tokens → [`L506-L519`](src/dua/probing/stages/stage1_generate.py#L506-L519) (`build_delim_ids`)
  - Name segments → [`L522-L557`](src/dua/probing/stages/stage1_generate.py#L522-L557) (`split_into_name_segments`)
  - Per-name states → [`L560-L598`](src/dua/probing/stages/stage1_generate.py#L560-L598) (`extract_per_name`)
- **HDF5 layout** (`per_query/p1..p5` as `(N, n_L, D)` fp16, plus `per_name/*` and a `completed_mask`) → [`stage1_generate.py:L605-L669`](src/dua/probing/stages/stage1_generate.py#L605-L669) (`init_h5`)
- **Writing P9 rows** → [`L672-L691`](src/dua/probing/stages/stage1_generate.py#L672-L691) (`_append_per_name`)
- **Per-paper write** → [`L780-L796`](src/dua/probing/stages/stage1_generate.py#L780-L796)
- **Outputs:** `embeddings.h5` and `meta.json`.

### §7 / A7 — Scoring the open-model answers (stage 2)
The same matching levels as §4.5 score each answer. Every P9 name is also labelled matched or hallucinated.
- **Per-paper HR2/HR4/HR5** → [`stage2_score.py:L127-L130`](src/dua/probing/stages/stage2_score.py#L127-L130) (`score_paper`), calling [`scholar_utils.py:L395`](src/dua/probing/scholar_utils.py#L395) (`score_authors`)
- **Matcher** → [`scholar_utils.py:L35`](src/dua/probing/scholar_utils.py#L35) (`NameSplitter`), [`L222`](src/dua/probing/scholar_utils.py#L222) (`NameMatcher`)
- **Per-name label** → [`scholar_utils.py:L436`](src/dua/probing/scholar_utils.py#L436) (`per_name_is_hallucinated`), used at [`stage2_score.py:L226`](src/dua/probing/stages/stage2_score.py#L226)
- **Outputs:** `scored.tsv` and `per_name_labels.tsv`. Stage 4 fits the citation-only OLS (`citation_regression*.csv`).

### A7.1 — P1 carries the strongest signal
A ridge decoder predicts log(citations+1) for each position and layer. P1 gives the best cross-validated R². The signal peaks in mid-to-late layers (Figures A11–A12).
- **Fold-safe decoder:** PCA(100) → scaler → RidgeCV, refit inside each of 5 folds → [`prevalence/decoders.py:L50-L93`](src/dua/probing/stages/prevalence/decoders.py#L50-L93) (`fold_safe_pca_ridge_oof`)
- **Sweep and peak per strategy** → [`prevalence/layer_sweep.py:L29-L82`](src/dua/probing/stages/prevalence/layer_sweep.py#L29-L82) (`run_validated_strategy_layer_sweep`, `strategy_peak_summary`)
- **Earlier stage-5 sweep** → [`stage5_embedding_prevalence.py:L69-L173`](src/dua/probing/stages/stage5_embedding_prevalence.py#L69-L173) (`svd_reduce`, `fit_prevalence_cv`). Its SVD is fit on the full set, so it isn't fold-safe; stage 8 replaces it.
- **Protocol comparison** → [`prevalence/protocol_comparison.py:L27-L47`](src/dua/probing/stages/prevalence/protocol_comparison.py#L27-L47) (`run_protocol_comparison`)
- **Figures** → [`tables.py:L402`](src/dua/probing/tables.py#L402) (`figure_strategy_comparison`), [`L432`](src/dua/probing/tables.py#L432) (`figure_prevalence_depth`)
- **Outputs:** `validated_strategy_layer_prevalence.csv`, `validated_strategy_peak_r2.csv`, `prevalence_decoding_protocol_comparison.csv`

### §7 / A7.2 — Internal states predict prevalence
P1 predicts log(citations+1) with the following cross-validated R²:

| Features | Qwen | Mistral |
|---|---|---|
| P1 | 0.615 | 0.585 |
| Metadata alone | 0.039 | 0.039 |
| Metadata + P1 | 0.620 | 0.590 |
| P1, within a field (mean) | 0.589 | 0.563 |
| P1, after removing the title-only baseline (R² 0.13) | 0.520 | 0.483 |

- **Load P1 at the peak layer** → [`prevalence/common.py:L227-L238`](src/dua/probing/stages/prevalence/common.py#L227-L238) (`load_p1_embeddings`)
- **Metadata features** → [`prevalence/decoders.py:L96-L112`](src/dua/probing/stages/prevalence/decoders.py#L96-L112) (`metadata_matrix`)
- **Metadata / P1 / combined decoders, producing the out-of-fold score `p1_prevalence_pred_oof`** → [`prevalence/adjusted_decoding.py:L26-L104`](src/dua/probing/stages/prevalence/adjusted_decoding.py#L26-L104) (`run_adjusted_decoding`)
- **Within-field decoding** → [`prevalence/within_field.py:L24-L137`](src/dua/probing/stages/prevalence/within_field.py#L24-L137) (`run_within_field_decoding`)
- **Title-only baselines (TF-IDF, SBERT)** → [`stage13_title_only_baselines.py:L65`](src/dua/probing/stages/stage13_title_only_baselines.py#L65), [`L114`](src/dua/probing/stages/stage13_title_only_baselines.py#L114), [`L154`](src/dua/probing/stages/stage13_title_only_baselines.py#L154)
- **P1 refit on the title residual** → [`stage13_title_only_baselines.py:L277-L285`](src/dua/probing/stages/stage13_title_only_baselines.py#L277-L285)
- **Tables** → [`tables.py:L53`](src/dua/probing/tables.py#L53), [`L79`](src/dua/probing/tables.py#L79), [`L132`](src/dua/probing/tables.py#L132), [`L159`](src/dua/probing/tables.py#L159)

### A7.3 — Negative controls
Labels are shuffled and the same decoder is refit. R² falls to about zero.
- **Shuffled-label loop** → [`prevalence/negative_controls.py:L22-L48`](src/dua/probing/stages/prevalence/negative_controls.py#L22-L48) (`run_negative_controls`)
- **Table** → [`tables.py:L109`](src/dua/probing/tables.py#L109) (`table_negative_control`)

### A7.4 — Linear decodability across citation levels (classification)
Four binary tasks are classified from P1 with a class-balanced logistic regression. AUROC for Qwen / Mistral:

| Task | AUROC |
|---|---|
| Head vs. tail | 0.975 / 0.970 |
| Top decile | 0.946 / 0.930 |
| Above median | 0.895 / 0.888 |

- **Classifier** (StratifiedKFold, fold-safe PCA → scaler → `LogisticRegression`) → [`prevalence/bucket_probe.py:L23-L65`](src/dua/probing/stages/prevalence/bucket_probe.py#L23-L65) (`classify_with_cv`)
- **Task definitions and 4-quartile multiclass** → [`prevalence/bucket_probe.py:L68-L179`](src/dua/probing/stages/prevalence/bucket_probe.py#L68-L179) (`multiclass_bucket_probe`, `run_citation_bucket_probe`)
- **Table** → [`tables.py:L190`](src/dua/probing/tables.py#L190) (`table_bucket_probe`)
- **Related classifiers that are not in the paper:**
  - HR2-threshold probes → [`stage6_followup_analyses.py:L140`](src/dua/probing/stages/stage6_followup_analyses.py#L140), with labels at [`L247-L274`](src/dua/probing/stages/stage6_followup_analyses.py#L247-L274)
  - SVD direction plus probe AUROC → [`stage3_eval.py:L97-L169`](src/dua/probing/stages/stage3_eval.py#L97-L169)

### §7 / A7.5 — More prevalent in the representation, fewer hallucinations
Deciles are formed over the out-of-fold P1 prevalence score. Mean HR2 falls from the lowest decile to the highest: from 0.994 to 0.843 for Qwen, and from 0.995 to 0.879 for Mistral.
- **Deciles** → [`prevalence/deciles.py:L14-L42`](src/dua/probing/stages/prevalence/deciles.py#L14-L42) (`run_internal_deciles`)
- **Figure 7 and table** → [`tables.py:L213-L249`](src/dua/probing/tables.py#L213-L249) (`table_internal_deciles`)

### §7 / A7.6 — Mediation analysis
The model has three parts:
- **Treatment:** log(citations+1), moved from its 25th to its 75th percentile.
- **Mediator:** the out-of-fold P1 score.
- **Outcome:** HR2.

The mediated share is 67.3% for Qwen and 51.9% for Mistral.
- **R `mediation::mediate` (the reported result)** → [`stage9_modern_mediation.py:L270-L318`](src/dua/probing/stages/stage9_modern_mediation.py#L270-L318) (`mediate_linear`), run by [`L346-L381`](src/dua/probing/stages/stage9_modern_mediation.py#L346-L381) (`run_r_analysis`)
- **Control mediators** → [`L25-L28`](src/dua/probing/stages/stage9_modern_mediation.py#L25-L28) (`CONTROL_MEDIATORS`)
- **Earlier Baron–Kenny version** → [`stage5_embedding_prevalence.py:L226-L253`](src/dua/probing/stages/stage5_embedding_prevalence.py#L226-L253) (`bootstrap_indirect`), [`L272`](src/dua/probing/stages/stage5_embedding_prevalence.py#L272) (`run_mediation`)
- **Table** → [`tables.py:L253-L278`](src/dua/probing/tables.py#L253-L278) (`table_mediation`)
- **Requires:** R with the `mediation` package.

### §7 / A7.7 — Activation steering
The steering vector is the difference between mean P1 for well-attributed and hallucinated papers. It is applied at α = −2 to 50 papers each model gets right.
- **Result:** HR2 rises from 10% to 70% for Qwen and from 36% to 82% for Mistral.
- **Random-direction control:** five norm-matched random directions reach at most 48% and 52%.
- **Probe-direction control:** the probe direction reproduces the effect.
- **Fix arm:** steering the other way does not repair failures.

Code:
- **Disjoint vector and evaluation pools** → [`stage14_activation_steering.py:L189-L251`](src/dua/probing/stages/stage14_activation_steering.py#L189-L251) (`select_pools`)
- **P1 re-extraction** → [`L102-L106`](src/dua/probing/stages/stage14_activation_steering.py#L102-L106) (`extract_p1`)
- **Difference-of-means vector** → [`L254-L255`](src/dua/probing/stages/stage14_activation_steering.py#L254-L255) (`build_vector`)
- **Steering hook** (adds `alpha * vector` to the output of `decoder_layers[layer]`) → [`L109-L123`](src/dua/probing/stages/stage14_activation_steering.py#L109-L123) (`make_steering_hook`), registered in [`L297-L333`](src/dua/probing/stages/stage14_activation_steering.py#L297-L333) (`run_condition`)
- **Induce arm and fix arm** → [`L455-L485`](src/dua/probing/stages/stage14_activation_steering.py#L455-L485)
- **Shuffled-label and norm-matched random controls** → [`L258-L294`](src/dua/probing/stages/stage14_activation_steering.py#L258-L294)
- **Reported controls (stage 24):**
  - Norm matching → [`stage24_position_probe_steering.py:L181`](src/dua/probing/stages/stage24_position_probe_steering.py#L181) (`norm_match`)
  - Position-masked hook → [`L79-L119`](src/dua/probing/stages/stage24_position_probe_steering.py#L79-L119)
  - Five random seeds → [`L297-L318`](src/dua/probing/stages/stage24_position_probe_steering.py#L297-L318)
- **Probe direction mapped to raw hidden space** → [`stage16_vector_analysis.py:L79-L100`](src/dua/probing/stages/stage16_vector_analysis.py#L79-L100) (`probe_ridge_direction`)
- **McNemar and paired bootstrap** → [`analyze_steering_paired_stats.py:L54-L74`](src/dua/probing/stages/analyze_steering_paired_stats.py#L54-L74)
- **Exploratory work behind "cannot repair":**
  - [`stage17_graded_bin_steering.py`](src/dua/probing/stages/stage17_graded_bin_steering.py)
  - [`stage18_layer_sweep.py`](src/dua/probing/stages/stage18_layer_sweep.py)
  - [`stage20_fix_layer_sweep.py`](src/dua/probing/stages/stage20_fix_layer_sweep.py)
  - [`stage22_norm_relative_fix.py:L69-L90`](src/dua/probing/stages/stage22_norm_relative_fix.py#L69-L90)
  - [`stage19_causal_tracing.py:L74-L109`](src/dua/probing/stages/stage19_causal_tracing.py#L74-L109)
- **Table** → [`tables.py:L325-L392`](src/dua/probing/tables.py#L325-L392) (`table_steering`)
- **Check a re-run against the shipped numbers** → [`tools/check_steering_controls.py`](tools/check_steering_controls.py) (`make check-steering-controls`)

### A7.8 — Entity-level analysis with P9 name states
Each generated name's P9 state is labelled matched or hallucinated. About 97% of names are hallucinated. The balanced-logistic probe reaches AUROC 0.814 for Qwen and 0.818 for Mistral. Because of the imbalance, AUPRC lift is only about 1.02. Nearest-centroid balanced accuracy is 0.76 for Qwen and 0.74 for Mistral.
- **Load P9 states and align labels** → [`stage12_p9_robustness.py:L169-L204`](src/dua/probing/stages/stage12_p9_robustness.py#L169-L204) (`analyze_run`)
- **Balanced logistic probe** → [`L132-L166`](src/dua/probing/stages/stage12_p9_robustness.py#L132-L166) (`run_probe`)
- **Centroid effect size** → [`L104-L114`](src/dua/probing/stages/stage12_p9_robustness.py#L104-L114) (`pooled_rms_effect_size`)
- **Nearest-centroid balanced accuracy** → [`L117-L129`](src/dua/probing/stages/stage12_p9_robustness.py#L117-L129)
- **Earlier geometry and PCA** → [`stage6_followup_analyses.py:L409`](src/dua/probing/stages/stage6_followup_analyses.py#L409), [`stage7_make_figures.py:L231`](src/dua/probing/stages/stage7_make_figures.py#L231)
- **Table** → [`tables.py:L460-L499`](src/dua/probing/tables.py#L460-L499) (`table_p9_entity`)
- **Layer mismatch:** the stage 12 docstring's default Mistral layer is 20, not 22.

---

## 8. Additional findings (§8, A5.2–A5.7)

### §8 / A5.2 — Author position
Recall gets worse further down the true author list. GPT-4o's hallucination rate rises from 34.2% at the first generated position to 75.5% at later ones.
- **Counts by position** → [`position.py:L28-L75`](src/dua/analysis/position.py#L28-L75) (`positional_counts`)
- **Plot** → [`position.py:L76-L111`](src/dua/analysis/position.py#L76-L111)

### §8 / A5.3 — Author count
The negative correlation with author count is an artifact. Models pad short lists: a single-author paper gets about 2.5 names, of which about 2.3 are fabricated. Output length tracks the true count (ρ ≈ 0.55), but not steeply enough.
- **Drop runaway generations** → [`author_count.py:L28-L41`](src/dua/analysis/author_count.py#L28-L41)
- **Output by true author count** → [`author_count.py:L42-L76`](src/dua/analysis/author_count.py#L42-L76) (`table_author_output`)
- **Per field** → [`author_count.py:L77-L107`](src/dua/analysis/author_count.py#L77-L107) (`table_field_author`)
- **Output-length scaling** → [`author_count.py:L108-L122`](src/dua/analysis/author_count.py#L108-L122) (`output_scaling`)

### §8 / A5.4 — Ethnic distribution of hallucinated names
Hallucinated names track the population in the literature (Cramér's V ≈ 0.03). Counting each distinct fabricated name once shows a small skew:

| Group | Ratio to population |
|---|---|
| English/Western | 1.5–1.6× |
| Korean | 1.4–1.8× |
| Russian | 0.60–0.67× |
| French | about 0.73× |

- **Corpus surname counts** → [`name_frequency.py:L23-L47`](src/dua/analysis/name_frequency.py#L23-L47)
- **Hallucinated-surname tallies, by population and by diversity** → [`name_frequency.py:L48-L96`](src/dua/analysis/name_frequency.py#L48-L96)
- **Classify surnames with `ethnicseer`** → [`ethnicity.py:L49-L85`](src/dua/analysis/ethnicity.py#L49-L85)
- **χ², Cramér's V, ratios, Bonferroni** → [`ethnicity.py:L45-L48`](src/dua/analysis/ethnicity.py#L45-L48), [`L86-L122`](src/dua/analysis/ethnicity.py#L86-L122) (`compare`)
- **Run and figures** → [`ethnicity.py:L127-L202`](src/dua/analysis/ethnicity.py#L127-L202). Run with `make ethnicity`.

### §8 / A5.5 — Title length
Controlling for citations, the correlation with title length is not significant (p = 0.076–0.479).
- **Partial Spearman** → [`title_length.py:L22-L36`](src/dua/analysis/title_length.py#L22-L36)
- **Fisher-pooled within bins** → [`title_length.py:L37-L58`](src/dua/analysis/title_length.py#L37-L58)
- **Table** → [`title_length.py:L59-L85`](src/dua/analysis/title_length.py#L59-L85)

### §8 / A5.6 — Multivariate and mixed-effects regression
- **Fractional logit:** each doubling of citations cuts the odds of hallucination by 34–36%. Title length is not significant.
- **Mixed-effects model:** a random field intercept gives the same result, with ICC ≈ 2%.

Code:
- **Design matrix** → [`regression.py:L27-L52`](src/dua/analysis/regression.py#L27-L52)
- **Fractional logit** → [`regression.py:L53-L83`](src/dua/analysis/regression.py#L53-L83) (`fit_fractional_logit`)
- **Mixed effects and ICC** → [`regression.py:L84-L118`](src/dua/analysis/regression.py#L84-L118) (`fit_mixed_effects`)
- **Tables** → [`regression.py:L119-L164`](src/dua/analysis/regression.py#L119-L164)

### §8 / A5.7 — Prompt sensitivity
DeepSeek-R1 was run on 1,004 papers with a baseline, an emotional, and an authoritative prompt. HR2 ρ is −0.450 at baseline and −0.474 for both variants. Bootstrap 95% CIs on the difference in ρ include zero.
- **Variant prompt text:** _not in repo._ `config/prompts/` has only the baseline prompts.
- **Align records and compute summaries** → [`stage10_prompt_sensitivity_significance.py:L173-L257`](src/dua/probing/stages/stage10_prompt_sensitivity_significance.py#L173-L257)
- **Paired bootstrap (10,000 draws)** → [`L164-L172`](src/dua/probing/stages/stage10_prompt_sensitivity_significance.py#L164-L172), [`L258-L328`](src/dua/probing/stages/stage10_prompt_sensitivity_significance.py#L258-L328)
- **Tables** → [`prompt_sensitivity.py:L41-L123`](src/dua/analysis/prompt_sensitivity.py#L41-L123). Run with `make prompt-sensitivity`.

---

## 9. Discussion (A8)

A8 is discussion, not experiments. A8.3 ("Consistency Across Architectures") rests on the two-model results in §7.

Stage 8 also writes one output that no paper table uses: the P1 decoder's error by citation bucket, `prevalence_residual_summary.csv` → [`prevalence/residuals.py:L20-L42`](src/dua/probing/stages/prevalence/residuals.py#L20-L42) (`run_prevalence_residual_summary`).
