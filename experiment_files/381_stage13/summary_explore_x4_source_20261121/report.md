# X4 L8 surname signal: where does it come from? — exploratory (post hoc, not pre-registered)

1178 X4 papers (Stage 11 sample with a cached partner); cohort 9,108 titles for embeddings/text models; team bootstrap 2000 draws (seed 1121), teams = pairs.parquet. Qwen D = mean over answer tokens of log10(1/rank), self source − partner source, source = last title token (cached raw/b2_pscope). Reproduction of published D: all L8 +0.0484 (pub +0.0484), surname-first L8 +0.0663 (pub +0.0663), all L40 +0.0694 (pub +0.0694).

## 1. Topic-matched partners

Cached partner = same field, same title token count, no shared surname (random within those). Topic-matched = same field, highest title cosine, other author team, no shared surname.

| embedding | cos(A, cached partner) mean [p10, p90] | cos(A, topic partner) mean [p10, p90] | share of cached partners at least as close as the median topic partner |
|---|---|---|---|
| bert | 0.225 [-0.026, 0.478] | 0.632 [0.498, 0.759] | 0.023 |
| mpnet | 0.102 [-0.028, 0.254] | 0.528 [0.422, 0.647] | 0.003 |

**Qwen D with the topic-matched partner is not computable from cache** (it needs A's answer scored from the topic partner's state). Cost of the direct run: per paper one authors-prompt forward of the partner (7 layers recorded) + 3 targets × 1 position × 7 patched layers (batched) — about 45 s per 50-paper shard on one A100-80GB (cached X4 runs: 63–85 s per shard for self + partner, two positions); 24 shards × 2 embeddings ≈ 0.6 GPU-h + model loading ≈ 1 GPU-h total. Not run.

### Proxy: Qwen D against how similar the cached partner already is

Per-paper D regressed on cos(A, cached partner); slope with team CI; "D at topic similarity" = intercept + slope × mean topic-partner cosine (extrapolation beyond most of the observed range; a model-based proxy, not a measurement).

| D | embedding | low tercile | mid | high tercile | slope per 0.1 cos [CI] | D at mean topic cos [CI] |
|---|---|---|---|---|---|---|
| author_surname_first@8 | bert | +0.0348 | +0.0761 | +0.0881 | +0.0086 [-0.0022, +0.0202] | +0.1015 [+0.0487, +0.1559] |
| author_surname_first@8 | mpnet | +0.0367 | +0.0958 | +0.0664 | +0.0080 [-0.0109, +0.0260] | +0.1003 [+0.0179, +0.1797] |
| author_all@8 | bert | +0.0509 | +0.0474 | +0.0470 | -0.0022 [-0.0073, +0.0027] | +0.0394 [+0.0172, +0.0608] |
| author_all@8 | mpnet | +0.0381 | +0.0627 | +0.0445 | +0.0009 [-0.0071, +0.0085] | +0.0522 [+0.0173, +0.0853] |
| author_surname_first@40 | bert | +0.1027 | +0.1384 | +0.1318 | +0.0046 [-0.0057, +0.0160] | +0.1432 [+0.0902, +0.1996] |
| author_surname_first@40 | mpnet | +0.1086 | +0.1417 | +0.1226 | -0.0022 [-0.0191, +0.0146] | +0.1150 [+0.0368, +0.1928] |
| author_all@40 | bert | +0.0678 | +0.0677 | +0.0727 | -0.0005 [-0.0044, +0.0036] | +0.0672 [+0.0484, +0.0875] |
| author_all@40 | mpnet | +0.0616 | +0.0820 | +0.0646 | -0.0014 [-0.0077, +0.0049] | +0.0635 [+0.0358, +0.0910] |
| year_informative@40 | bert | +0.0289 | +0.0177 | +0.0163 | -0.0030 [-0.0068, +0.0008] | +0.0089 [-0.0090, +0.0263] |
| year_informative@40 | mpnet | +0.0230 | +0.0182 | +0.0218 | -0.0039 [-0.0102, +0.0023] | +0.0044 [-0.0239, +0.0322] |
| year_all@40 | bert | +0.0134 | +0.0088 | +0.0085 | -0.0012 [-0.0028, +0.0005] | +0.0054 [-0.0021, +0.0130] |
| year_all@40 | mpnet | +0.0115 | +0.0087 | +0.0106 | -0.0016 [-0.0043, +0.0012] | +0.0035 [-0.0088, +0.0157] |

## 2. Text-only baseline in the same design

Logistic regression from title features (bert-base-uncased mean-pooled; TF-IDF 1–2-gram SVD-300) to the first author's surname-first / given-first Qwen token and to the publication year (classes seen ≥ 5 times, rest OOV), 5 folds by author team, C = 0.03 (as x4_textbase2). D_text = log10 p(answer | own title) − log10 p(answer | partner title), units log10 p.

### Positive control (held-out log-likelihood vs frequency prior)

| features | target | n | model | prior | gain |
|---|---|---|---|---|---|
| bert | surname_first | 9108 | -3.368 | -3.127 | -0.241 |
| bert | given_first | 2442 | -3.172 | -2.974 | -0.197 |
| bert | year | 9108 | -1.901 | -1.678 | -0.223 |
| tfidf_svd | surname_first | 9108 | -3.309 | -3.127 | -0.182 |
| tfidf_svd | given_first | 2442 | -3.105 | -2.974 | -0.131 |
| tfidf_svd | year | 9108 | -1.914 | -1.678 | -0.236 |

### D_text by partner type (mean [team CI]; mean/sd)

| features | answer | cached partner | topic partner (bert) | topic partner (mpnet) |
|---|---|---|---|---|
| bert | surname_first | +0.0513 [+0.0124, +0.0896]; +0.08 | +0.0080 [-0.0222, +0.0363]; +0.02 | +0.0513 [+0.0178, +0.0862]; +0.09 |
| bert | given_first | +0.0879 [+0.0183, +0.1569]; +0.13 | +0.0668 [+0.0219, +0.1141]; +0.15 | +0.0376 [-0.0144, +0.0929]; +0.07 |
| bert | year | +0.1318 [+0.0880, +0.1811]; +0.16 | +0.0609 [+0.0259, +0.0973]; +0.10 | +0.0730 [+0.0316, +0.1148]; +0.10 |
| tfidf_svd | surname_first | +0.0207 [-0.0100, +0.0528]; +0.04 | -0.0188 [-0.0456, +0.0111]; -0.04 | +0.0166 [-0.0125, +0.0463]; +0.03 |
| tfidf_svd | given_first | +0.0062 [-0.0479, +0.0607]; +0.01 | -0.0204 [-0.0653, +0.0250]; -0.05 | +0.0306 [-0.0134, +0.0733]; +0.08 |
| tfidf_svd | year | +0.0691 [+0.0256, +0.1120]; +0.09 | +0.0325 [-0.0080, +0.0737]; +0.04 | +0.0582 [+0.0192, +0.0982]; +0.08 |

### Standardised comparison, cached partner (Qwen units log10(1/rank), text units log10 p, so compare mean/sd; difference with team CI)

| Qwen D | text D | Qwen mean/sd | text mean/sd | Qwen − text [CI] |
|---|---|---|---|---|
| author_surname_first@8 | text bert surname_first | +0.180 | +0.076 | +0.104 [+0.029, +0.180] |
| author_surname_first@40 | text bert surname_first | +0.303 | +0.076 | +0.227 [+0.160, +0.298] |
| author_given_first@8 | text bert given_first | +0.088 | +0.130 | -0.042 [-0.181, +0.098] |
| year_informative@40 | text bert year | +0.158 | +0.163 | -0.005 [-0.082, +0.072] |
| year_all@40 | text bert year | +0.179 | +0.163 | +0.016 [-0.060, +0.090] |
| year_informative@8 | text bert year | +0.059 | +0.163 | -0.104 [-0.189, -0.027] |

## 3. Target − control within citation bins (team CI)

| measure | L8 | L16 | L24 | L32 | L40 | L48 |
|---|---|---|---|---|---|---|
| Qwen author_all | +0.0403 [+0.0222, +0.0589] | +0.0425 [+0.0252, +0.0599] | +0.0499 [+0.0321, +0.0661] | +0.0552 [+0.0362, +0.0729] | +0.0603 [+0.0427, +0.0773] | +0.0233 [+0.0157, +0.0305] |
| Qwen author_surname_first | +0.0834 [+0.0417, +0.1252] | +0.1002 [+0.0564, +0.1442] | +0.1179 [+0.0721, +0.1620] | +0.1245 [+0.0781, +0.1711] | +0.1465 [+0.0991, +0.1933] | +0.0443 [+0.0252, +0.0622] |
| Qwen author_given_first | +0.0363 [-0.0080, +0.0841] | +0.0491 [+0.0093, +0.0898] | +0.0354 [-0.0076, +0.0792] | +0.0406 [-0.0043, +0.0891] | +0.0367 [-0.0110, +0.0881] | +0.0329 [-0.0009, +0.0679] |
| Qwen author_initial_first | +0.0088 [-0.0138, +0.0318] | -0.0051 [-0.0271, +0.0172] | -0.0057 [-0.0272, +0.0154] | -0.0078 [-0.0293, +0.0141] | +0.0076 [-0.0117, +0.0295] | +0.0102 [-0.0038, +0.0242] |
| Qwen year_all | +0.0003 [-0.0066, +0.0071] | +0.0026 [-0.0037, +0.0091] | +0.0044 [-0.0024, +0.0114] | +0.0040 [-0.0032, +0.0107] | +0.0019 [-0.0048, +0.0090] | -0.0023 [-0.0074, +0.0029] |
| Qwen year_informative | +0.0006 [-0.0158, +0.0168] | +0.0078 [-0.0080, +0.0237] | +0.0110 [-0.0058, +0.0281] | +0.0095 [-0.0081, +0.0260] | +0.0047 [-0.0111, +0.0208] | -0.0045 [-0.0170, +0.0081] |
| Qwen field_all | +0.0092 [-0.0818, +0.1005] | -0.0219 [-0.1078, +0.0625] | -0.0325 [-0.1131, +0.0489] | -0.0402 [-0.1139, +0.0299] | -0.0348 [-0.0999, +0.0315] | +0.0059 [-0.0343, +0.0448] |

| text D (layer-free) | cached partner | topic (bert) | topic (mpnet) |
|---|---|---|---|
| bert surname_first | +0.0281 [-0.0465, +0.1065] | +0.0169 [-0.0453, +0.0817] | +0.0345 [-0.0338, +0.1046] |
| bert given_first | -0.0184 [-0.1703, +0.1306] | -0.1272 [-0.2225, -0.0277] | -0.0078 [-0.1263, +0.1144] |
| bert year | -0.0793 [-0.1710, +0.0121] | -0.0789 [-0.1513, -0.0054] | +0.0148 [-0.0690, +0.1004] |
| tfidf_svd surname_first | +0.0167 [-0.0487, +0.0839] | +0.0283 [-0.0358, +0.0898] | +0.0288 [-0.0346, +0.0904] |
| tfidf_svd given_first | +0.0457 [-0.0600, +0.1457] | +0.0434 [-0.0428, +0.1306] | +0.0542 [-0.0262, +0.1317] |
| tfidf_svd year | -0.0991 [-0.1903, -0.0076] | -0.0667 [-0.1484, +0.0181] | -0.0548 [-0.1422, +0.0283] |

## 4. Literal overlap

Rules: (a) a word of the title equals an author surname (lower-case, ≥ 3 letters); (b) the first author's surname-first Qwen token id, or its stripped lower-case string (≥ 3 chars), occurs among the title's Qwen tokens (title tokenised with and without a leading space); (c) eponym: a capitalised non-initial title word of ≥ 4 letters that is a surname somewhere in the 9,108-paper cohort and never appears lower-case in any cohort title, or a possessive "Xxx's", or a capitalised hyphen pair "Xxx-Yyy".

Counts: (a) 0, (b) 8, (c) 99, any 104 of 1178.

| D | all papers | without (a) | without (a)+(b) | without (a)+(b)+(c) | T−C without (a)+(b)+(c) | D among flagged (any) |
|---|---|---|---|---|---|---|
| author_surname_first@8 | +0.0663 [+0.0454, +0.0884] | +0.0663 [+0.0454, +0.0884] | +0.0667 [+0.0456, +0.0890] | +0.0640 [+0.0420, +0.0871] | +0.0813 [+0.0381, +0.1256] | +0.0908 [+0.0140, +0.1733] |
| author_all@8 | +0.0484 [+0.0396, +0.0576] | +0.0484 [+0.0396, +0.0576] | +0.0483 [+0.0393, +0.0575] | +0.0469 [+0.0379, +0.0566] | +0.0409 [+0.0224, +0.0602] | +0.0647 [+0.0313, +0.1015] |
| author_surname_first@40 | +0.1243 [+0.1017, +0.1485] | +0.1243 [+0.1017, +0.1485] | +0.1245 [+0.1017, +0.1490] | +0.1218 [+0.0981, +0.1472] | +0.1528 [+0.1046, +0.2029] | +0.1510 [+0.0837, +0.2235] |
| author_all@40 | +0.0694 [+0.0604, +0.0784] | +0.0694 [+0.0604, +0.0784] | +0.0689 [+0.0600, +0.0779] | +0.0672 [+0.0579, +0.0765] | +0.0612 [+0.0425, +0.0798] | +0.0920 [+0.0609, +0.1261] |

## 5. Readout difficulty

No-patch score = the target prompt with the literal "X" (raw/b2_pscope none_*); partner score = A's answer read from another paper's state (a non-paper-specific source). Per-paper means of log10(1/rank) over answer tokens.

| answer | no-patch mean (sd) | partner L8 mean (sd) | partner L40 mean (sd) | D/sd L8 | D/sd L40 | win L8 | win L40 |
|---|---|---|---|---|---|---|---|
| author_all | -1.321 (0.410) | -1.267 (0.401) | -1.301 (0.407) | +0.312 | +0.449 | 0.615 | 0.677 |
| author_surname_first | - | -2.130 (1.026) | -2.152 (1.028) | +0.180 | +0.303 | 0.578 | 0.610 |
| year_all | -0.200 (0.080) | -0.177 (0.080) | -0.182 (0.080) | +0.067 | +0.179 | 0.518 | 0.547 |
| year_informative | - | -0.391 (0.179) | -0.406 (0.185) | +0.059 | +0.158 | 0.517 | 0.537 |
| field_all | -1.659 (0.540) | -1.292 (0.756) | -1.175 (0.535) | +0.060 | +0.014 | 0.526 | 0.503 |

Year answer tokens (position j in " YYYY"; partner-source mean log10(1/rank) and D, L8 / L40):

| j | partner L8 | D L8 | partner L40 | D L40 |
|---|---|---|---|---|
| 0 | +0.000 | +0.0000 | +0.000 | +0.0000 |
| 1 | -0.097 | +0.0031 | -0.096 | +0.0095 |
| 2 | -0.003 | -0.0003 | -0.000 | -0.0003 |
| 3 | -0.203 | +0.0062 | -0.196 | +0.0285 |
| 4 | -0.580 | +0.0106 | -0.617 | +0.0135 |

Standardised D per layer (mean/sd) and earliest layer with a team CI above 0 (all papers):

| answer | L8 | L16 | L24 | L32 | L40 | L48 | L56 | earliest |
|---|---|---|---|---|---|---|---|---|
| author_surname_first | +0.18 | +0.22 | +0.25 | +0.25 | +0.30 | +0.23 | +0.04 | 8 |
| author_all | +0.31 | +0.35 | +0.37 | +0.37 | +0.45 | +0.37 | +0.06 | 8 |
| year_informative | +0.06 | +0.02 | +0.07 | +0.10 | +0.16 | +0.15 | +0.04 | 24 |
| year_all | +0.07 | +0.04 | +0.08 | +0.11 | +0.18 | +0.16 | +0.04 | 8 |
| field_all | +0.06 | +0.07 | +0.06 | +0.02 | +0.01 | +0.01 | +0.01 | 8 |

Label: exploratory (post hoc, not pre-registered). Single model; partners are the cached X4 partners unless stated; text models are fit on the cohort excluding the held-out fold of A's team (the partner may be in training).
