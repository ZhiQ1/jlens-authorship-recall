# New 2 — source of the K4c reversal (exploratory, post hoc)

y = p_orig − p_fict (log10(1/rank) of the true name tokens at the final layer after patching the variant's post-title tail at layer l); y_F = mean over L24/32/40/44/48. Coefficients per 1 SD of each regressor (field fixed effects, den = true − false_0 as scale control). n = 90; team bootstrap 50.

```
    y model   term  coef_per_sd      lo      hi  n
  y_F    M0   lcit      +0.0060 -0.0056 +0.0161 90
  y_F    M0    den      +0.0289 +0.0157 +0.0408 90
  y_F    M1   lcit      +0.0038 -0.0096 +0.0158 90
  y_F    M1 k_rare      +0.0104 -0.0006 +0.0200 90
  y_F    M1    den      +0.0298 +0.0166 +0.0424 90
  y_F    M2   lcit      +0.0047 -0.0091 +0.0164 90
  y_F    M2    dlp      -0.0063 -0.0209 +0.0067 90
  y_F    M2    den      +0.0277 +0.0131 +0.0381 90
  y_F    M3   lcit      +0.0023 -0.0095 +0.0153 90
  y_F    M3 k_rare      +0.0019 -0.0130 +0.0133 90
  y_F    M3    dlp      -0.0043 -0.0168 +0.0094 90
  y_F    M3   tlen      +0.0214 -0.0026 +0.0355 90
  y_F    M3 target      -0.0008 -0.0124 +0.0154 90
  y_F    M3    den      +0.0237 +0.0094 +0.0335 90
y_L48    M0   lcit      +0.0177 -0.0018 +0.0383 90
y_L48    M0    den      +0.0651 +0.0393 +0.0917 90
y_L48    M1   lcit      +0.0135 -0.0103 +0.0344 90
y_L48    M1 k_rare      +0.0205 +0.0060 +0.0406 90
y_L48    M1    den      +0.0668 +0.0414 +0.0915 90
y_L48    M2   lcit      +0.0158 -0.0027 +0.0363 90
y_L48    M2    dlp      -0.0097 -0.0299 +0.0086 90
y_L48    M2    den      +0.0631 +0.0328 +0.0886 90
y_L48    M3   lcit      +0.0119 -0.0083 +0.0332 90
y_L48    M3 k_rare      +0.0057 -0.0089 +0.0226 90
y_L48    M3    dlp      -0.0059 -0.0251 +0.0106 90
y_L48    M3   tlen      +0.0300 +0.0038 +0.0567 90
y_L48    M3 target      +0.0140 -0.0026 +0.0374 90
y_L48    M3    den      +0.0530 +0.0183 +0.0815 90
```

Means by within-field citation half:

```
         y_F   y_L48  k_rare     dlp     tlen  target     den
half                                                         
high +0.0410 +0.0872 +5.0571 +0.4157 +13.5143 +0.4000 +0.1800
low  +0.0370 +0.0728 +3.6182 +0.7058 +12.8182 +0.4364 +0.2182
```

Correlations:

```
          lcit  k_rare     dlp    tlen  target     den     y_F
lcit   +1.0000 +0.2390 -0.1830 +0.1040 +0.0480 -0.0500 +0.0790
k_rare +0.2390 +1.0000 -0.1590 +0.3460 +0.2050 -0.0420 +0.1390
dlp    -0.1830 -0.1590 +1.0000 -0.1620 -0.0870 -0.1650 -0.1950
tlen   +0.1040 +0.3460 -0.1620 +1.0000 +0.2840 +0.2160 +0.4140
target +0.0480 +0.2050 -0.0870 +0.2840 +1.0000 +0.3600 +0.2090
den    -0.0500 -0.0420 -0.1650 +0.2160 +0.3600 +1.0000 +0.4120
y_F    +0.0790 +0.1390 -0.1950 +0.4140 +0.2090 +0.4120 +1.0000
```
