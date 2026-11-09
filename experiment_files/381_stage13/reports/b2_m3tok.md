# Addendum 12 item 2-10: M3 task runs scored on all name tokens of all authors

Written 2026-11-09 04:56 by `13_stage13/stage13_b2B_analyze.py m3tok`. Plan: `381_stage13/config/prereg_addendum12.json` (sha256 OK). Raw: `/scratch/zhang.zhiqi2/jlens/381_stage13/raw`.

M3 authors prompt `Who are the authors of the paper titled "{t}"?\nAuthors:` (no year), every author context of every cohort paper, teacher-forced, log10(1/rank) of every name token at the model output (batch 1, as score_tf). Paper scores: m3_alltok = mean over all name tokens of all authors (primary; Stage 10 averaging); m3_authormean = mean over authors of their token means; m3_first_alltok = first author all tokens; m3_firsttok_allauthors = first token of every author; m3_first_first = first author first token inside its name forward; m3_first_exact = the same token by the exact published prompt-only forward (hard check); m3_role_* = tokens of one role.

In-sequence first token (m3_first_first) vs the same published cells, WARN only: max |diff| 9.0e-04 (threshold 0.005) -> OK; per paper {'n': 9108, 'mean_abs': 0.003989130165148209, 'max_abs': 0.3010299956639812, 'share_exact': 0.8987703118137901}.
HARD CHECK (m3_first_exact = exact published prompt-only path, reproduces the published m3_scores_summary.csv author_first_nlr cells; threshold 0.005): max |diff| 2.2e-16 over 9/9 cells -> **PASS**.
Per paper, exact arm (WARN only): {'n': 9108, 'mean_abs': 7.030924907815e-17, 'max_abs': 8.881784197001252e-16, 'share_exact': 1.0}.

## Means by cohort group

| score | all | target | control | guard | excluded |
|---|---|---|---|---|---|
| m3_first_exact | -1.1736 (n 9108) | -1.1427 (n 4621) | -1.2705 (n 2220) | -0.5484 (n 214) | -1.2034 (n 2053) |
| m3_first_first | -1.1736 (n 9108) | -1.1427 (n 4621) | -1.2706 (n 2220) | -0.5475 (n 214) | -1.2037 (n 2053) |
| m3_first_alltok | -0.8248 (n 9108) | -0.7089 (n 4621) | -1.0303 (n 2220) | -0.2219 (n 214) | -0.9266 (n 2053) |
| m3_alltok | -0.8195 (n 9108) | -0.7212 (n 4621) | -1.0018 (n 2220) | -0.3435 (n 214) | -0.8935 (n 2053) |
| m3_authormean | -0.8474 (n 9108) | -0.7505 (n 4621) | -1.0267 (n 2220) | -0.3500 (n 214) | -0.9235 (n 2053) |
| m3_firsttok_allauthors | -1.1826 (n 9108) | -1.1587 (n 4621) | -1.2560 (n 2220) | -0.8722 (n 214) | -1.1891 (n 2053) |
| m3_role_initial | -0.9152 (n 8464) | -0.9197 (n 4413) | -0.9180 (n 1972) | -0.8067 (n 202) | -0.9135 (n 1877) |
| m3_role_given_first | -1.9860 (n 4202) | -2.0003 (n 2149) | -2.0615 (n 1014) | -1.0157 (n 66) | -1.9415 (n 973) |
| m3_role_given_cont | -0.7296 (n 2978) | -0.6594 (n 1433) | -0.8450 (n 762) | -0.1771 (n 34) | -0.7717 (n 749) |
| m3_role_surname_first | -1.5994 (n 9108) | -1.4253 (n 4621) | -1.9223 (n 2220) | -0.4219 (n 214) | -1.7651 (n 2053) |
| m3_role_surname_cont | -0.3769 (n 8109) | -0.2557 (n 4312) | -0.6151 (n 1822) | -0.0444 (n 186) | -0.4610 (n 1789) |

## Target - control within citation bin (team CI primary; paper CI beside it)

| score | papers | estimate | team CI | paper CI | bins |
|---|---|---|---|---|---|
| m3_first_exact | all cohort target/control | +0.1470 | [+0.0955, +0.1906] | [+0.0986, +0.1905] | 10 |
| m3_first_first | all cohort target/control | +0.1469 | [+0.0959, +0.1906] | [+0.0978, +0.1901] | 10 |
| m3_first_alltok | all cohort target/control | +0.2434 | [+0.2182, +0.2673] | [+0.2184, +0.2685] | 10 |
| m3_alltok | all cohort target/control | +0.2342 | [+0.2153, +0.2524] | [+0.2164, +0.2524] | 10 |
| m3_authormean | all cohort target/control | +0.2314 | [+0.2119, +0.2498] | [+0.2127, +0.2504] | 10 |
| m3_firsttok_allauthors | all cohort target/control | +0.1360 | [+0.1012, +0.1675] | [+0.1013, +0.1701] | 10 |
| m3_role_initial | all cohort target/control | +0.0283 | [+0.0027, +0.0514] | [+0.0038, +0.0511] | 10 |
| m3_role_given_first | all cohort target/control | +0.1319 | [+0.0685, +0.1925] | [+0.0721, +0.1904] | 9 |
| m3_role_given_cont | all cohort target/control | +0.1924 | [+0.1310, +0.2556] | [+0.1305, +0.2565] | 9 |
| m3_role_surname_first | all cohort target/control | +0.3617 | [+0.3109, +0.4123] | [+0.3163, +0.4063] | 10 |
| m3_role_surname_cont | all cohort target/control | +0.2613 | [+0.2313, +0.2895] | [+0.2319, +0.2904] | 10 |
| m3_first_exact | Stage 11 sample (1,186) | +0.1701 | [+0.0767, +0.2582] | [+0.0824, +0.2653] | 10 |
| m3_first_first | Stage 11 sample (1,186) | +0.1703 | [+0.0767, +0.2587] | [+0.0826, +0.2659] | 10 |
| m3_first_alltok | Stage 11 sample (1,186) | +0.2754 | [+0.2298, +0.3219] | [+0.2291, +0.3219] | 10 |
| m3_alltok | Stage 11 sample (1,186) | +0.2481 | [+0.2166, +0.2839] | [+0.2140, +0.2806] | 10 |
| m3_authormean | Stage 11 sample (1,186) | +0.2503 | [+0.2178, +0.2877] | [+0.2152, +0.2840] | 10 |
| m3_firsttok_allauthors | Stage 11 sample (1,186) | +0.1525 | [+0.0905, +0.2137] | [+0.0889, +0.2170] | 10 |
| m3_role_initial | Stage 11 sample (1,186) | +0.0551 | [+0.0114, +0.0981] | [+0.0097, +0.1040] | 10 |
| m3_role_given_first | Stage 11 sample (1,186) | +0.0781 | [-0.0351, +0.1885] | [-0.0323, +0.1896] | 10 |
| m3_role_given_cont | Stage 11 sample (1,186) | +0.1193 | [+0.0021, +0.2449] | [+0.0019, +0.2367] | 10 |
| m3_role_surname_first | Stage 11 sample (1,186) | +0.3865 | [+0.3012, +0.4812] | [+0.3009, +0.4768] | 10 |
| m3_role_surname_cont | Stage 11 sample (1,186) | +0.2340 | [+0.1792, +0.2880] | [+0.1770, +0.2875] | 10 |
| m3_first_exact | pairs.parquet tune | +0.0982 | [-0.0325, +0.2234] | [-0.0255, +0.2266] | 10 |
| m3_first_first | pairs.parquet tune | +0.0976 | [-0.0344, +0.2242] | [-0.0255, +0.2266] | 10 |
| m3_first_alltok | pairs.parquet tune | +0.2717 | [+0.2053, +0.3348] | [+0.2085, +0.3361] | 10 |
| m3_alltok | pairs.parquet tune | +0.2251 | [+0.1768, +0.2732] | [+0.1773, +0.2728] | 10 |
| m3_authormean | pairs.parquet tune | +0.2243 | [+0.1742, +0.2732] | [+0.1743, +0.2743] | 10 |
| m3_firsttok_allauthors | pairs.parquet tune | +0.1212 | [+0.0304, +0.2126] | [+0.0307, +0.2121] | 10 |
| m3_role_initial | pairs.parquet tune | -0.0186 | [-0.0859, +0.0489] | [-0.0863, +0.0482] | 10 |
| m3_role_given_first | pairs.parquet tune | +0.0957 | [-0.0545, +0.2420] | [-0.0525, +0.2475] | 9 |
| m3_role_given_cont | pairs.parquet tune | +0.0958 | [-0.1270, +0.3077] | [-0.1228, +0.3072] | 5 |
| m3_role_surname_first | pairs.parquet tune | +0.3762 | [+0.2375, +0.5056] | [+0.2546, +0.5147] | 10 |
| m3_role_surname_cont | pairs.parquet tune | +0.2290 | [+0.1527, +0.3032] | [+0.1565, +0.3060] | 10 |
| m3_first_exact | pairs.parquet test | +0.2600 | [+0.1257, +0.3991] | [+0.1301, +0.3936] | 10 |
| m3_first_first | pairs.parquet test | +0.2609 | [+0.1282, +0.3993] | [+0.1303, +0.3950] | 10 |
| m3_first_alltok | pairs.parquet test | +0.2798 | [+0.2147, +0.3479] | [+0.2132, +0.3486] | 10 |
| m3_alltok | pairs.parquet test | +0.2713 | [+0.2248, +0.3192] | [+0.2251, +0.3189] | 10 |
| m3_authormean | pairs.parquet test | +0.2753 | [+0.2278, +0.3245] | [+0.2264, +0.3238] | 10 |
| m3_firsttok_allauthors | pairs.parquet test | +0.1895 | [+0.0931, +0.2867] | [+0.0929, +0.2836] | 10 |
| m3_role_initial | pairs.parquet test | +0.1330 | [+0.0688, +0.1933] | [+0.0706, +0.1993] | 10 |
| m3_role_given_first | pairs.parquet test | +0.0556 | [-0.1155, +0.2276] | [-0.1135, +0.2275] | 10 |
| m3_role_given_cont | pairs.parquet test | +0.1064 | [-0.1853, +0.3854] | [-0.1747, +0.3912] | 3 |
| m3_role_surname_first | pairs.parquet test | +0.3892 | [+0.2575, +0.5152] | [+0.2659, +0.5167] | 10 |
| m3_role_surname_cont | pairs.parquet test | +0.2405 | [+0.1604, +0.3205] | [+0.1636, +0.3214] | 10 |

Full tables: summary_b2B/m3tok_perpaper.csv, m3tok_summary.csv.

## WARN

- none

