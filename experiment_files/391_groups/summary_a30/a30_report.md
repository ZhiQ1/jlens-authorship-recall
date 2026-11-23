# Addendum 30 (LOCKED) — H5 direction asymmetry: Reversed (reverse direction easier than forward)

Papers 1200 ({'A': 600, 'B': 600}); missing shards []; prereg sha256 ada47d7d4dd7686427aa22af22c0368384a63bdb5e145a72bbd028d4e5a57e63.

                                                        test       est        lo        hi     p    n  p_holm   holm_lo   holm_hi
                                R1 A - B within bins of F_id  0.442748  0.373157  0.517122 0.000 1200     0.0  0.362068  0.527697
                     R2 A: forward success - reverse success -0.031667 -0.047233 -0.015948 0.000  600     0.0 -0.047233 -0.015948
R3 (secondary) A: F_id -> p_true | log citations (std slope)  0.109764  0.034053  0.187348 0.006  600     NaN       NaN       NaN

## Descriptive (group means)

       F_spec  F_spec_mis      F_id  fwd_success    fwd_f1  fwd_exact  rev_success
grp                                                                               
A    0.615475    0.016469  0.599006     0.008333  0.149131      0.005        0.040
B    0.103859   -0.052399  0.156258     0.000000  0.120351      0.000        0.005
