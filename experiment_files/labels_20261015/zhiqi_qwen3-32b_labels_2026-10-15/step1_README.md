# Run `2026-10-15_qwen3-32b_v3-measure-a100` -- filter, measure path (plan v3 step 1)

This file is written by the code (`elm.stages.filter.measure.report.write_readme`). Do not edit it by hand; all settings are in `run.json`.

## The question this run answers

For the model **Qwen/Qwen3-32B** (local weights): what does it write when asked openly for the authors of each paper (scored with the metric panel), and does it pick the true author list among the real teams of three other papers, in 4 orders of the options (kind `team_b`, when asked: the same with a second draw of the three teams, for the sampled papers; kind `coauthor`, when asked: three lists that each swap one author for a real co-author of the first author)? The label stage turns these rows into recall levels, outcomes and groups.

## Result in 3 sentences

1. Open question: the model gave the exact author list for 1.4% of the 9108 papers (mean HR2 0.97); its first name was the first true author for 3.4% and any true author for 5.1%; 0.5% refusals, 8.2% cut off.
2. Multiple choice (team: all 4 orders right for 53.2% (mean letter mass 1.00); team_b: all 4 orders right for 57.6% (mean letter mass 1.00)).
3. Of the 400 papers answered again at batch size 1, 45.5% gave another text (batching noise).

## The run in numbers

- Papers: 9108 | kinds: team, team_b | orders per kind: 4
- Rows: {'open': 9108, 'mc': {'team': 36432, 'team_b': 2000}, 'noise': 400} (expected {'open': 9108, 'noise': 400, 'mc': {'team': 36432, 'team_b': 2000}}; written twice: {'open': 0, 'noise': 0}) -> status: complete

## Files

| File | What it is | One row / line is |
|------|------------|-------------------|
| `run.json` | The run card: settings, expected and written counts, input and prompt files with their sha256, code version, torch / transformers versions and GPU. | |
| `README.md` | This file. | |
| `open_results.jsonl` | Every open answer with the metric panel. | one paper |
| `mc_results.jsonl` | Every multiple-choice order with its letter probabilities. | one paper x kind x order |
| `open_results_noise.jsonl` | The noise re-run: some papers answered again at another batch size (`changed` = the text differs). | one paper |
| `bin_table.csv` | Summary per citation bin (last row `all`). | one citation bin |

### Columns of `open_results.jsonl` (and of `open_results_noise.jsonl`, plus `changed`)

| Key | Meaning |
|-----|---------|
| `paper_id` | Paper id (as in `data/prepared/papers_9108.csv`). |
| `generated_text` | The model's raw answer to the open question (greedy, at most `max_new_tokens` tokens). |
| `finish_reason` | `stop` (the model wrote an end-of-turn token) or `length` (cut by the token limit). |
| `n_tokens` | Tokens of the answer before the end token. |
| `parse_class` | `clean_list`, `preamble`, `refusal`, `empty` or `cut_off` (metrics/panel.py). |
| `names` | The names found in the answer after the stripping, in order. |
| `m`, `h`, `u`, `hr2` | Matched, hallucinated, unretrieved and HR2 = (h + u) / (m + h + u) (shared metrics). |
| `fa1`, `first_is_any_true` | 1 if the first name written is the first true author / any true author. |
| `exact` | 1 if h = 0 and u = 0. |
| `n_names` | Number of names in the answer. |
| `own_first_name` | The first name written, as "initial. surname" (the gap stage scores it as a candidate); `null` without a name. |
| `batch_id` | The batch (of `batch_size` prompts) this answer was generated in. |

### Columns of `mc_results.jsonl`

| Key | Meaning |
|-----|---------|
| `paper_id` | Paper id. |
| `kind` | The multiple-choice kind: `team` (the three wrong options are the real author lists of other papers); `team_b` (a second, independent draw of those lists, asked for the sampled papers of `mc_team_b.jsonl` only); `coauthor` (three lists that each replace the same author, never the first, by a real co-author of the first author, asked for the papers of `mc_coauthor.jsonl`). |
| `order_index` | Which of the stored orders (0-3: ABDC, BCAD, CDBA, DACB over the canonical options). |
| `order` | The canonical option shown as A, B, C, D; 0 is the true list. `[1, 2, 0, 3]` means the true list was C. |
| `correct_label` | The letter of the true list in this order. |
| `probs` | Probability of each letter A-D from the next-token distribution at the answer position ("A" and " A" summed). |
| `mass` | The four probabilities summed; low = the model does not answer with a letter. |
| `chosen` | The letter with the highest probability. |
| `correct` | 1 if `chosen` is `correct_label`. |
| `letter_token_probs` | Each letter token alone, keyed by its text (`"A"`, `" A"`, ...), 6 significant digits. |
| `top_tokens` | The 5 most probable next tokens (`mc_top_tokens` in run.json), `[token id, text, probability]` (6 significant digits): what the model writes instead when the mass is low. |

### Columns of `bin_table.csv`

Explained in the Metrics table of `src/elm/stages/filter/README.md`.

## Sample prompts (complete, as sent to the model inside its chat template)

Paper: `e7f41e22fa4b626ed9a0a3f4a97cb7874aa2993e` -- true authors: S. Bree, S. Snoek, S. V. Diest, L. Elbers, F. Hilbers, Suzanne Duijst, J. Vliet, R. V. D. Wijngaard, C. Cailotto, W. Jonge, G. Boeckxstaens

### Kind `team`, order 0 -- one user message

```text
You are an academic assistant. Your task is to identify the correct author list for an academic paper. You will be given a paper title, its publication year, and four candidate author lists labelled A, B, C, and D. Exactly one is correct.

- Respond with a single letter: A, B, C, or D.
- Do not add any explanation, notes, or extra content.

Here are some examples:

Question: Which of the following is the author list of the paper titled 'Why men are at higher risk for hepatocellular carcinoma?' which was published in 2012?
A: V. Keng, D. Largaespada, A. Villanueva
B: M. Sherman, J. Bruix, A. Forner
C: J. Llovet, S. Ricci, V. Mazzaferro
D: H. El-Serag, K. Rudolph, A. Marrero
Answer: A

Question: Which of the following is the author list of the paper titled 'Research as an influence on teaching' which was published in 1984?
A: J. Centra
B: K. R. Jolls
C: P. Ramsden
D: M. Prosser
Answer: B

Now, answer the following question:
Question: Which of the following is the author list of the paper titled 'Novel Mast Cell Stabilizers in the Treatment of Postoperative Ileus' which was published in 2011?
A: S. Bree, S. Snoek, S. Diest, L. Elbers, F. Hilbers, S. Duijst, J. Vliet, R. Wijngaard, et al.
B: G. Clemente, C. Len, C. Silva, S. Sachetti, V. Ferriani, F. Sztajnbok, S. Oliveira, B. Bica, et al.
C: M. Nicoletto, R. Padrini, M. Palumbo, A. Ziade, R. Ragazzi, G. Pratesi, G. Artioli, M. de Cesare, et al.
D: A. Kowsar, I. Labioche, T. Arentz, M. Zimmerman, F. Georger, P. Defaye, P. Lagrange, L. Roy, et al.
Answer:
```

Correct: A | the model answered: C (letter mass 1.00)

### Open question -- a system message and a user message

```text
[system] You are a knowledgeable assistant. Answer factually and concisely. When asked for authors, return a semicolon separated list of full names only, with no additional text.
[user]   Who are the authors of the paper titled 'Novel Mast Cell Stabilizers in the Treatment of Postoperative Ileus' which was published in 2011? Return a semicolon separated list of author names only.
```

The model answered: `Cumhur; Cem; Mehmet; Zeynep; Emre; Ahmet` (clean_list, stop)
