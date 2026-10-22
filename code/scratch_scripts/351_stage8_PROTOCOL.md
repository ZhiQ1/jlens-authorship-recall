cat > ~/351_stage8_PROTOCOL.md <<'MD'

# Stage 8 — Independent Validation



## Status



Stage 8A is completed and frozen on Explorer.



- 200 independent papers.

- 100 exact field/citation-bin matched A/B pairs.

- A: Recognition Pass / R0.

- B: Recognition Fail / R0.

- Low: 25 pairs, citation bin 0–2.

- Middle: 50 pairs, citation bin 3–128.

- High: 25 pairs, citation bin 129+.



Stage 8A manifest SHA256:



7e4b878e9ee037fe822cc42821218459ff48b203cd026de6995a79ca13486f55



Never reselect papers after reading J-Lens outcomes.



The 50-paper Stage 4–7.4 pilot is exploratory.

Stage 8 is an independent validation experiment.



## Research Questions



### RQ1 — Replication of L56 Title-specific Signal



Does the L56 Title-specific Advantage replicate on

200 previously untested scientific papers?



Primary measurement:



Title-specific Advantage =

Gold Candidate Win under the true paper title

minus

the average Gold Candidate Win under 20 wrong titles.



The same frozen 100 false-author candidates must be

used in both the true-title and wrong-title contexts.



The primary analysis uses the paper as the unit.



Report:



- Mean L56 advantage.

- Paper-cluster bootstrap 95% confidence interval.

- Median and variance.

- Number of papers with positive advantage.

- Per-paper null rank and descriptive null-tail position.



The 20 shuffled-title contexts are NOT 20 independent

papers and must not be used as independent bootstrap units.



Do not describe a 20-shuffle empirical tail as an

exactly calibrated permutation p-value.



### RQ2 — Recognition Pass versus Recognition Fail



Among papers with failed free recall (R0), does

Recognition Pass correspond to greater L56

Title-specific Advantage than Recognition Fail?



A: Recognition Pass / R0.

B: Recognition Fail / R0.



Primary comparison:



Mean of 100 matched-pair differences:



L56 Advantage(A) - L56 Advantage(B).



Resample complete matched pairs for the

bootstrap 95% confidence interval.



Do not bootstrap A and B independently.



The observational matching does not demonstrate

that Recognition causes stronger representations.



### RQ3 — Low-Citation Accessibility



Does the positive title-specific signal persist

among papers in citation bin 0–2?



Compare:



Low: citation bin 0–2.

High: citation bin 129+.



Use L56 Title-specific Advantage.



Analyze A and B separately and report the

group-balanced Low-minus-High contrast.



Use the matched-pair structure where applicable.

Report confidence intervals and paper-level variation.



The Middle group is retained as descriptive evidence.



A positive mean in the Low group does not, by itself,

establish a universal factual Accessibility Floor.



## Layer Policy



Fixed layers:



16, 24, 32, 40, 48, 56, 62.



L56 is the predeclared replication layer.



All seven layer trajectories must be reported.



Integrated seven-layer statistics are secondary,

not replacements for the fixed primary L56 outcomes.



Do not choose a different layer based on Stage 8 scores.



## J-Lens versus Vanilla



Use the same contexts, candidate token IDs,

papers, layers, and aggregation rules.



Report:



- J-Lens Title-specific Advantage.

- Vanilla Title-specific Advantage.

- J-Lens minus Vanilla difference-in-differences.

- 95% confidence intervals.

- Per-layer curves and paper-level variation.



There is no prior assumption that J-Lens is superior.



The Stage 7.4 pilot found only a small average

J-Lens-specific increment with an interval crossing zero.



## Stage 8B — Frozen Negative Controls



For each target paper:



- One first-listed Gold Author.

- 50 matched False Authors.

- 50 random False Authors.

- 20 wrong paper titles.



Total:



200 Gold Author candidate records.

10,000 matched False Author records.

10,000 random False Author records.

20,200 total author candidate records.

4,000 wrong-title records.



The complete true-author list is used to exclude

all actual coauthors from the false-author pools.



All candidate names must be distinct within a paper.



Use the Qwen3-32B tokenizer with a leading space

before the author name and add_special_tokens=False.



Record:



- First-token ID.

- Full candidate token IDs.

- Name token count.

- Gold/False first-token collision.

- Matching tier.

- Source paper information.

- Year gap.

- Field and citation-bin information.



Wrong-title controls:



- Use distinct source paper IDs.

- Do not reuse the target title.

- Exclude papers sharing true authors with the target.

- Prefer same field and citation bin.

- Then use year proximity and title-token length.

- Preserve the target paper's publication year in the prompt.



Record:



- Wrong title and source paper.

- Match tier.

- Year gap.

- Title token length gap.

- Source-author overlap checks.

- Whether the source author occurs in the false pool.



The Stage 8B candidate construction is deterministic

but is not guaranteed to exactly reproduce the

Stage 7.2/7.3 matching distribution.



Differences in matching quality must be audited

and disclosed before Stage 8C scoring.



## Stage 8B Outputs



Under /scratch/$USER/jlens/351_stage8:



controls/stage8_author_candidates.csv

controls/stage8_shuffled_titles.csv

controls/stage8_control_quality.csv

config/stage8B_manifest.json



The manifest records:



- Frozen Stage 8A manifest checksum.

- Full source manifest checksum.

- Tokenizer name and revision.

- Deterministic selection seed.

- Row counts.

- Output file SHA256 hashes.



Frozen controls must not be changed after

outcome inspection.



## Stage 8C — GPU Scoring



Stage 8B does not implement GPU scoring.



Required model:



Qwen/Qwen3-32B



Model revision:



9216db5781bf21249d130ec9da846c4624c16137



Public J-Lens:



Qwen3-32B Jacobian Lens,

Neuronpedia Salesforce-wikitext.



Public Lens SHA256:



0af5ccf2e1c251bedc202607a7ca214f3b9f60980bab73d67a3d0b887db213d8



Score:



200 true-title contexts.

4,000 wrong-title contexts.

4,200 total contexts.



All seven layers:



16, 24, 32, 40, 48, 56, 62.



Freeze the exact prompt format, token IDs,

runtime settings and manifests before scoring.



Preserve:



- Per-context raw scores.

- Per-paper candidate win rates.

- Per-layer J-Lens scores.

- Per-layer Vanilla scores.

- Context, paper and candidate identifiers.

- Checkpoint/restart records.

- Model and readout checksums.



Do not use any gold-name prefix for the

primary first-token outcome.



Teacher-forced author continuation is separate

and cannot substitute for unassisted recall.



## Stage 8D — Statistical Validation



Run all three predeclared research questions.



Use fixed bootstrap seeds.



Required analyses:



1. L56 paper-level True-minus-Null advantage.

2. L56 matched A-minus-B advantage.

3. Group-balanced Low-minus-High contrast.

4. J-Lens versus Vanilla difference-in-differences.

5. Seven-layer descriptive trajectories.

6. First-token collision sensitivity.

7. Name token-count and name-prior checks.

8. False-title matching quality checks.

9. Outlier and per-paper distribution checks.

10. Comparison with the exploratory 50-paper pilot.



Deliver:



- Raw JSONL/CSV.

- Summary CSV.

- Bootstrap distributions and confidence intervals.

- Figures in PNG and PDF.

- Markdown Methods/Results/Limitations.

- Configuration and SHA256 checksums.



## Stage 9 Separation



Stage 9 tests Readout Stability:



- Split-half Lens fitting.

- Fitting sample-size sensitivity.

- Final-logit anchor.

- Token-type controls.

- Prompt-format controls.



Do not use Stage 8 outcomes to select a

self-fitted Lens, optimize prompt format,

or choose a favorable source layer.



If independently calibrated lenses are later

applied to Stage 8, report the analysis transparently

as predeclared or exploratory as appropriate.



## Scientific Interpretation



Stage 8 can establish whether a measured

title-conditioned author-token association replicates.



It cannot alone demonstrate:



- Full multi-token author identity recovery.

- Successful free recall.

- Causal knowledge retrieval.

- J-Lens superiority without direct evidence.

- A universal accessibility floor.

- The absence of knowledge when a readout fails.



## Completion Criteria



Stage 8 is complete when:



- All 200 papers have frozen valid controls.

- All 4,200 contexts are scored or documented

  as failures without selective exclusion.

- All three primary research questions are tested.

- J-Lens/Vanilla comparisons are reported.

- Raw records, statistics, figures and reports

  can be independently regenerated.

- No post-hoc resampling or layer selection is

  used to manufacture a favorable result.



Negative or inconclusive findings count as

completed science when the protocol is satisfied.

