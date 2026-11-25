# New 2 — source of the K4c reversal (exploratory, post hoc)

y = p_orig − p_fict (log10(1/rank) of the true name tokens at the final layer after patching the variant's post-title tail at layer l); y_F = mean over L24/32/40/44/48. Coefficients per 1 SD of each regressor (field fixed effects, den = true − false_0 as scale control). n = 1083; team bootstrap 2000.

```
    y model   term  coef_per_sd      lo      hi    n
  y_F    M0   lcit      -0.0114 -0.0148 -0.0080 1083
  y_F    M0    den      +0.0135 +0.0094 +0.0176 1083
  y_F    M1   lcit      -0.0111 -0.0146 -0.0077 1083
  y_F    M1 k_rare      +0.0020 -0.0012 +0.0053 1083
  y_F    M1    den      +0.0134 +0.0093 +0.0176 1083
  y_F    M2   lcit      -0.0118 -0.0155 -0.0083 1083
  y_F    M2    dlp      -0.0019 -0.0058 +0.0019 1083
  y_F    M2    den      +0.0134 +0.0093 +0.0175 1083
  y_F    M3   lcit      -0.0111 -0.0147 -0.0074 1083
  y_F    M3 k_rare      +0.0003 -0.0031 +0.0038 1083
  y_F    M3    dlp      -0.0016 -0.0054 +0.0021 1083
  y_F    M3   tlen      +0.0029 -0.0007 +0.0067 1083
  y_F    M3 target      +0.0071 +0.0040 +0.0103 1083
  y_F    M3    den      +0.0108 +0.0068 +0.0148 1083
y_L48    M0   lcit      -0.0198 -0.0267 -0.0130 1083
y_L48    M0    den      +0.0388 +0.0294 +0.0479 1083
y_L48    M1   lcit      -0.0196 -0.0265 -0.0129 1083
y_L48    M1 k_rare      +0.0009 -0.0055 +0.0073 1083
y_L48    M1    den      +0.0388 +0.0294 +0.0478 1083
y_L48    M2   lcit      -0.0189 -0.0260 -0.0120 1083
y_L48    M2    dlp      +0.0036 -0.0033 +0.0110 1083
y_L48    M2    den      +0.0390 +0.0296 +0.0481 1083
y_L48    M3   lcit      -0.0180 -0.0252 -0.0112 1083
y_L48    M3 k_rare      -0.0020 -0.0089 +0.0051 1083
y_L48    M3    dlp      +0.0040 -0.0029 +0.0115 1083
y_L48    M3   tlen      +0.0055 -0.0017 +0.0127 1083
y_L48    M3 target      +0.0098 +0.0034 +0.0162 1083
y_L48    M3    den      +0.0354 +0.0257 +0.0450 1083
```

Means by within-field citation half:

```
         y_F   y_L48  k_rare     dlp     tlen  target     den
half                                                         
high +0.0143 +0.0415 +3.2104 -0.0333 +12.3166 +0.5214 +0.3708
low  +0.0285 +0.0624 +4.0330 +0.4163 +12.9158 +0.5018 +0.2710
```

Correlations:

```
          lcit  k_rare     dlp    tlen  target     den     y_F
lcit   +1.0000 -0.1300 -0.2420 -0.0770 +0.0090 +0.2110 -0.1600
k_rare -0.1300 +1.0000 +0.0490 +0.4410 +0.0520 -0.0480 +0.0430
dlp    -0.2420 +0.0490 +1.0000 +0.0340 -0.0710 -0.1330 -0.0080
tlen   -0.0770 +0.4410 +0.0340 +1.0000 +0.0480 -0.0360 +0.0530
target +0.0090 +0.0520 -0.0710 +0.0480 +1.0000 +0.3570 +0.1960
den    +0.2110 -0.0480 -0.1330 -0.0360 +0.3570 +1.0000 +0.1970
y_F    -0.1600 +0.0430 -0.0080 +0.0530 +0.1960 +0.1970 +1.0000
```
