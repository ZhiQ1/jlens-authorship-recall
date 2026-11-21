# Citation split of the title-position and name-position probes — exploratory (post hoc, not pre-registered)

Exploratory (post hoc, not pre-registered), 2026-11-21: does the target - control probe signal differ between low- and
high-citation papers?  ("276x gap location", user reading rule: high half stronger at the title-position probe -> the gap is at
recognising; equal -> the gap is at saying.)  CPU only, stored per-paper probe outputs only.

Probes (per paper spec = probe(true) - probe(false)):
  title   E4b title-position probe, first author first token (summary_b1_e4b5/probe/perpaper_e4b_parity_L40.parquet);
          V0 = spec0 on papers with drop0 == False (the confirmed 1,395-paper version, C09); Vpd = mean of spec_k over the
          false titles not dropped (per-donor rule; larger n).
  name    name-position probe, surname first token, Vpd (summary_b2_np/probe_v2/perpaper_surname_first_L{40,48}.parquet;
          the 4,654 papers of the locked H3 test).
Sets: (S11) Stage-11 sample (1,186) intersect available, split at the Stage-11 median (31 citations, ties low);
      (FULL) each probe's full available target+control set, split at its own median (ties low).
Contrast: target - control within citation bins (bins with >= MINB papers per group inside the half; weights n_t n_c/(n_t+n_c));
          low, high, high - low. CI: 2,000 multinomial draws over author teams (stage13_cpu.group_folds), default_rng(1121),
          one draw set per analysis set. Also plain group means per half.


| set | half | n T / C | citations | mean T | mean C | T − C within bins [95% team CI] |
|---|---|---|---|---|---|---|
| title E4b V0 (spec0, reuse-free) L40 · FULL (median 55) | low | 319.0 / 380.0 | 0–55 | +0.0894 | +0.0287 | +0.0581 [+0.0156, +0.1015] |
| title E4b V0 (spec0, reuse-free) L40 · FULL (median 55) | high | 577.0 / 119.0 | 57–12788 | +0.0747 | +0.0207 | +0.0615 [-0.0090, +0.1292] |
| title E4b V0 (spec0, reuse-free) L40 · FULL (median 55) | high − low | | | | | +0.0034 [-0.0764, +0.0834] |
| title E4b V0 (spec0, reuse-free) L40 · Stage-11 ∩ (median 31) | low | 62.0 / 75.0 | 0–31 | +0.0908 | +0.0361 | +0.0736 [-0.0249, +0.1779] |
| title E4b V0 (spec0, reuse-free) L40 · Stage-11 ∩ (median 31) | high | 56.0 / 58.0 | 32–1010 | +0.0720 | +0.0179 | +0.0546 [-0.0589, +0.1670] |
| title E4b V0 (spec0, reuse-free) L40 · Stage-11 ∩ (median 31) | high − low | | | | | -0.0189 [-0.1726, +0.1304] |
| title E4b Vpd L40 · FULL (median 66) | low | 1137.0 / 1193.0 | 0–66 | +0.0893 | +0.0562 | +0.0354 [+0.0144, +0.0576] |
| title E4b Vpd L40 · FULL (median 66) | high | 1993.0 / 331.0 | 67–20185 | +0.0611 | +0.0510 | +0.0163 [-0.0184, +0.0504] |
| title E4b Vpd L40 · FULL (median 66) | high − low | | | | | -0.0191 [-0.0592, +0.0207] |
| title E4b Vpd L40 · Stage-11 ∩ (median 31) | low | 207.0 / 207.0 | 0–31 | +0.1006 | +0.0417 | +0.0592 [+0.0078, +0.1088] |
| title E4b Vpd L40 · Stage-11 ∩ (median 31) | high | 197.0 / 207.0 | 32–1010 | +0.0923 | +0.0411 | +0.0549 [+0.0010, +0.1070] |
| title E4b Vpd L40 · Stage-11 ∩ (median 31) | high − low | | | | | -0.0042 [-0.0778, +0.0679] |
| name-position Vpd L40 · FULL (median 66) | low | 1137.0 / 1193.0 | 0–66 | +0.0867 | +0.0581 | +0.0307 [+0.0151, +0.0473] |
| name-position Vpd L40 · FULL (median 66) | high | 1993.0 / 331.0 | 67–20185 | +0.0703 | +0.0401 | +0.0325 [+0.0124, +0.0516] |
| name-position Vpd L40 · FULL (median 66) | high − low | | | | | +0.0018 [-0.0252, +0.0271] |
| name-position Vpd L40 · Stage-11 ∩ (median 31) | low | 207.0 / 207.0 | 0–31 | +0.0639 | +0.0602 | +0.0037 [-0.0315, +0.0388] |
| name-position Vpd L40 · Stage-11 ∩ (median 31) | high | 197.0 / 207.0 | 32–1010 | +0.0866 | +0.0432 | +0.0435 [+0.0106, +0.0748] |
| name-position Vpd L40 · Stage-11 ∩ (median 31) | high − low | | | | | +0.0398 [-0.0072, +0.0879] |
| name-position Vpd L48 · FULL (median 66) | low | 1137.0 / 1193.0 | 0–66 | +0.1169 | +0.0657 | +0.0527 [+0.0344, +0.0714] |
| name-position Vpd L48 · FULL (median 66) | high | 1993.0 / 331.0 | 67–20185 | +0.1237 | +0.0659 | +0.0535 [+0.0301, +0.0775] |
| name-position Vpd L48 · FULL (median 66) | high − low | | | | | +0.0008 [-0.0313, +0.0304] |
| name-position Vpd L48 · Stage-11 ∩ (median 31) | low | 207.0 / 207.0 | 0–31 | +0.0895 | +0.0677 | +0.0216 [-0.0208, +0.0632] |
| name-position Vpd L48 · Stage-11 ∩ (median 31) | high | 197.0 / 207.0 | 32–1010 | +0.1265 | +0.0805 | +0.0427 [-0.0034, +0.0873] |
| name-position Vpd L48 · Stage-11 ∩ (median 31) | high − low | | | | | +0.0210 [-0.0383, +0.0836] |

V0 check: target+control papers with drop0 == False = 1395 (published 1,395).
