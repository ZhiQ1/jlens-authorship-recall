# Qwen3-32B recall and recognition labels for the 9,108 papers (2026-10-15)

Model: Qwen/Qwen3-32B, local bf16 weights, greedy decoding, on an A100 80GB (Explorer cluster).
These labels hold for this model only; another model needs its own run.

## Files

| File | What it is |
|---|---|
| `paper_labels_with_papers.csv` | One row per paper: title, year, citations, authors, plus every label column. Start here. |
| `label_README.md` | The meaning of every column in `paper_labels_with_papers.csv` and the checks. |
| `rules.yaml`, `bin_table.csv` | The thresholds used, and the counts per citation bin. |
| `open_results.jsonl` | Open question ("who wrote this paper?"): the model's answer text and its scores, one row per paper. |
| `mc_results.jsonl` | Multiple choice: one row per paper, kind and order, with the probability of each letter. |
| `mc_team.jsonl`, `mc_team_b.jsonl` | The 4 options shown for each paper (first draw: every paper; second draw: 500 sampled papers). |
| `step1_README.md` | How the open question and the multiple choice were asked. |

## The groups (column `group_tight` recommended, `group` also given)

- Open question: HR2 > 0.5 = cannot say the authors (R0: no true author named; R1: some, but more made up). HR2 <= 0.5 = R2.
- Multiple choice: the true author list against the real teams of 3 other papers (same field, similar team size,
  citation bin and year), asked in 4 orders. `mc_team_a` = orders right (0-4).
- `target` = cannot say the authors, but recognises the list (`group_tight`: 4 of 4 right and mean probability of
  the true letter >= 0.5).
- `control` = cannot say the authors and does not recognise the list (a <= 1).
- `guard` = says the authors (R2). `excluded` = in between.

## Caveats

1. In the low citation bins "recognised" is mostly a preference for one team: the 0-2 bin still has 25.5% targets
   under `group_tight`, about what a fixed team preference gives by chance (25%). Targets in high bins are more
   trustworthy. `strong_both` (4 of 4 right under two independent draws of the false lists) is cleaner but exists
   for the 500 sampled papers only.
2. High bins have few controls (4097+: 0, 2049-4096: 9, 1025-2048: 29), so target/control pairs within a bin run out there.
3. For first-author probes: `fa1 = 1` means the model's first written name already is the true first author
   (120 targets). Use `recall_level == "R0"` for papers where no true author was named at all.
