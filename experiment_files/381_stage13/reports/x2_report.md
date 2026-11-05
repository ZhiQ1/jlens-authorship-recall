# Stage 13 X2: subspace patching (addendum 6)

Shards 24; pairs: test 582, tune 596 (equal title token length, as X1). Score = A's first-author teacher-forced score (mean log10(1/rank) of the name tokens); this is the model's internal preference for the correct first-author tokens under teacher forcing, not generation (addendum 4).
carry: R_S = mean(patched - corrupt) / mean(clean - corrupt), B's prompt with h_B + P_S(h_A - h_B) at every title position. remove: L_S = mean(clean - removed) / mean(clean - corrupt), A's prompt with h_A - P_S(h_A - mu). 95% team-cluster bootstrap (2,000 draws). S_rand = average of 3 random 10-dim subspaces (seeds 61-63). S_full = identity map (carry = X1 full replacement; remove = mu at every title position).

## Verdict (carry arm, layer chosen on tune, confirmed on test)

| subspace | layer (tune) | tune R_S - R_rand | test R_S - R_rand | test R_S | test R_rand | test R_full | carries? | remove arm test L_S - L_rand |
|---|---|---|---|---|---|---|---|---|
| S_id | L40 | +0.005 | +0.002 [-0.001, +0.005] | +0.005 | +0.003 | +0.920 | no | +0.001 [-0.003, +0.005] |
| S_auth | L48 | +0.015 | +0.015 [+0.010, +0.020] | +0.018 | +0.003 | +0.428 | yes | +0.001 [-0.004, +0.006] |

- H2 (S_id carries AND R_id >= 0.5 x R_full at L40): **not supported** (R_id +0.005 vs 0.5 x R_full +0.460).
- H3 (S_auth carries AND R_auth - R_id > 0 at L48): **supported** (R_auth - R_id on test +0.014 [+0.008, +0.020]; remove arm +0.000 [-0.005, +0.005]).
- Neither (no tune/test layer with R_id - R_rand or R_auth - R_rand above 0): **no**.

**Verdict: H3 supported (S_auth carries more than S_id)**

## carry arm: R_S (share of the clean - corrupt gap moved into B by patching A's S-component)

### test (confirmatory) - clean - corrupt 0.347, n 582

| layer | S_id | S_auth | S_rand (avg of 3) | S_full | S = 0 | id - rand | auth - rand | auth - id | id - 0.5 full |
|---|---|---|---|---|---|---|---|---|---|
| L16 | +0.003 [-0.000, +0.007] | +0.003 [-0.001, +0.007] | +0.002 [-0.001, +0.004] | +1.000 [+0.989, +1.010] | +0.002 [-0.002, +0.005] | +0.002 [-0.002, +0.005] | +0.001 [-0.003, +0.005] | -0.001 [-0.005, +0.004] | -0.496 [-0.503, -0.490] |
| L24 | +0.002 [-0.001, +0.006] | +0.002 [-0.002, +0.007] | +0.002 [-0.001, +0.005] | +0.992 [+0.978, +1.005] | +0.002 [-0.001, +0.005] | +0.000 [-0.003, +0.004] | +0.000 [-0.004, +0.005] | -0.000 [-0.005, +0.005] | -0.493 [-0.501, -0.486] |
| L32 | +0.005 [-0.000, +0.010] | +0.002 [-0.002, +0.007] | +0.002 [-0.001, +0.005] | +0.971 [+0.954, +0.988] | +0.000 [-0.003, +0.004] | +0.002 [-0.002, +0.007] | +0.000 [-0.005, +0.005] | -0.002 [-0.009, +0.004] | -0.481 [-0.490, -0.471] |
| L40 | +0.005 [+0.001, +0.009] | +0.014 [+0.009, +0.019] | +0.003 [+0.001, +0.006] | +0.920 [+0.895, +0.945] | +0.001 [-0.002, +0.004] | +0.002 [-0.001, +0.005] | +0.011 [+0.006, +0.016] | +0.009 [+0.004, +0.014] | -0.455 [-0.468, -0.442] |
| L48 | +0.004 [-0.000, +0.008] | +0.018 [+0.012, +0.024] | +0.003 [+0.000, +0.005] | +0.428 [+0.394, +0.462] | +0.002 [-0.001, +0.005] | +0.001 [-0.002, +0.004] | +0.015 [+0.010, +0.020] | +0.014 [+0.008, +0.020] | -0.210 [-0.227, -0.192] |

### tune - clean - corrupt 0.390, n 596

| layer | S_id | S_auth | S_rand (avg of 3) | S_full | S = 0 | id - rand | auth - rand | auth - id | id - 0.5 full |
|---|---|---|---|---|---|---|---|---|---|
| L16 | +0.003 [-0.001, +0.007] | +0.005 [+0.000, +0.009] | +0.003 [-0.000, +0.005] | +0.995 [+0.987, +1.003] | -0.000 [-0.004, +0.003] | +0.001 [-0.002, +0.004] | +0.002 [-0.001, +0.005] | +0.001 [-0.003, +0.005] | -0.494 [-0.500, -0.489] |
| L24 | +0.001 [-0.003, +0.005] | +0.003 [-0.003, +0.008] | +0.002 [-0.001, +0.004] | +0.993 [+0.982, +1.005] | +0.001 [-0.002, +0.004] | -0.001 [-0.005, +0.003] | +0.001 [-0.003, +0.006] | +0.002 [-0.003, +0.007] | -0.496 [-0.503, -0.489] |
| L32 | +0.000 [-0.004, +0.004] | +0.005 [+0.000, +0.009] | +0.003 [+0.000, +0.006] | +0.978 [+0.963, +0.994] | +0.001 [-0.003, +0.004] | -0.003 [-0.007, +0.001] | +0.002 [-0.002, +0.006] | +0.004 [-0.000, +0.010] | -0.489 [-0.497, -0.481] |
| L40 | +0.007 [+0.002, +0.011] | +0.013 [+0.007, +0.018] | +0.002 [-0.001, +0.004] | +0.918 [+0.897, +0.939] | +0.001 [-0.003, +0.004] | +0.005 [+0.001, +0.009] | +0.011 [+0.006, +0.016] | +0.006 [+0.000, +0.011] | -0.452 [-0.463, -0.441] |
| L48 | +0.003 [+0.000, +0.007] | +0.016 [+0.012, +0.022] | +0.001 [-0.002, +0.004] | +0.414 [+0.383, +0.446] | +0.003 [+0.001, +0.006] | +0.002 [-0.000, +0.005] | +0.015 [+0.011, +0.020] | +0.013 [+0.009, +0.018] | -0.204 [-0.220, -0.188] |

### all - clean - corrupt 0.369, n 1178

| layer | S_id | S_auth | S_rand (avg of 3) | S_full | S = 0 | id - rand | auth - rand | auth - id | id - 0.5 full |
|---|---|---|---|---|---|---|---|---|---|
| L16 | +0.003 [+0.001, +0.006] | +0.004 [+0.001, +0.007] | +0.002 [+0.000, +0.004] | +0.997 [+0.991, +1.004] | +0.001 [-0.002, +0.003] | +0.001 [-0.001, +0.004] | +0.002 [-0.001, +0.004] | +0.000 [-0.003, +0.003] | -0.495 [-0.499, -0.491] |
| L24 | +0.002 [-0.001, +0.005] | +0.003 [-0.001, +0.006] | +0.002 [-0.000, +0.004] | +0.993 [+0.984, +1.002] | +0.001 [-0.001, +0.004] | -0.000 [-0.003, +0.002] | +0.001 [-0.002, +0.004] | +0.001 [-0.003, +0.004] | -0.495 [-0.500, -0.489] |
| L32 | +0.002 [-0.001, +0.005] | +0.004 [+0.000, +0.007] | +0.003 [+0.001, +0.005] | +0.975 [+0.963, +0.987] | +0.001 [-0.002, +0.003] | -0.000 [-0.003, +0.003] | +0.001 [-0.002, +0.004] | +0.001 [-0.003, +0.005] | -0.485 [-0.492, -0.479] |
| L40 | +0.006 [+0.003, +0.009] | +0.013 [+0.010, +0.017] | +0.002 [+0.000, +0.004] | +0.919 [+0.903, +0.934] | +0.001 [-0.001, +0.003] | +0.004 [+0.001, +0.006] | +0.011 [+0.008, +0.014] | +0.007 [+0.004, +0.011] | -0.453 [-0.462, -0.445] |
| L48 | +0.004 [+0.001, +0.006] | +0.017 [+0.013, +0.021] | +0.002 [-0.000, +0.004] | +0.420 [+0.397, +0.444] | +0.003 [+0.001, +0.005] | +0.002 [-0.000, +0.004] | +0.015 [+0.012, +0.019] | +0.014 [+0.010, +0.017] | -0.207 [-0.219, -0.194] |

Single random subspaces (carry, all pairs): L16 rand61 +0.003, rand62 +0.003, rand63 +0.001; L24 rand61 +0.003, rand62 +0.003, rand63 -0.000; L32 rand61 +0.001, rand62 +0.003, rand63 +0.003; L40 rand61 +0.001, rand62 +0.003, rand63 +0.003; L48 rand61 +0.002, rand62 +0.003, rand63 +0.001

## remove arm: L_S (share of the clean - corrupt gap lost when A's S-component is set to the training mean)

### test (confirmatory) - clean - corrupt 0.347, n 582

| layer | S_id | S_auth | S_rand (avg of 3) | S_full | S = 0 | id - rand | auth - rand | auth - id | id - 0.5 full |
|---|---|---|---|---|---|---|---|---|---|
| L16 | -0.001 [-0.006, +0.004] | -0.001 [-0.006, +0.004] | -0.000 [-0.004, +0.003] | +0.744 [+0.697, +0.795] | -0.000 [-0.004, +0.004] | -0.000 [-0.005, +0.004] | -0.001 [-0.005, +0.004] | -0.000 [-0.006, +0.005] | -0.373 [-0.398, -0.349] |
| L24 | -0.003 [-0.008, +0.003] | +0.001 [-0.004, +0.007] | -0.000 [-0.004, +0.003] | +0.741 [+0.694, +0.791] | +0.001 [-0.002, +0.005] | -0.002 [-0.007, +0.002] | +0.002 [-0.004, +0.006] | +0.004 [-0.002, +0.010] | -0.373 [-0.399, -0.349] |
| L32 | -0.001 [-0.007, +0.004] | -0.002 [-0.007, +0.003] | +0.000 [-0.004, +0.003] | +0.598 [+0.550, +0.646] | -0.000 [-0.004, +0.004] | -0.001 [-0.006, +0.004] | -0.002 [-0.006, +0.003] | -0.001 [-0.006, +0.005] | -0.300 [-0.325, -0.276] |
| L40 | +0.000 [-0.005, +0.005] | +0.001 [-0.004, +0.007] | -0.001 [-0.004, +0.003] | +0.474 [+0.428, +0.521] | -0.002 [-0.006, +0.002] | +0.001 [-0.003, +0.005] | +0.002 [-0.003, +0.007] | +0.001 [-0.005, +0.007] | -0.237 [-0.261, -0.214] |
| L48 | -0.000 [-0.004, +0.004] | +0.000 [-0.005, +0.005] | -0.001 [-0.004, +0.003] | +0.090 [+0.055, +0.124] | -0.000 [-0.004, +0.004] | +0.001 [-0.003, +0.004] | +0.001 [-0.004, +0.006] | +0.000 [-0.005, +0.005] | -0.045 [-0.062, -0.028] |

### tune - clean - corrupt 0.390, n 596

| layer | S_id | S_auth | S_rand (avg of 3) | S_full | S = 0 | id - rand | auth - rand | auth - id | id - 0.5 full |
|---|---|---|---|---|---|---|---|---|---|
| L16 | +0.002 [-0.002, +0.006] | +0.006 [+0.002, +0.010] | +0.002 [-0.000, +0.005] | +0.740 [+0.695, +0.786] | +0.002 [-0.001, +0.005] | -0.000 [-0.004, +0.003] | +0.003 [+0.000, +0.007] | +0.004 [-0.001, +0.008] | -0.368 [-0.392, -0.345] |
| L24 | -0.000 [-0.004, +0.004] | +0.003 [-0.002, +0.007] | +0.000 [-0.002, +0.003] | +0.737 [+0.693, +0.782] | +0.002 [-0.000, +0.005] | -0.000 [-0.004, +0.003] | +0.002 [-0.002, +0.006] | +0.003 [-0.002, +0.007] | -0.369 [-0.392, -0.346] |
| L32 | +0.002 [-0.003, +0.006] | +0.003 [-0.001, +0.007] | +0.003 [+0.001, +0.006] | +0.623 [+0.582, +0.666] | +0.002 [-0.001, +0.005] | -0.001 [-0.005, +0.003] | -0.000 [-0.004, +0.004] | +0.001 [-0.004, +0.006] | -0.310 [-0.331, -0.289] |
| L40 | +0.003 [-0.001, +0.008] | +0.006 [+0.001, +0.010] | +0.002 [-0.000, +0.005] | +0.502 [+0.458, +0.545] | +0.001 [-0.002, +0.004] | +0.001 [-0.003, +0.004] | +0.003 [-0.001, +0.007] | +0.002 [-0.003, +0.007] | -0.248 [-0.270, -0.225] |
| L48 | +0.001 [-0.003, +0.004] | +0.005 [+0.000, +0.010] | +0.002 [-0.001, +0.004] | +0.100 [+0.069, +0.130] | +0.002 [-0.001, +0.005] | -0.001 [-0.003, +0.002] | +0.003 [-0.002, +0.008] | +0.004 [-0.001, +0.009] | -0.049 [-0.064, -0.033] |

### all - clean - corrupt 0.369, n 1178

| layer | S_id | S_auth | S_rand (avg of 3) | S_full | S = 0 | id - rand | auth - rand | auth - id | id - 0.5 full |
|---|---|---|---|---|---|---|---|---|---|
| L16 | +0.001 [-0.002, +0.004] | +0.003 [-0.001, +0.006] | +0.001 [-0.001, +0.003] | +0.741 [+0.710, +0.776] | +0.001 [-0.002, +0.003] | -0.000 [-0.003, +0.002] | +0.002 [-0.001, +0.005] | +0.002 [-0.001, +0.005] | -0.370 [-0.387, -0.354] |
| L24 | -0.001 [-0.005, +0.002] | +0.002 [-0.001, +0.006] | +0.000 [-0.002, +0.002] | +0.739 [+0.708, +0.773] | +0.002 [-0.000, +0.004] | -0.001 [-0.004, +0.002] | +0.002 [-0.001, +0.005] | +0.003 [-0.000, +0.007] | -0.371 [-0.388, -0.355] |
| L32 | +0.000 [-0.003, +0.004] | +0.001 [-0.002, +0.004] | +0.002 [-0.001, +0.004] | +0.612 [+0.580, +0.643] | +0.001 [-0.001, +0.003] | -0.001 [-0.004, +0.002] | -0.001 [-0.004, +0.002] | +0.000 [-0.003, +0.004] | -0.305 [-0.321, -0.289] |
| L40 | +0.002 [-0.001, +0.005] | +0.004 [-0.000, +0.007] | +0.001 [-0.001, +0.003] | +0.489 [+0.457, +0.521] | -0.000 [-0.003, +0.002] | +0.001 [-0.002, +0.003] | +0.003 [-0.001, +0.006] | +0.002 [-0.002, +0.006] | -0.243 [-0.259, -0.227] |
| L48 | +0.000 [-0.002, +0.003] | +0.003 [-0.001, +0.006] | +0.001 [-0.001, +0.003] | +0.095 [+0.073, +0.116] | +0.001 [-0.002, +0.003] | -0.000 [-0.002, +0.002] | +0.002 [-0.002, +0.006] | +0.002 [-0.001, +0.006] | -0.047 [-0.058, -0.036] |

Single random subspaces (remove, all pairs): L16 rand61 +0.001, rand62 +0.001, rand63 +0.001; L24 rand61 +0.001, rand62 -0.000, rand63 +0.000; L32 rand61 +0.002, rand62 +0.000, rand63 +0.003; L40 rand61 +0.001, rand62 +0.001, rand63 +0.001; L48 rand61 +0.000, rand62 +0.001, rand63 +0.001

## Share of ||h_A - h_B||^2 at the title positions inside each subspace (mean over pairs)

| layer | id | auth | rand61 | rand62 | rand63 |
|---|---|---|---|---|---|
| L16 | 0.0027 | 0.0054 | 0.0020 | 0.0019 | 0.0020 |
| L24 | 0.0029 | 0.0054 | 0.0020 | 0.0019 | 0.0020 |
| L32 | 0.0029 | 0.0040 | 0.0020 | 0.0019 | 0.0020 |
| L40 | 0.0024 | 0.0040 | 0.0019 | 0.0019 | 0.0020 |
| L48 | 0.0020 | 0.0042 | 0.0020 | 0.0019 | 0.0020 |

## Subspace fits (training papers outside all pair teams; held-out 5-fold team CV)

| layer | n train | rank S_id | alpha year / logcit / field / auth | year R² | log cit R² | field acc | author-map R² | author top-1 (majority) | max cos(S_id, S_auth) |
|---|---|---|---|---|---|---|---|---|---|
| L16 | 5041 | 9 | 1 / 1 / 1 / 100 | 0.362 | 0.261 | 0.675 | 0.0009 | 0.078 (0.080) | 0.360 |
| L24 | 5041 | 9 | 1 / 1 / 1 / 100 | 0.429 | 0.334 | 0.706 | 0.0014 | 0.079 (0.080) | 0.354 |
| L32 | 5041 | 9 | 1 / 1 / 1 / 100 | 0.441 | 0.323 | 0.701 | 0.0014 | 0.079 (0.080) | 0.359 |
| L40 | 5041 | 9 | 1 / 1 / 1 / 100 | 0.470 | 0.410 | 0.696 | 0.0023 | 0.078 (0.080) | 0.336 |
| L48 | 5041 | 9 | 1 / 1 / 1 / 100 | 0.519 | 0.491 | 0.699 | 0.0033 | 0.078 (0.080) | 0.317 |

## Checks (WARN only)

- OK S_full vs X1 authors@L16: R_full 0.9972 vs X1 R_authors 0.9989 on 1178 common pairs; per pair |score diff| max 0.1033, exact share 0.156; clean |diff| max 0.0000, corrupt |diff| max 0.0000
- OK S_full vs X1 authors@L24: R_full 0.9927 vs X1 R_authors 0.9928 on 1178 common pairs; per pair |score diff| max 0.1187, exact share 0.138; clean |diff| max 0.0000, corrupt |diff| max 0.0000
- OK S_full vs X1 authors@L32: R_full 0.9749 vs X1 R_authors 0.9745 on 1178 common pairs; per pair |score diff| max 0.2036, exact share 0.164; clean |diff| max 0.0000, corrupt |diff| max 0.0000
- OK S_full vs X1 authors@L40: R_full 0.9188 vs X1 R_authors 0.9191 on 1178 common pairs; per pair |score diff| max 0.1845, exact share 0.137; clean |diff| max 0.0000, corrupt |diff| max 0.0000
- OK S_full vs X1 authors@L48: R_full 0.4205 vs X1 R_authors 0.4201 on 1178 common pairs; per pair |score diff| max 0.1078, exact share 0.062; clean |diff| max 0.0000, corrupt |diff| max 0.0000
- WARN identity patch S=0 (carry == corrupt): max |diff| 0.1030, mean 0.00830, exact share 0.030; ratio with S=0 per layer +0.0007, +0.0015, +0.0006, +0.0009, +0.0027
- WARN identity patch S=0 (remove == clean): max |diff| 0.1365, mean 0.00821, exact share 0.145; ratio with S=0 per layer +0.0008, +0.0019, +0.0010, -0.0003, +0.0009
- WARN 3 random subspaces agree (all pairs, both arms, all layers): interval excludes 0 at: carry L24 rand62 - rand63 +0.003 [+0.001, +0.006]

## Deviations from addendum 6

- S_id has 9 dimensions, not 10: with one shared ridge alpha the 8 one-vs-rest field weight vectors sum to exactly 0 (centred one-hot rows sum to 0), so year + log citations + 8 field vectors span 9 dimensions; the dependent QR direction is dropped. S_auth, S_rand stay 10-dim (the comparison with S_rand is therefore slightly conservative for S_id).
- Ridge convention of the Stage 13 probes (features standardised on the training rows, alpha x trace/d, intercept); the fitted readout vectors are mapped back to raw residual coordinates (w / sd) before orthonormalisation. Alpha per target family (year, log citations, field, author map) by pooled held-out normalised MSE over the 5 team folds.
- Training teams = the archived 9,108-paper team ids (summary_cpu_teamci/folds_own9108_k5s13.npz); CV folds = the archived team folds restricted to the training papers.
- "Layer selected on tune" = the layer with the largest R_S - R_rand on tune (as the X1 layer choice of prereg.json). "Neither ... anywhere" is checked on tune and test, carry arm.
- S_full in the remove arm (every title position set to mu) is reported as a reference; addendum 6 only defines S_full for carry.

## Plain summary

1. Replacing B's whole title states with A's (S_full) moves 0.92 of the clean - corrupt gap at L40 on test; this is the X1 ceiling.
2. Moving only A's 10-dim paper-attribute component (S_id: year, citations, field) moves +0.01 of the gap at L40 vs +0.00 for random 10-dim subspaces (difference +0.002 [-0.001, +0.005]).
3. Moving A's 10-dim author component (S_auth: the directions that predict the first-author token's unembedding) moves +0.02 at L48 vs +0.00 random (difference +0.015 [+0.010, +0.020]).
4. Removing the components from A's own prompt (remove arm) costs S_id +0.00 and S_auth +0.00 of the gap at those layers (random -0.00 / -0.00).
5. Pre-registered verdict: H3 supported (S_auth carries more than S_id).

