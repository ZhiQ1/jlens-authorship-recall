# Addendum 19 results — confirmatory analysis of already-seen data (post hoc lock), addendum 19

Addendum sha256 f6b650726d75d2a21f42dcaabf539803e074e3070ae09ddb2cdd0285b9cc35a4; 9,108 papers, 7,247 author teams, 2000 team bootstrap draws (seed 391). Computed by job 11951874 (prereg19_exposure_ratio.py); this report written by prereg19_report.py from its saved outputs.

## Main comparison: threshold ratio

| quantity | n | est | lo | hi | log10_1p_est | log10_1p_lo | log10_1p_hi |
|---|---|---|---|---|---|---|---|
| c50_recognition | 9108 | 39.99 | 35.81 | 44.39 | 1.613 | 1.566 | 1.657 |
| c50_recognition_excl_uncertain | 7046 | 9.319 | 8.002 | 10.64 | 1.014 | 0.9544 | 1.066 |
| c50_recall | 9108 | 1.104e+04 | 8172 | 1.561e+04 | 4.043 | 3.912 | 4.193 |
| rho_recall_over_recognition | 9108 | 276 | 202.6 | 390.4 | 2.43 | 2.296 | 2.581 |
| rho_recall_over_recognition_excl_uncertain | 9108 | 1184 | 851.5 | 1712 | 3.029 | 2.888 | 3.187 |

ρ = c50(recall) / c50(recognition) = 276 [203, 390]; log10 ρ = 2.430 [2.296, 2.581] → **confirmed** (rule: 95% CI of ρ entirely above 1). Valid draws 2000.
Sensitivity (recognition excluding uncertain papers, n 7,046; descriptive): ρ = 1184 [851, 1712].

## Secondary comparison: trend of within-bin target − control (spec_all, final L63)

| citation_bin | n_papers | n_target | n_control | median_citations | used_in_slope | diff | lo | hi |
|---|---|---|---|---|---|---|---|---|
| 0-2 | 796 | 200 | 352 | 0 | True | 0.1894 | 0.153 | 0.2267 |
| 3-4 | 799 | 207 | 355 | 3 | True | 0.1913 | 0.1524 | 0.2283 |
| 5-8 | 800 | 237 | 332 | 6 | True | 0.1871 | 0.1526 | 0.2204 |
| 9-16 | 800 | 288 | 275 | 12 | True | 0.1754 | 0.1419 | 0.2094 |
| 17-32 | 800 | 327 | 234 | 23 | True | 0.1848 | 0.1506 | 0.2197 |
| 33-64 | 800 | 401 | 185 | 44 | True | 0.2432 | 0.2078 | 0.2778 |
| 65-128 | 800 | 441 | 165 | 87 | True | 0.2066 | 0.1656 | 0.2439 |
| 129-256 | 800 | 497 | 126 | 165.5 | True | 0.2412 | 0.201 | 0.2836 |
| 257-512 | 800 | 533 | 105 | 328 | True | 0.2366 | 0.1958 | 0.2777 |
| 513-1024 | 800 | 603 | 53 | 671 | True | 0.2985 | 0.2363 | 0.3579 |
| 1025-2048 | 665 | 539 | 29 | 1332 | False | 0.3451 | 0.2693 | 0.4215 |
| 2049-4096 | 326 | 264 | 9 | 2610 | False | 0.3476 | 0.1915 | 0.4985 |
| 4097+ | 122 | 84 | 0 | 5924 | False |  |  |  |

WLS slope = +0.0297 [+0.0141, +0.0445] change in target - control per 10x median citations (log10 scale), over 10 bins with ≥ 30 papers per group → **grows with exposure** (rule: CI above 0).

Labels: confirmatory analysis of already-seen data (point thresholds known since 2026-11-14); single model; bins are stratified samples, not population rates; recognition at the bottom bins includes the ~25% guess floor of the 4-order multiple-choice rule; c50 of recall lies inside the observed citation range but near its upper part.
