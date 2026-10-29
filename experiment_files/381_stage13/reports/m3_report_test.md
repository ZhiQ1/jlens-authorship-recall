# Stage 13 M3: is the title / colon state about the paper or about the question?

384 papers, 3 prompts per paper (authors, year, field), 5 group folds; 95% team-cluster bootstrap. **TEST RUN (3 shards, 2 layers)**
Rule (addendum 2): PRIMARY = transfer ratio T at L16-L40, also relative to T(L4); the identity index counts only as I(l) - I(L4).

## Transfer ratio T (train on one prompt, test on another, / within-prompt); average of 6 ordered pairs

### title_last

| layer | year | log citations | field | year: T - T(L4) | field: T - T(L4) | within-prompt year R², field acc |
|---|---|---|---|---|---|---|
| L4 | +0.995 [+0.829, +1.136] | -1.280 [-0.079, +2.025] | +1.017 [+0.998, +1.039] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | 0.044, 0.379 |
| L24 | +0.956 [+0.922, +0.980] | +0.936 [+0.836, +1.047] | +0.983 [+0.965, +1.002] | -0.039 [-0.185, +0.116] | -0.034 [-0.061, -0.009] | 0.267, 0.603 |

### colon

| layer | year | log citations | field | year: T - T(L4) | field: T - T(L4) | within-prompt year R², field acc |
|---|---|---|---|---|---|---|
| L4 | -22.008 [-91.860, -12.212] | -60.997 [-463.483, +384.143] | +0.328 [+0.297, +0.362] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | 0.141, 0.615 |
| L24 | -2.986 [-4.454, -2.244] | -9.346 [-13.936, -6.978] | +0.261 [+0.233, +0.288] | +19.022 [+9.772, +87.728] | -0.067 [-0.112, -0.026] | 0.378, 0.709 |

## Identity index (judged only relative to L4)

| layer | pos | I | I - I(L4) |
|---|---|---|---|
| L4 | title_last | +0.982 [+0.975, +0.988] | +0.000 [+0.000, +0.000] |
| L4 | colon | +0.753 [+0.748, +0.758] | +0.000 [+0.000, +0.000] |
| L24 | title_last | +0.970 [+0.964, +0.976] | -0.012 [-0.013, -0.011] |
| L24 | colon | +0.281 [+0.276, +0.286] | -0.472 [-0.478, -0.466] |

## Pre-registered reading (L16-L40)

- title_last, year: T at L16-L40 = L24 0.96 -> H2 (paper identity, T >= 0.8 throughout)
- title_last, log_citations: T at L16-L40 = L24 0.94 -> H2 (paper identity, T >= 0.8 throughout)
- title_last, field: T at L16-L40 = L24 0.98 -> H2 (paper identity, T >= 0.8 throughout)
- colon, year: T at L16-L40 = L24 -2.99 -> H1 (task-specific, T < 0.5 throughout)
- colon, log_citations: T at L16-L40 = L24 -9.35 -> H1 (task-specific, T < 0.5 throughout)
- colon, field: T at L16-L40 = L24 0.26 -> H1 (task-specific, T < 0.5 throughout)
