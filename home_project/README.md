# Dreaming Up Authors

Code and data for **"Dreaming Up Authors: Factual Prevalence and LLM
Hallucinations in Academic Authorship Attribution"** (EMNLP 2026).

The paper asks whether large language models hallucinate more about facts that
are rare in their training data. It uses academic authorship attribution as the
testbed and citation count as a proxy for prevalence, over 1.92M curated papers
and a 9,108-paper stratified evaluation sample. Hallucination rates exceed 98%
for rarely cited papers and fall below 36.4% for highly cited ones, across
GPT-4o, DeepSeek-R1, and Claude Sonnet 4.5.

## Start here

```bash
git clone <this repo> && cd dreaming-up-authors-code
make install
source .venv/bin/activate
make verify      # unit tests, checksums, cross-artifact invariants
make all         # every table, figure, and quoted number
```

`make all` takes about a minute. It needs no network, no API key, and no GPU.
It reads the 15 MB of shipped artifacts in `data/release/` and writes
`results/tables/*.tex`, `results/figures/*.pdf`, and `results/metrics/*.json`.

Python 3.11 or 3.12. `make install` uses `uv` when present and falls back to
`python3.12`/`python3.11` on `PATH`.

## What backs which claim

| Paper artifact | Command | Output |
|---|---|---|
| Figure 2, HR2 by citation count | `dua analyse --only results` | `fig_hr2_by_citation.pdf` |
| Figure 3, field variance radar | `dua analyse --only results` | `fig_field_variance_radar.pdf` |
| Figure 4, GPT-4o by field | `dua analyse --only results` | `fig_gpt4o_field_by_citation.pdf` |
| Table 2, sample per field | `dua analyse --only results` | `field_sample_sizes.tex` |
| Table 3, Spearman by field × model | `dua analyse --only results` | `spearman_all_models.tex` |
| §4.1 stratum stability | `dua analyse --only stratum_stability` | `stratum_stability.tex` |
| §4.5 / A6.5 evaluator agreement | `dua analyse --only eval_agreement` | `eval_agreement.tex`, `variance_comparison.tex` |
| A6.1–A6.3 HR metrics and decomposition | `dua analyse --only hr_decomposition` | `spearman_hr.tex`, `pearson_hr.tex`, `hr4_hr5_binwise.tex` |
| A6.8 positional bias | `dua analyse --only position` | `fig_positional_*.pdf` |
| A6.9 author count | `dua analyse --only author_count` | `author_output.tex`, `field_author.tex` |
| A6.11 title length | `dua analyse --only title_length` | `title_length.tex` |
| A6.12 regression | `dua analyse --only regression` | `regression_summary.tex` |
| A6.13 prompt sensitivity | `make prompt-sensitivity` | `spearman_prompt.tex`, `mean_prompt.tex` |
| §7 / A8 hidden-state probing | `make probing-tables` | `prevalence_decoding.tex`, `mediation_summary.tex`, `steering.tex`, … |
| Every number quoted in prose | `dua metrics` | `results/metrics/metrics.json` |

Five stages need something this repository cannot ship, so their outputs are
**not** in a fresh clone. The generators are here and the commands are real;
what is missing is a key, a cache, or a 7.3 GB file.

| Paper artifact | Command | Needs |
|---|---|---|
| §2.2 corpus statistics (Tables 1, A4–A9) | `dua distributions` | the 1.92M-paper corpus |
| §2.2 pre-filter tables (A1–A3) | *no generator* | a 100k Semantic Scholar-enriched pre-filter sample |
| §3 prevalence proxies (Figure 1, six tables) | `dua proxy both --offline`, then `dua proxy analyse` | a proxy response cache |
| §6 / A7 multiple-choice recognition | `dua recognise --analyse` | `OPENAI_API_KEY` |
| A6.10 ethnicity | `make ethnicity` | the `ethnicity` extra; ~6 minutes |

## Four tiers of reproducibility

Conflating these is what makes reproducibility claims fail, so they are
labelled explicitly.

**Deterministic — bit-identical given the same inputs and seed.** Corpus
filtering, stratified sampling, name matching, every metric, every table and
figure. Re-scoring the 27,324 shipped model responses with `dua.evaluate`
reproduces the published `(M, H, U)` triple on 100% of rows for all three
models. `make verify` checks a sample of that on every run.

**Archived — not regenerable, shipped as frozen artifacts.** The LLM responses
(§4–§6), the Google hit counts and Infini-gram counts (§3). Temperature 0 is
not a determinism guarantee for hosted APIs: OpenRouter routed the DeepSeek-R1
run across eight upstream providers, and two of the three models were reached
through floating aliases rather than dated snapshots. `config/models.yaml`
records exactly what was called and when. Re-running the collection produces
*similar* numbers, not identical ones.

**Reimplemented: not byte-identical to the paper.** The §6 multiple-choice
recognition code in `dua.recognition` was rebuilt from the appendix
description, because no code for it existed in either original source tree.
It meets every integrity check the appendix states: no duplicate names, no
distractor that overlaps a true author, and the correct option within 2 pp of
uniform. But its distractor sampling is seeded differently from the original
run, GPT-4o at temperature 0 is not deterministic, and the collaborator-swap
control depends on Semantic Scholar author records that change over time. No
MC results are shipped. A re-run should land close to the published numbers,
not on them. The recall side of the gap is the exception: it comes from the
shipped GPT-4o responses and matches exactly.

**External and drifting — snapshot-dated.** Semantic Scholar citation counts,
as of September 2025. Re-querying today gives different values and would move
every bin assignment.

## Repository layout

```
config/          config.yaml, models.yaml, and the verbatim prompt templates
src/dua/
  data/          Stage A  corpus construction and the five-stage filter
  sampling/      Stage B  the 9,108-paper stratified draw
  proxy/         Stage C  Google hits and Infini-gram prevalence proxies
  collect/       Stage D  LLM response collection
  evaluate/      Stage E  name matching and the HR metrics
  recognition/   Stage F  multiple-choice recognition (§6); not byte-identical, see above
  probing/       Stage G  hidden-state probing and steering (§7)
    stages/prevalence/    Stage 8's experiments, one module each
  analysis/      Stage H  every table and figure
data/release/    the shipped artifacts, 15 MB, checksummed
results/         generated output; `make clean` removes it
tests/           matcher fixtures, metric identities, MC construction
tools/           maintainer scripts, not part of the reviewer path
```

Run `make help` for every target, or `dua --help` for every subcommand.

## Data

`data/release/` is 15 MB, tracked in git, UTF-8, comma-separated, gzipped, and
verified against `checksums.sha256` by `make verify`.

| | |
|---|---|
| `eval_sample_9108.csv.gz` | the stratified evaluation sample |
| `responses/*.csv.gz` | all three models' answers and scores, on one schema |
| `probing/` | Section 7 probe outputs, so Appendix A8 regenerates without a GPU |
| `prompt_sensitivity/` | Appendix A6.13 inputs |
| `name_frequency/` | surname tallies for Appendix A6.10 |

### `eval_sample_9108.csv.gz`

One row per paper. `paper_id` is the Semantic Scholar `paperId` and the join
key everywhere. `authors` is a JSON array in publication order. `citations` is
a September 2025 snapshot; `citation_bin` is recomputable from it, and
`dua verify` checks that all 9,108 labels still follow.

`year` is Semantic Scholar's, not OAG's, because that is the value the
collection scripts interpolated into the prompt. The two disagree on about
0.02% of the corpus, since OAG stopped updating in 2019. Exactly one paper in
the sample is affected. `dua.data.distributions` prefers the OAG year for the
Section 2.2 temporal table, where the 1800–2019 range is the claim being made.
Each use takes the source its claim rests on.

### `responses/<model>.csv.gz`

One row per paper per model, 9,108 rows each, covering the same papers.
`<model>` is `gpt-4o`, `deepseek-r1`, or `claude-sonnet-4.5`. Carries the raw
`llm_answer`, the `(m, h, u)` counts everything is built on, the matched /
hallucinated / unretrieved name lists, the LLM-as-judge triple for GPT-4o, and
call provenance.

The paper writes **M** (matches), **H** (hallucinations), **U** (unretrieved).
The original CSVs wrote the same quantities as `matched_gt_authors(X)`,
`hallucinated_llm_authors(Y)`, `unmatched_gt_authors(Z)`. They map in order:
`X = M`, `Y = H`, `Z = U`. The released files use `m`, `h`, `u`. All five
hallucination rates are functions of that triple alone and are recomputed on
every load rather than stored, so a changed definition cannot leave a stale
column behind.

The provenance columns are **empty for GPT-4o**, not fabricated. See
[Provenance](#provenance).

### `probing/` and `name_frequency/`

Probing column names are the originals from `dua.probing.stages`. `strategy`
values are the extraction positions below; **P1** is the one the paper reports.

`name_frequency/` holds gzipped JSON mapping a particle-stripped, title-cased
surname to a count: occurrences across the corpus, papers a surname was
hallucinated into, and one per distinct surname. Surnames only, no given names,
and no per-name list of paper ids. The originals carried one, and shipping it
next to an inferred protected attribute would be the wrong trade.

### What is not in this repository

| | Size | Needed for |
|---|---|---|
| OAG v2 sample, 9,999,863 records | ~15 GB | rebuilding the corpus from scratch |
| Curated corpus, 1,921,209 papers | 7.3 GB gzipped | resample, §2.2 distributions, surname frequencies |
| `lid.176.bin` FastText model | 126 MB | the language filter |
| Model weights (Qwen3-32B, Mistral-Small-3.2-24B) | ~60 GB, ~48 GB | Section 7 extraction |

None of these are needed for `make all`. Point at local copies with `DUA_CORPUS`,
`DUA_OAG_POOL`, `DUA_FASTTEXT_LID`, or by writing `config/config.local.yaml`,
which is gitignored and merged over `config.yaml`.

FastText comes from
<https://fasttext.cc/docs/en/language-identification.html>. The language filter
removes 47.9% of records, by far the largest of the five, so **retention will
not match the paper without it**. `dua filter` warns loudly on stderr when the
model is absent rather than quietly reporting a different number.

Semantic Scholar enrichment — the step that attaches citation counts, canonical
names, and field labels — is not in this repository. It was a separate
distributed pipeline. The corpus is the artifact; enrichment is documented in
Section 2 of the paper.

## Section 7: probing and steering

Two halves with very different requirements. **Analysis needs no GPU**:
`make probing-tables` reads `data/release/probing/` and writes every Appendix
A8 table and figure in seconds. **Extraction needs a GPU**:
`dua.probing.stages.*` runs Qwen3-32B and Mistral-Small-3.2-24B over the 9,108
papers, extracts hidden states, fits probes, and applies steering. Roughly
6–12 GPU-hours per model plus 40–90 GB of scratch.

### Extraction positions

| | |
|---|---|
| **P1** | last prompt token, before any answer token is generated |
| P2, P3 | first and last generated token |
| P4, P5 | mean-pooled prompt and generated-answer state |
| P9 | last token of each generated author name (entity level) |

P1 is what the paper reports. The prevalence signal is strongest there, and
because it precedes generation, a signal there cannot be a post-hoc summary of
what the model happened to say.

### Which stages back the paper

Stages marked **cited** produce something the camera-ready reports. The rest is
robustness work kept for completeness; the source docstrings carry the
findings.

| Stage | Produces | Paper |
|---|---|---|
| `stage1_generate`, `stage2_score`, `stage3_eval` | embeddings, per-paper (M, H, U), HR metrics | **cited** — input to everything below |
| `stage5_embedding_prevalence` | layer × strategy sweep | **cited** — Figures A7, A8 |
| `stage8_prevalence_appendix` | validated strategy, adjusted and within-field decoding, negative controls, bucket probe, internal deciles; one module per experiment in `stages/prevalence/` | **cited** — Tables A18–A22, Figure 6 |
| `stage9_modern_mediation` | `modern_mediation_summary.csv` | **cited** — Table A23 |
| `stage12_p9_robustness` | `p9_robustness_summary.csv` | **cited** — Table A24 |
| `stage13_title_only_baselines` | `title_vs_p1_comparison.csv` | **cited** — the R² = 0.13 baseline |
| `stage14_activation_steering` | `steering_results.csv` | **cited** — Appendix A8.8 |
| `stage15_norm_matched_control` | norm-matched control at α = 1 and α = 2 | **cited** — the single-direction control |
| `stage24_position_probe_steering` | `position_probe/…_eval_high.csv` | **cited** — Table A25 |
| `analyze_steering_paired_stats` | `paired_hr_stats.csv` | **cited** — the paired CIs on the steering effect |
| `stage4`, `stage10`, `stage11`, `analyze_steering_name_recall` | regression, significance, binwise, name recall | supporting |
| `stage16`–`stage23`, `analyze_localization_vs_editing` | vector analysis, graded-bin steering, layer sweeps, causal tracing | not cited |

Two stages produce a norm-matched random control, and Appendix A8.8 quotes the
second. Stage 15 draws one control direction and sweeps two alphas; its
`steering_meta.json` records `n_control_shuffles: 1`. Stage 24 re-runs the
control arm at five seeds (542–546) and adds a probe-direction arm, both at
α = 2. Table A25's ranges and its 58% / 64% probe result come from Stage 24.
Both are shipped, and they agree.

One caveat carried over: `stage23_fix_logprob_readout`'s E1/E2 readout was
invalidated by a contamination artifact found during development. The rest of
the stage is sound. Nothing in the camera-ready depends on it.

### Running a stage

Every stage is a plain argparse CLI and does not require a scheduler. They read
a prompt CSV with columns `paperId, question, answer, citation, citation_bin,
field` — a view of the released sample, rebuilt rather than shipped twice:

```bash
make probing-prompts        # -> data/interim/probing_prompts_9108.csv
python -m dua.probing.stages.stage1_generate \
    --model_path Qwen/Qwen3-32B \
    --data_csv   data/interim/probing_prompts_9108.csv \
    --out_dir    runs/qwen3_32b
```

The question is a fixed template, so the prompts reproduce exactly. The
`answer` column differs for 68 of the 9,108 papers: the original stripped
apostrophes from surnames (`Goldanskii` for `Gol'danskii`) and the release
preserves them. Scoring is unaffected, because `NameMatcher` compares on an
alphabetic-only normalisation that drops apostrophes on both sides.

### Re-running Table A25 from the release

Stage 24 is the one cited stage cheap enough to re-run alone: one GPU, about
two hours per model, and no HDF5 extraction. Every other input is shipped, so
weights and a GPU are all you bring.

```bash
DUA_MODEL_KEY=qwen3_32b DUA_MODEL=Qwen/Qwen3-32B make steering-controls
DUA_MODEL_KEY=qwen3_32b make check-steering-controls
```

`DUA_MODEL_KEY` picks the layer (48 Qwen, 22 Mistral) and the release
subdirectory. `check-steering-controls` diffs every arm against the shipped
artifact and exits non-zero on disagreement; pass `--tol` on different
hardware, where bitwise-identical generation is not guaranteed.

The open-weight stages are deterministic given the same weights, dtype, and
hardware. Record the revision you pulled; `config/models.yaml` has a `revision`
field for this. Batched generation was tried and rejected: bf16 batching is not
bitwise identical to per-paper generation, and the steering pools were selected
on per-paper rates.

## Provenance

This repository is a fresh, squashed history assembled from two private trees:
one covering Sections 2–6 with heavy duplication, one covering Section 7 that
ported nearly intact.

Several components existed in three to seven near-identical copies. In each
case the version that produced the *published* artifacts was identified and the
rest dropped. The name matcher had seven variants; `name_matcher_v3.py` is
canonical, confirmed empirically — re-scoring all 27,324 published responses
with the ported matcher reproduces the published `(M, H, U)` on 100% of rows
for all three models. The collection scripts had six variants, all dropped:
the one committed still queried six other models and sampled 100 papers into
ten heuristic buckets, so anyone running it would have reproduced a different
experiment.

**GPT-4o came from a different pipeline than the other two models**, and the
difference survives in the archive. Claude and DeepSeek went through OpenRouter
with raw NDJSON, per-call timestamps, response envelopes, and latencies. GPT-4o
went to OpenAI directly, and none of that was kept. Its answers survive; the
calls that produced them do not. The model string was `chatgpt-4o-latest`, a
floating alias that moved after October 2025 — the paper says "GPT-4o", and
these are not the same thing.

Four components had no code on this machine and were rewritten from the paper:
Google hits collection, Infini-gram collection, multiple-choice recognition,
and the A6.12 regression. Each was checked against what the paper reports. The
raw GPT-4o NDJSON does not exist in any recoverable form.

## Datasheet

Following Gebru et al., *Datasheets for Datasets*.

**Motivation.** To measure whether LLMs hallucinate more about facts that
appear rarely in training data. That needs a large set of verifiable facts
spanning several orders of magnitude of prevalence. Authorship attribution
fits: the ground truth is public and unambiguous, and citation count gives a
prevalence proxy that is stable, cheap, and consistently defined.

**Composition.** Academic papers, represented by title, year, author list,
venue, DOI, citation count, and field. 1,921,209 in the curated corpus, drawn
from a random sample of 9,999,863 OAG v2 records (19.2% retention). A
stratified subset of 9,108 is used for LLM evaluation, and a further 6,048 for
the prevalence proxies. It contains real author names, which are personal data;
it contains no directly sensitive attributes.

**Collection.** OAG v2 provides random sampling and Semantic Scholar does not,
hence the two-step design. OAG records were matched to Semantic Scholar by
title, verified by exact normalised title plus first-author surname. Papers are
published 1800–2019, before the knowledge cutoffs of the evaluated models.
Enrichment is as of September 2025. The data is published bibliographic
metadata obtained from public APIs under their terms.

**Preprocessing.** Five filters, with the share removed at each step: document
type, journal and conference only (56.9%); author count 1–20 (0.3%); FastText
English at confidence ≥ 0.8 (47.9%); author name patterns, no institutional,
single-token, or malformed names (0.8%); title and first-author match against
Semantic Scholar (13.5%). Filter 4 drops a paper if *any* author name is
unusable, which is strict but necessary — a paper whose author list contains
"Institute of Physics" has no usable ground truth, and keeping it would score a
correct refusal as a hallucination.

**Uses.** Suitable for measuring hallucination against factual prevalence,
validating citation count as a prevalence proxy, and probing hidden states.
Also plausible for retrieval evaluation, long-tail knowledge benchmarks, and
calibration studies.

**Should not be used for** evaluating or ranking individual researchers,
training a model to predict authorship, or any per-author inference. This is a
measurement instrument for model behaviour, not a record about people.

**Known biases.** English-only, which removes 47.9% of the pool and skews the
disciplinary and geographic mix. Papers are pre-2019. Citation counts favour
older papers and fields with faster citation dynamics. Semantic Scholar's
author disambiguation is imperfect, so some ground-truth lists contain errors;
the fuzzy matcher mitigates but does not eliminate this.

**Maintenance.** Citation counts will not be refreshed. The September 2025
snapshot is what the results are keyed to, and updating it would silently
invalidate every bin assignment.

**Personal data.** Two constraints are enforced in code rather than left to
convention. Results are aggregate: no analysis writes a per-author record.
Appendix A6.10 infers a coarse category from surnames; those labels are
computed at analysis time and **never written to disk**, and the shipped
tallies are surname counts only.

## Keys and configuration

Nothing in this repository contains a credential. Copy `.env.example` to `.env`
and fill in whichever keys your stage needs. Every client reads from the
environment and fails immediately, naming the missing variable.

Every path, seed, bin edge, field list, and model identifier lives in
`config/config.yaml` and `config/models.yaml`. Machine-specific paths go in
`config/config.local.yaml` (gitignored) or `DUA_*` environment variables.

Generated tables and figures carry a provenance header recording the source
module, the git commit, and the seed. `results/metrics/metrics.json` collects
every number quoted in prose. Where a generated value and the paper disagree,
the generated one is the value a reader can check.

## Citation

```bibtex
@inproceedings{zhong2026dreaming,
  title     = {Dreaming Up Authors: Factual Prevalence and {LLM} Hallucinations
               in Academic Authorship Attribution},
  author    = {Zhong, Sijia and Yirga, Tamir and Ma, Yijia and
               Le, Thai and Hu, Yifan},
  booktitle = {Proceedings of EMNLP 2026},
  year      = {2026}
}
```

## Licence

Code: MIT (`LICENSE`). Data: see `DATA_LICENSE.md`.
