# Stage 7.2 — Frozen Gold vs 100 False Authors

Completed papers: 50/50; complete A/B pairs: 20/20.

Measures are **first-token**, NOT complete author identity. Collision is a tie (0.5), not a correct classification.

## Matched A/B per-layer mean difference (exploratory)

| Readout | Pool | Layer | n pairs | A−B | Bootstrap 95% CI |
|---|---|---:|---:|---:|---|
| jlens | random | 16 | 20 | +0.0470 | [-0.1340, +0.2360] |
| jlens | matched | 16 | 20 | +0.0420 | [-0.1330, +0.2200] |
| jlens | combined | 16 | 20 | +0.0445 | [-0.1310, +0.2282] |
| jlens | random | 24 | 20 | +0.0665 | [-0.1160, +0.2530] |
| jlens | matched | 24 | 20 | +0.1325 | [-0.0300, +0.2935] |
| jlens | combined | 24 | 20 | +0.0995 | [-0.0710, +0.2745] |
| jlens | random | 32 | 20 | -0.0220 | [-0.2185, +0.1760] |
| jlens | matched | 32 | 20 | +0.0750 | [-0.1050, +0.2510] |
| jlens | combined | 32 | 20 | +0.0265 | [-0.1568, +0.2150] |
| jlens | random | 40 | 20 | +0.1525 | [+0.0200, +0.2930] |
| jlens | matched | 40 | 20 | +0.1475 | [+0.0015, +0.2940] |
| jlens | combined | 40 | 20 | +0.1500 | [+0.0133, +0.2893] |
| jlens | random | 48 | 20 | +0.1930 | [+0.0730, +0.3165] |
| jlens | matched | 48 | 20 | +0.1930 | [+0.0595, +0.3225] |
| jlens | combined | 48 | 20 | +0.1930 | [+0.0710, +0.3178] |
| jlens | random | 56 | 20 | +0.1850 | [-0.0105, +0.3540] |
| jlens | matched | 56 | 20 | +0.1880 | [+0.0100, +0.3525] |
| jlens | combined | 56 | 20 | +0.1865 | [+0.0148, +0.3445] |
| jlens | random | 62 | 20 | +0.0420 | [-0.1620, +0.2365] |
| jlens | matched | 62 | 20 | +0.0345 | [-0.1345, +0.2060] |
| jlens | combined | 62 | 20 | +0.0382 | [-0.1440, +0.2147] |
| vanilla | random | 16 | 20 | +0.0225 | [-0.1610, +0.2105] |
| vanilla | matched | 16 | 20 | +0.0605 | [-0.1050, +0.2285] |
| vanilla | combined | 16 | 20 | +0.0415 | [-0.1303, +0.2180] |
| vanilla | random | 24 | 20 | +0.0760 | [-0.1240, +0.2725] |
| vanilla | matched | 24 | 20 | +0.0780 | [-0.1275, +0.2790] |
| vanilla | combined | 24 | 20 | +0.0770 | [-0.1235, +0.2775] |
| vanilla | random | 32 | 20 | +0.1910 | [+0.0370, +0.3380] |
| vanilla | matched | 32 | 20 | +0.2090 | [+0.0505, +0.3575] |
| vanilla | combined | 32 | 20 | +0.2000 | [+0.0467, +0.3455] |
| vanilla | random | 40 | 20 | +0.1170 | [-0.0395, +0.2570] |
| vanilla | matched | 40 | 20 | +0.0840 | [-0.0625, +0.2275] |
| vanilla | combined | 40 | 20 | +0.1005 | [-0.0490, +0.2403] |
| vanilla | random | 48 | 20 | +0.0930 | [-0.0775, +0.2470] |
| vanilla | matched | 48 | 20 | +0.1090 | [-0.0405, +0.2420] |
| vanilla | combined | 48 | 20 | +0.1010 | [-0.0580, +0.2415] |
| vanilla | random | 56 | 20 | +0.1650 | [-0.0505, +0.3590] |
| vanilla | matched | 56 | 20 | +0.2070 | [-0.0015, +0.4050] |
| vanilla | combined | 56 | 20 | +0.1860 | [-0.0250, +0.3790] |
| vanilla | random | 62 | 20 | +0.0305 | [-0.1635, +0.2170] |
| vanilla | matched | 62 | 20 | +0.0470 | [-0.1320, +0.2295] |
| vanilla | combined | 62 | 20 | +0.0387 | [-0.1513, +0.2213] |
| final | random | 63 | 20 | +0.0345 | [-0.1495, +0.2135] |
| final | matched | 63 | 20 | +0.0405 | [-0.1335, +0.2070] |
| final | combined | 63 | 20 | +0.0375 | [-0.1420, +0.2082] |

## Interpretation limits

Random/Matched false candidates are historical dataset authors, not verified exhaustive nonauthors outside the sampled paper list.
The frozen Matched pool uses tiered matching with different constraints by paper. Readout scores share token priors and candidate duplication.
This experiment does **not** run shuffled title controls or full-name conditional validation.
The pilot and per-layer comparisons are exploratory; confidence intervals are unadjusted for multiple comparisons.
