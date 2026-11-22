# Pre-registration addendum 23 — H1 format-locking layer at the ":" position

Status: LOCKED 2026-11-22 (user order 2026-11-22 "立即跑"). Written before any real-model data of this test.
Code: ~/jlens_work/18_h1lock/ (frozen Stage 10/11/13 scripts imported read-only). Output: 391_groups/summary_a23/.

## 1. Question
H1 says the ":" position (and the name positions) carry the task/format. At which layer is the answer FORMAT (which question
was asked: authors / year / field) fixed in the ":" residual, so that later layers no longer need to read it from the prompt?

Why not CPU only: decoding the question from the stored ":" state is trivially ~100% at every layer (the question words are
in the prompt); decodability does not show when the format is fixed. That needs interventions (patching, knockout).

## 2. Sample and prompts
The 582 X1/M3 test papers (`381_stage13/config/pairs.parquet`, split = test; 288 target, 294 control) — the same papers as
X1/X5, so the results are comparable. Prompts = the M3 templates (`381_stage13.py` lines 48–50), true title, no year:
authors `Who are the authors of the paper titled "{t}"?\nAuthors:`, year `In what year was the research paper titled "{t}"
published?\nYear:`, field `In what research field is the paper titled "{t}"?\nField:`. Last position = ":". Shards of 50
papers (12 shards); the freeze file lists them.

## 3. Output measure at ":" (final model output, L63 logits → softmax over the full vocabulary)
Three format classes of next tokens, fixed now from the tokenizer and the cohort (overlaps removed from all classes):
- name: first token of every author name context in the cohort (space-prefixed name pieces);
- year: the bare space token (220) and the ten digit tokens (Qwen writes " 1999" as " ", "1", "9", "9", "9");
- field: first token of each of the 8 field labels, lower-case and capitalised, with and without a leading space.
Class mass m_c = sum of probabilities. Predicted format = argmax_c m_c. Format score for recipient question q against donor
question q′: F = ln m_class(q) − ln m_class(q′). Baseline accuracy = share of unpatched prompts whose predicted format matches
their own question (reported per task; a task with baseline accuracy < 0.90 is "not interpretable" for that task).

## 4. Interventions (layers L ∈ {4, 8, 16, 24, 32, 40, 48, 56}; block output of layer l)
(i) Colon patching: recipient = paper i under question q; donor = the same paper under q′ ≠ q (6 ordered pairs). At layer l
replace the recipient's ":" residual with the donor's ":" residual (only that position). Switch share S(l) = share of papers
whose predicted format becomes the donor's class; ΔF(l) = F(patched) − F(base) (negative = moves to the donor).
(ii) Knockout, primary ("isolated colon"): from layer l to the last layer the ":" query may attend only to itself (all other
keys masked). Retention K(l) = share of papers whose predicted format stays the recipient's own class; l = 64 = nothing
blocked (explicit-mask baseline). Secondary: from layer l the ":" query is blocked from the question positions only (every
prompt position that is neither a title token nor the ":" itself; includes the 9-token prefix, the words after the title and
the label word before ":"), title tokens visible.

## 5. Decision rules (fixed before any real-model data)
Per recipient task q (3 tasks), primary knockout: locked layer X_q = the smallest l in L such that K(l′) ≥ 0.95 with the
lower 95% CI bound ≥ 0.90 for every l′ ≥ l in L. CIs: team bootstrap (pairs.parquet team ids), 2,000 draws, seed 23.

| reading (per task) | condition |
|---|---|
| format fixed early | X_q ≤ 16 |
| fixed in the middle | 24 ≤ X_q ≤ 40 |
| fixed only late | X_q ∈ {48, 56} |
| never fully fixed at the colon | no X_q (K(l) < 0.95 or CI lower < 0.90 at L56): the format keeps being re-read from the prompt |
| odd / not interpretable | baseline accuracy < 0.90, or K(64) < 0.95 (explicit-mask baseline broken) |

Overall H1 statement = the per-task readings; if all three agree, "the answer format is fixed at the colon by layer max X_q".
Corroboration (reported, no verdict of its own): the smallest l from which S(l) ≥ 0.95 for every later l (per ordered
pair); the secondary knockout K₂(l); target vs control difference of K(l) and S(l) (within the 582 papers, team CI).

## 6. Checks (WARN only, never stop)
Patching the recipient with its own ":" state reproduces the base output (max |Δ logit| ≤ 0.5); K(64) with the explicit mask
vs no mask: predicted format identical for ≥ 0.99 of papers; class vocabularies disjoint (asserted).

## 7. Cost and order
CPU precheck → tiny random-model test → 1 real-model shard (50 papers) for cost → remaining shards (+ CPU gate that checks
the freeze's full shard list, resubmits missing shards ≤ 4 rounds, then runs the analysis). Estimate ≈ 1 GPU-h.

## 8. Limitations stated in advance
Single model; only the ":" position; format measured by three token classes of the first answer token; the isolated-colon
knockout removes all context (including attention-sink keys) and may push states off-distribution — that is why the
secondary knockout and the patching are reported alongside; 582 papers.
