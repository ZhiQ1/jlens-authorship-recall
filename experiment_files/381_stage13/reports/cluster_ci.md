# Team-cluster bootstrap vs per-paper bootstrap (point estimates unchanged)

Teams: 7247 groups over 9108 papers (papers sharing any full author name).

## Interval width ratio (team / paper), by table

                                   count  mean   min   max
table                                                     
6.2 true-title target-control       47.0  1.07  0.99  1.21
6.3 title-specific mean, control    47.0  1.08  0.98  1.22
6.3 title-specific mean, target     47.0  1.07  0.97  1.22
6.4 title-specific target-control   47.0  1.05  0.95  1.17
C-A within target                   47.0  1.00  0.94  1.08
E1 recovery, control                14.0  1.00  0.96  1.06
E1 recovery, target                 14.0  0.99  0.92  1.04
E1t recovery, control               11.0  1.03  0.99  1.10
E1t recovery, target                11.0  0.97  0.95  1.02
E2 loss, control                    12.0  1.01  0.98  1.08
E2 loss, target                     12.0  1.00  0.95  1.07
E2n loss, control                   12.0  0.99  0.95  1.04
E2n loss, target                    12.0  0.98  0.96  1.05
R0 view A-B                         47.0  1.03  0.93  1.11

## Rows where "interval excludes 0" changes: 4 of 380

                            table      readout  layer    est  lo_paper  hi_paper  lo_team  hi_team
6.4 title-specific target-control        logit     32  0.005     0.000     0.011   -0.000    0.010
    6.2 true-title target-control        logit     56  0.035     0.006     0.064   -0.001    0.069
                C-A within target        logit     55  0.025    -0.000     0.049    0.000    0.050
  6.3 title-specific mean, target jlens_public     48 -0.007    -0.014     0.000   -0.015   -0.000

