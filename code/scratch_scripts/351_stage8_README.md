# Stage 8: Independent-target validation — pre-scoring cohort freeze

## Epistemic sequence

1. Stages 5–7.4 are **exploratory pilot** (50 target papers), not independent confirmation. They motivate hypotheses but cannot yield unbiased confirmatory p-values in the same papers.
2. Freeze unseen target-paper IDs and exact field+citation-bin A/B pairs *before* new scoring. Keep A = Recognition Pass/R0 and B = Recognition Fail/R0. No swapping labels or pooling C/D.
3. Freeze *new* matched/random candidate sets and title-shuffle maps **before** scoring, with explicit exposure/overlap logs. This script does **not** perform step 3; old Stage7 scripts require new cohort-compatible adaptations.
4. Score true and 20 null title contexts with a single frozen 101-candidate first-token set per paper, same 7 layers, J-Lens and Vanilla. True−Null is computed within paper; A−B within pair.
5. Primary test: 7-layer-integrated A−B Title Advantage, pair bootstrap. Separate independent test: positive title-specific association. L56 is a pilot-selected *secondary* endpoint. Low citation 0–2 vs high 129+ requires group-stratified analysis. Multiple per-layer tests adjusted (Holm).
6. Keep separate full-author Conditional JMRR and first-token name-free readout. Never identify them as equivalent.

## Files and commands

From Windows PowerShell upload `351_stage8.py` via `scp` to Explorer home directory.

On Explorer login node with activated `jlens` environment:

```bash
python -m py_compile ~/351_stage8.py
python ~/351_stage8.py freeze
python ~/351_stage8.py audit
```

The default destination is `/scratch/$USER/jlens/351_stage8/` with frozen `cohort/stage8_papers.csv`, `matching/stage8_ab_pairs.csv`, `config/analysis_plan.json`, `config/manifest.json`, and `summary/matching_audit.json`. Repeated `freeze`/`audit` verifies all SHA-256 hashes and refuses silent mutation.

**Real-data local dry run:** using the actual archived 6,841-paper Stage5 manifest, produced 100 A/B pairs = 200 targets, with 25 low (`0–2`), 50 middle (`3–128`), and 25 high (`129+`) pairs, excluding all 50 pilot target papers. `audit` passed. These are *candidate targets for future validation*, not model scores or findings.

## Constraints and boundaries

- Sampling is deterministic greedy nearest matching **within exact field and citation bin** (year and author count minimized; disjoint listed author names; no replacement). This is not globally optimal matching; balance is audited and must be scrutinized before freezing scoring protocols.
- Although Stage 8 *target IDs* are untouched by the 50-paper pilot, the public J-Lens and the original 6,841-paper input source are shared; this is an independent target-paper holdout, **not full data-source or model independence**.
- Pilot-specific effects in L56 must not be used to adjust Stage 8 matching or measure definitions.
- The present freeze does not run GPU or build 100 false authors/20 shuffle controls. Do not run previous Stage7.2/7.3 50-paper GPU scripts directly on Stage8 outputs.
- If Stage8 targets were previously used to fit/tune a self-fit lens, it is **not** an independent validation of that lens. Such overlaps require exclusion or separately reported analysis.
