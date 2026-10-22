# Run `2026-10-15_qwen3-32b_v3_pilot` -- label (plan v3 step 2): recall level, multiple-choice outcome, group

Written by the code (`elm.stages.label.report`). Settings, checks and `checks_passed` are in `run.json`, the thresholds in `rules.yaml`.

## Result in 3 sentences

1. Of 9108 papers, 214 are recalled (R2, guard), 5680 are targets (held but not recalled; 4826 strong), 2220 are controls and 994 are excluded (0 of them without a complete multiple choice); under the tightened rule 4621 targets, 2220 controls, 2053 excluded. No gap run: the margins are empty.
2. The floor bin 0-2 (796 papers) has a pass rate of 38.6% against a maximum of 10.0% (25.5% under the tightened rule; over its 793 R0/R1 papers 38.3%): even the tightened labels exceed it (the split refuses both group columns unless --allow-failed-floor-check); both labels are written.
3. 98.1% of the 214 guard papers pass the multiple choice (minimum 90.0%): check passed; 0.0% of the 36432 orders have a letter mass below 0.5 (maximum 10.0%): check passed; checks_passed = true. team_b orders: 0.0% of 2000 below the letter mass. Second draw of the false lists for 500 papers (500 compared): the pass label agrees for 83.6% (kappa 0.63), 48.4% strong under both.

## Files

| File | One line / row is |
|------|-------------------|
| `paper_labels.csv` | one paper (both labels: plain, and `_tight` under the tightened rule) |
| `bin_table.csv` | one citation bin (last row `all`) |
| `rules.yaml` | the thresholds used |

### Columns of `paper_labels.csv`

| Column | Meaning |
|--------|---------|
| `paper_id`, `citation_bin`, `field` | The paper (from data/prepared/papers_9108.csv). |
| `recall_level` | From the unsteered open answer: R0 = no true author named (m = 0); R1 = some named but HR2 above the threshold; R2 = HR2 at or below it (mostly right). |
| `m`, `h`, `u`, `hr2`, `fa1` | The open answer's scores copied from the filter run (matched, hallucinated, unretrieved, HR2, first name = first true author). |
| `first_is_any_true` | 1 if the first name written matches any true author. |
| `mc_team_a` | Orders (0-4) of the team multiple choice in which the true list's letter has the highest probability and the letter mass is at least letter_mass_min. |
| `mc_team_p_true`, `mc_team_p_min` | Mean and lowest probability of the true letter over the orders. |
| `mc_team_margin` | Mean over orders of (true letter's probability - the best false option's). |
| `mc_team_consistent_wrong` | True if the same false team was chosen in at least 3 orders. |
| `mc_team_mass_min` | Lowest sum of the four letters' probabilities over the orders (a missing or NaN mass is left out and never counts as enough). |
| `mc_team_n_ties` | Orders whose highest letter probability is shared by two letters: no choice (not won, and no false team chosen for consistent_wrong). |
| `mc_n_orders`, `mc_n_low_mass`, `mc_orders_complete` | The team orders read, those whose letter mass is below letter_mass_min (or unknown), and whether exactly 4 distinct orders are there. |
| `mc_team_outcome` | Plain rule: strong (a = 4), pass (a >= 3), uncertain (a = 2) or fail (a <= 1); incomplete when the paper does not have exactly 4 distinct team orders (no outcome). |
| `margin_pos1`, `margin_all`, `margin_any_first`, `own_margin` | From the gap run (empty without one): log p of the true first author minus the mean over 19 real teams of their first author's; the same averaged over every position; the best single true author as first name; true first author minus the model's own first name. |
| `n_false_lists` | The real teams the margins average over (19 unless the paper's pool was short; 0 without candidate rows; empty without a gap run). |
| `group` | Plain rule: guard = R2; target = R0/R1 and a pass; control = R0/R1 and fail; excluded = uncertain or incomplete. |
| `mc_team_outcome_tight`, `group_tight` | The same two labels under the tightened rule (a pass needs a = 4 and p_true >= tightened.min_p_true; a = 2 or 3 is uncertain). Always written; preferred when the floor check is exceeded (run.json -> checks.floor). |
| `mc_team_b_a`, `mc_team_b_p_true` | The second draw of the false lists (kind team_b, the sampled papers; empty without one): orders won and mean probability of the true letter. |
| `mc_team_b_outcome` | Plain rule on the second draw; incomplete without its 4 orders; empty without a second draw. |
| `pass_agree` | both / one / neither: the paper passes under both draws, under one of them, under neither (empty unless both outcomes are complete). |
| `strong_both` | True if a = 4 under both draws (strong under both); empty like pass_agree. |
| `group_both` | The same verdict under both draws: target when both pass, control when both fail (a <= 1), guard for a recalled paper (R2) whatever the draws say, excluded otherwise; empty without a comparison. The group of a paper stays the first draw's. |
| `mc_coauthor_a`, `mc_coauthor_p_true` | The coauthor multiple choice (the true list vs three lists that each replace the same author by a real co-author of the first author; empty without an item): orders won and mean probability of the true letter. |
| `mc_coauthor_outcome` | Plain rule on the coauthor orders (strong, pass, uncertain, fail; incomplete without exactly 4 distinct orders); empty without an item. |
| `knows_full_list` | True for a target paper that also passes the coauthor question, False for a target paper whose complete coauthor outcome does not pass; empty otherwise. It never changes the group. |
| `mc_coauthor_outcome_tight`, `knows_full_list_tight` | The same under the tightened rule (a = 4 and mean true-letter probability >= 0.5), the mark for the targets of group_tight. |

### Columns of `bin_table.csv`

| Column | Meaning |
|--------|---------|
| `bin`, `n` | Citation bin (last row `all`) and its papers. |
| `n_R0`, `n_R1`, `n_R2` | Papers per recall level. |
| `n_strong`, `n_pass`, `n_uncertain`, `n_fail`, `n_incomplete` | Papers per multiple-choice outcome (plain rule; incomplete = not exactly 4 distinct team orders). |
| `n_guard`, `n_target`, `n_control`, `n_excluded` | Papers per group (plain rule). |
| `pass_rate` | Share of complete papers with a passing outcome (strong or pass); the floor bin's value is the floor check. |
| `guard_pass_rate` | Share of complete guard (R2) papers that pass (the known-positive check); empty without guard papers. |
| `low_mass_share` | Share of multiple-choice orders whose letter mass is below letter_mass_min (the letter-mass check on the `all` row). |
| `n_strong_tight`, `n_pass_tight`, `n_uncertain_tight`, `n_fail_tight` | Papers per outcome under the tightened rule (incomplete is the same under both rules). |
| `n_guard_tight`, `n_target_tight`, `n_control_tight`, `n_excluded_tight` | Papers per group under the tightened rule (guard is the same under both rules). |
| `pass_rate_tight`, `guard_pass_rate_tight` | The two rates under the tightened rule. |
| `n_second_draw` | Papers with the second draw of the false lists (kind team_b). |
| `pass_agree_rate` | Share of the compared papers (both outcomes complete) whose pass label is the same under both draws (pass_agree both or neither); empty without compared papers. |
| `pass_kappa` | Cohen's kappa of the pass label between the two draws over the compared papers; empty when both labels are constant. |
| `strong_both_share` | Share of the compared papers that are strong (a = 4) under both draws. |
| `n_coauthor_items` | Papers of the bin with coauthor orders. |
| `coauthor_pass_rate` | Share of the complete coauthor outcomes that pass (strong or pass); empty without any. |
| `n_knows_full_list` | Target papers of the bin marked knows_full_list. |
| `knows_full_list_share` | That count over the target papers judged (with a complete coauthor outcome); empty without any. |
| `coauthor_pass_rate_tight`, `n_knows_full_list_tight` | The coauthor pass rate and the marked targets under the tightened rule. |

## Per-bin table

```
              n  n_R0  n_R1  n_R2  n_strong  n_pass  n_uncertain  n_fail  n_incomplete  n_guard  n_target  n_control  n_excluded  pass_rate  guard_pass_rate  low_mass_share  n_strong_tight  n_pass_tight  n_uncertain_tight  n_fail_tight  n_guard_tight  n_target_tight  n_control_tight  n_excluded_tight  pass_rate_tight  guard_pass_rate_tight  n_second_draw  pass_agree_rate  pass_kappa  strong_both_share  n_coauthor_items  coauthor_pass_rate  n_knows_full_list  knows_full_list_share  coauthor_pass_rate_tight  n_knows_full_list_tight
bin                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
0-2         796   783    10     3       203     104          137     352             0        3       304        352         137      0.386            1.000           0.000             203             0                241           352              3             200              352               241            0.255                  1.000             39            0.821       0.513              0.077                 0                 NaN                  0                    NaN                       NaN                        0
3-4         799   781    17     1       208     102          134     355             0        1       309        355         134      0.388            1.000           0.000             208             0                236           355              1             207              355               236            0.260                  1.000             39            0.795       0.556              0.154                 0                 NaN                  0                    NaN                       NaN                        0
5-8         800   784    16     0       237     107          124     332             0        0       344        332         124      0.430              NaN           0.000             237             0                231           332              0             237              332               231            0.296                    NaN             39            0.744       0.488              0.205                 0                 NaN                  0                    NaN                       NaN                        0
9-16        800   781    18     1       288     110          127     275             0        1       397        275         127      0.498            1.000           0.000             288             0                237           275              1             288              275               236            0.360                  0.000             39            0.769       0.541              0.333                 0                 NaN                  0                    NaN                       NaN                        0
17-32       800   771    28     1       329     136          101     234             0        1       464        234         101      0.581            1.000           0.000             328             0                238           234              1             327              234               238            0.410                  1.000             39            0.744       0.487              0.308                 0                 NaN                  0                    NaN                       NaN                        0
33-64       800   762    34     4       404     110          101     185             0        4       510        185         101      0.642            1.000           0.000             404             0                211           185              4             401              185               210            0.505                  0.750             39            0.769       0.521              0.282                 0                 NaN                  0                    NaN                       NaN                        0
65-128      800   755    43     2       443     109           83     165             0        2       550        165          83      0.690            1.000           0.001             443             0                192           165              2             441              165               192            0.554                  1.000             38            0.868       0.671              0.447                 0                 NaN                  0                    NaN                       NaN                        0
129-256     800   738    51    11       507      98           69     126             0       11       595        126          68      0.756            0.909           0.000             507             0                167           126             11             497              126               166            0.634                  0.909             38            0.789       0.465              0.447                 0                 NaN                  0                    NaN                       NaN                        0
257-512     800   711    68    21       551      87           57     105             0       21       619        105          55      0.798            0.905           0.000             551             0                144           105             21             533              105               141            0.689                  0.857             38            0.789       0.224              0.553                 0                 NaN                  0                    NaN                       NaN                        0
513-1024    800   659   103    38       640      67           39      54             0       38       670         53          39      0.884            0.974           0.000             640             0                106            54             38             603               53               106            0.800                  0.974             38            0.895       0.550              0.737                 0                 NaN                  0                    NaN                       NaN                        0
1025-2048   665   500   111    54       590      27           19      29             0       54       563         29          19      0.928            1.000           0.000             590             0                 46            29             54             539               29                43            0.887                  0.944             38            0.947       0.472              0.921                 0                 NaN                  0                    NaN                       NaN                        0
2049-4096   326   221    64    41       305       7            5       9             0       41       271          9           5      0.957            1.000           0.000             305             0                 12             9             41             264                9                12            0.936                  1.000             38            0.974       0.655              0.921                 0                 NaN                  0                    NaN                       NaN                        0
4097+       122    52    33    37       121       0            1       0             0       37        84          0           1      0.992            1.000           0.000             121             0                  1             0             37              84                0                 1            0.992                  1.000             38            0.974       0.000              0.947                 0                 NaN                  0                    NaN                       NaN                        0
all        9108  8298   596   214      4826    1064          997    2221             0      214      5680       2220         994      0.647            0.981           0.000            4825             0               2062          2221            214            4621             2220              2053            0.530                  0.953            500            0.836       0.627              0.484                 0                 NaN                  0                    NaN                       NaN                        0
```
