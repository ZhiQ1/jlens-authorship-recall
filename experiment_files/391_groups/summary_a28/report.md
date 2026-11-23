# Addendum 28 — X4 with topic-matched partners

verdict: **mixed (P reported with CI)**

{
 "label": "addendum 28 (LOCKED)",
 "addendum_sha256": "d98f36861b9605046efb02f972986e2f7389e43e9257cf295dda6071d8c3b28d",
 "n_papers": 1178,
 "missing_shards": [],
 "verdict": "mixed (P reported with CI)",
 "primary": {
  "P": 0.24533481503740037,
  "lo": -0.06735341349332472,
  "hi": 0.49306853767027226,
  "D_topic": 0.01627505804669142,
  "D_topic_lo": -0.0035301150262725383,
  "D_topic_hi": 0.03575442157823866
 },
 "sensitivity_bert": {
  "P": 0.40850169319482815,
  "lo": 0.10668475765027113,
  "hi": 0.6779631105221299
 }
}

## Contrasts (team bootstrap 2,000, seed 27)

          ans  layer                                  contrast    n     est       lo      hi      p  p_holm_layers
        field      8                                 D_partner 1178  0.0493   0.0050  0.0961 0.0310            NaN
        field      8                             D_topic_mpnet 1178  0.0052  -0.0368  0.0484 0.7960            NaN
        field      8                              D_topic_bert 1178 -0.0017  -0.0446  0.0392 0.9560            NaN
        field      8 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.1055  -1.9660  1.2551    NaN            NaN
        field      8   P_topic_bert = D_topic_bert / D_partner 1178 -0.0344  -2.5000  0.9933    NaN            NaN
        field     16                                 D_partner 1178  0.0542   0.0120  0.0984 0.0120            NaN
        field     16                             D_topic_mpnet 1178  0.0074  -0.0308  0.0482 0.7150            NaN
        field     16                              D_topic_bert 1178  0.0107  -0.0260  0.0491 0.5530            NaN
        field     16 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.1365  -1.1968  1.0115    NaN            NaN
        field     16   P_topic_bert = D_topic_bert / D_partner 1178  0.1973  -0.9517  1.0111    NaN            NaN
        field     24                                 D_partner 1178  0.0459   0.0057  0.0865 0.0260            NaN
        field     24                             D_topic_mpnet 1178  0.0106  -0.0262  0.0519 0.6070            NaN
        field     24                              D_topic_bert 1178 -0.0065  -0.0403  0.0283 0.7150            NaN
        field     24 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.2303  -1.1456  1.4930    NaN            NaN
        field     24   P_topic_bert = D_topic_bert / D_partner 1178 -0.1427  -2.4179  0.6858    NaN            NaN
        field     32                                 D_partner 1178  0.0120  -0.0231  0.0500 0.5100            NaN
        field     32                             D_topic_mpnet 1178 -0.0061  -0.0341  0.0236 0.6970            NaN
        field     32                              D_topic_bert 1178 -0.0285  -0.0592  0.0004 0.0530            NaN
        field     32 P_topic_mpnet = D_topic_mpnet / D_partner 1178 -0.5091 -10.4573  8.6444    NaN            NaN
        field     32   P_topic_bert = D_topic_bert / D_partner 1178 -2.3688 -25.8164 22.1841    NaN            NaN
        field     40                                 D_partner 1178  0.0082  -0.0249  0.0425 0.6290            NaN
        field     40                             D_topic_mpnet 1178 -0.0290  -0.0532 -0.0050 0.0200            NaN
        field     40                              D_topic_bert 1178 -0.0455  -0.0712 -0.0198 0.0010            NaN
        field     40 P_topic_mpnet = D_topic_mpnet / D_partner 1178 -3.5274 -23.9370 27.2625    NaN            NaN
        field     40   P_topic_bert = D_topic_bert / D_partner 1178 -5.5357 -36.3012 40.2836    NaN            NaN
        field     48                                 D_partner 1178  0.0051  -0.0148  0.0251 0.6090            NaN
        field     48                             D_topic_mpnet 1178 -0.0145  -0.0299  0.0000 0.0520            NaN
        field     48                              D_topic_bert 1178 -0.0101  -0.0261  0.0060 0.2040            NaN
        field     48 P_topic_mpnet = D_topic_mpnet / D_partner 1178 -2.8713 -22.8084 19.7730    NaN            NaN
        field     48   P_topic_bert = D_topic_bert / D_partner 1178 -2.0021 -16.2933 14.8309    NaN            NaN
        field     56                                 D_partner 1178  0.0003  -0.0022  0.0027 0.8430            NaN
        field     56                             D_topic_mpnet 1178 -0.0022  -0.0049  0.0006 0.1230            NaN
        field     56                              D_topic_bert 1178  0.0009  -0.0014  0.0032 0.4520            NaN
        field     56 P_topic_mpnet = D_topic_mpnet / D_partner 1178 -8.7046 -28.7860 22.6796    NaN            NaN
        field     56   P_topic_bert = D_topic_bert / D_partner 1178  3.4889 -11.1041 12.7791    NaN            NaN
 first_author      8                                 D_partner 1178  0.0484   0.0395  0.0572 0.0000            NaN
 first_author      8                             D_topic_mpnet 1178  0.0191   0.0108  0.0272 0.0000            NaN
 first_author      8                              D_topic_bert 1178  0.0205   0.0120  0.0293 0.0000            NaN
 first_author      8 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.3941   0.2435  0.5263    NaN            NaN
 first_author      8   P_topic_bert = D_topic_bert / D_partner 1178  0.4236   0.2652  0.5653    NaN            NaN
 first_author     16                                 D_partner 1178  0.0543   0.0454  0.0629 0.0000            NaN
 first_author     16                             D_topic_mpnet 1178  0.0236   0.0160  0.0312 0.0000            NaN
 first_author     16                              D_topic_bert 1178  0.0286   0.0208  0.0367 0.0000            NaN
 first_author     16 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.4350   0.3122  0.5494    NaN            NaN
 first_author     16   P_topic_bert = D_topic_bert / D_partner 1178  0.5264   0.4079  0.6469    NaN            NaN
 first_author     24                                 D_partner 1178  0.0562   0.0472  0.0648 0.0000            NaN
 first_author     24                             D_topic_mpnet 1178  0.0289   0.0211  0.0366 0.0000            NaN
 first_author     24                              D_topic_bert 1178  0.0311   0.0231  0.0391 0.0000            NaN
 first_author     24 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.5144   0.4028  0.6263    NaN            NaN
 first_author     24   P_topic_bert = D_topic_bert / D_partner 1178  0.5534   0.4423  0.6605    NaN            NaN
 first_author     32                                 D_partner 1178  0.0601   0.0504  0.0700 0.0000            NaN
 first_author     32                             D_topic_mpnet 1178  0.0310   0.0229  0.0391 0.0000            NaN
 first_author     32                              D_topic_bert 1178  0.0381   0.0296  0.0466 0.0000            NaN
 first_author     32 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.5156   0.4080  0.6239    NaN            NaN
 first_author     32   P_topic_bert = D_topic_bert / D_partner 1178  0.6337   0.5319  0.7405    NaN            NaN
 first_author     40                                 D_partner 1178  0.0694   0.0608  0.0785 0.0000            NaN
 first_author     40                             D_topic_mpnet 1178  0.0366   0.0295  0.0445 0.0000            NaN
 first_author     40                              D_topic_bert 1178  0.0472   0.0394  0.0550 0.0000            NaN
 first_author     40 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.5277   0.4459  0.6149    NaN            NaN
 first_author     40   P_topic_bert = D_topic_bert / D_partner 1178  0.6797   0.5989  0.7640    NaN            NaN
 first_author     48                                 D_partner 1178  0.0246   0.0209  0.0284 0.0000            NaN
 first_author     48                             D_topic_mpnet 1178  0.0153   0.0119  0.0188 0.0000            NaN
 first_author     48                              D_topic_bert 1178  0.0192   0.0158  0.0225 0.0000            NaN
 first_author     48 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.6223   0.4964  0.7513    NaN            NaN
 first_author     48   P_topic_bert = D_topic_bert / D_partner 1178  0.7787   0.6667  0.9015    NaN            NaN
 first_author     56                                 D_partner 1178  0.0007   0.0001  0.0014 0.0290            NaN
 first_author     56                             D_topic_mpnet 1178  0.0007   0.0000  0.0015 0.0440            NaN
 first_author     56                              D_topic_bert 1178  0.0002  -0.0003  0.0008 0.4420            NaN
 first_author     56 P_topic_mpnet = D_topic_mpnet / D_partner 1178  1.0278  -0.1872  4.0424    NaN            NaN
 first_author     56   P_topic_bert = D_topic_bert / D_partner 1178  0.3208  -1.3317  1.6428    NaN            NaN
surname_first      8                                 D_partner 1178  0.0663   0.0452  0.0871 0.0000            NaN
surname_first      8                             D_topic_mpnet 1178  0.0163  -0.0035  0.0358 0.1160         0.2320
surname_first      8                              D_topic_bert 1178  0.0271   0.0058  0.0490 0.0100         0.0200
surname_first      8 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.2453  -0.0674  0.4931    NaN            NaN
surname_first      8   P_topic_bert = D_topic_bert / D_partner 1178  0.4085   0.1067  0.6780    NaN            NaN
surname_first     16                                 D_partner 1178  0.0839   0.0615  0.1057 0.0000            NaN
surname_first     16                             D_topic_mpnet 1178  0.0318   0.0123  0.0506 0.0020         0.0060
surname_first     16                              D_topic_bert 1178  0.0469   0.0268  0.0679 0.0000         0.0000
surname_first     16 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.3785   0.1703  0.5575    NaN            NaN
surname_first     16   P_topic_bert = D_topic_bert / D_partner 1178  0.5590   0.3648  0.7646    NaN            NaN
surname_first     24                                 D_partner 1178  0.0978   0.0758  0.1208 0.0000            NaN
surname_first     24                             D_topic_mpnet 1178  0.0438   0.0250  0.0640 0.0000         0.0000
surname_first     24                              D_topic_bert 1178  0.0588   0.0380  0.0808 0.0000         0.0000
surname_first     24 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.4483   0.2841  0.5992    NaN            NaN
surname_first     24   P_topic_bert = D_topic_bert / D_partner 1178  0.6007   0.4363  0.7669    NaN            NaN
surname_first     32                                 D_partner 1178  0.1028   0.0802  0.1272 0.0000            NaN
surname_first     32                             D_topic_mpnet 1178  0.0458   0.0267  0.0667 0.0000         0.0000
surname_first     32                              D_topic_bert 1178  0.0681   0.0472  0.0903 0.0000         0.0000
surname_first     32 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.4457   0.2853  0.5939    NaN            NaN
surname_first     32   P_topic_bert = D_topic_bert / D_partner 1178  0.6617   0.5022  0.8237    NaN            NaN
surname_first     40                                 D_partner 1178  0.1243   0.1021  0.1475 0.0000            NaN
surname_first     40                             D_topic_mpnet 1178  0.0629   0.0450  0.0826 0.0000         0.0000
surname_first     40                              D_topic_bert 1178  0.0871   0.0681  0.1094 0.0000         0.0000
surname_first     40 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.5063   0.3862  0.6198    NaN            NaN
surname_first     40   P_topic_bert = D_topic_bert / D_partner 1178  0.7006   0.5874  0.8200    NaN            NaN
surname_first     48                                 D_partner 1178  0.0371   0.0290  0.0465 0.0000            NaN
surname_first     48                             D_topic_mpnet 1178  0.0199   0.0119  0.0282 0.0000         0.0000
surname_first     48                              D_topic_bert 1178  0.0265   0.0185  0.0352 0.0000         0.0000
surname_first     48 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.5359   0.3653  0.6988    NaN            NaN
surname_first     48   P_topic_bert = D_topic_bert / D_partner 1178  0.7147   0.5517  0.8723    NaN            NaN
surname_first     56                                 D_partner 1178  0.0011  -0.0006  0.0028 0.2020            NaN
surname_first     56                             D_topic_mpnet 1178  0.0009  -0.0008  0.0027 0.2980         0.2980
surname_first     56                              D_topic_bert 1178  0.0000  -0.0015  0.0015 1.0000         1.0000
surname_first     56 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.8253  -3.4167  5.2768    NaN            NaN
surname_first     56   P_topic_bert = D_topic_bert / D_partner 1178  0.0057  -5.5628  5.0501    NaN            NaN
         year      8                                 D_partner 1178  0.0039   0.0005  0.0071 0.0270            NaN
         year      8                             D_topic_mpnet 1178  0.0043   0.0010  0.0074 0.0080            NaN
         year      8                              D_topic_bert 1178  0.0042   0.0008  0.0074 0.0190            NaN
         year      8 P_topic_mpnet = D_topic_mpnet / D_partner 1178  1.0852   0.2213  3.5116    NaN            NaN
         year      8   P_topic_bert = D_topic_bert / D_partner 1178  1.0645   0.1568  3.4995    NaN            NaN
         year     16                                 D_partner 1178  0.0020  -0.0010  0.0051 0.2040            NaN
         year     16                             D_topic_mpnet 1178  0.0023  -0.0010  0.0055 0.1560            NaN
         year     16                              D_topic_bert 1178  0.0016  -0.0016  0.0048 0.3100            NaN
         year     16 P_topic_mpnet = D_topic_mpnet / D_partner 1178  1.1158  -6.0142  7.3164    NaN            NaN
         year     16   P_topic_bert = D_topic_bert / D_partner 1178  0.7685  -3.7319  6.0045    NaN            NaN
         year     24                                 D_partner 1178  0.0047   0.0012  0.0080 0.0120            NaN
         year     24                             D_topic_mpnet 1178  0.0032   0.0002  0.0065 0.0450            NaN
         year     24                              D_topic_bert 1178  0.0038   0.0007  0.0069 0.0130            NaN
         year     24 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.6944  -0.0057  1.8461    NaN            NaN
         year     24   P_topic_bert = D_topic_bert / D_partner 1178  0.8250   0.2195  2.0866    NaN            NaN
         year     32                                 D_partner 1178  0.0071   0.0036  0.0106 0.0000            NaN
         year     32                             D_topic_mpnet 1178  0.0047   0.0012  0.0079 0.0080            NaN
         year     32                              D_topic_bert 1178  0.0065   0.0031  0.0098 0.0000            NaN
         year     32 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.6631   0.2254  1.2377    NaN            NaN
         year     32   P_topic_bert = D_topic_bert / D_partner 1178  0.9153   0.5152  1.6006    NaN            NaN
         year     40                                 D_partner 1178  0.0102   0.0070  0.0133 0.0000            NaN
         year     40                             D_topic_mpnet 1178  0.0081   0.0052  0.0113 0.0000            NaN
         year     40                              D_topic_bert 1178  0.0078   0.0047  0.0109 0.0000            NaN
         year     40 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.7941   0.5238  1.1244    NaN            NaN
         year     40   P_topic_bert = D_topic_bert / D_partner 1178  0.7594   0.5043  1.0793    NaN            NaN
         year     48                                 D_partner 1178  0.0073   0.0045  0.0099 0.0000            NaN
         year     48                             D_topic_mpnet 1178  0.0044   0.0021  0.0067 0.0000            NaN
         year     48                              D_topic_bert 1178  0.0054   0.0030  0.0079 0.0000            NaN
         year     48 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.5992   0.3385  0.9416    NaN            NaN
         year     48   P_topic_bert = D_topic_bert / D_partner 1178  0.7355   0.4356  1.1385    NaN            NaN
         year     56                                 D_partner 1178  0.0008  -0.0002  0.0018 0.1320            NaN
         year     56                             D_topic_mpnet 1178  0.0007  -0.0004  0.0018 0.2590            NaN
         year     56                              D_topic_bert 1178  0.0002  -0.0008  0.0012 0.6640            NaN
         year     56 P_topic_mpnet = D_topic_mpnet / D_partner 1178  0.8464  -3.0441  5.1445    NaN            NaN
         year     56   P_topic_bert = D_topic_bert / D_partner 1178  0.2932  -3.4518  3.9379    NaN            NaN

## Target − control within citation bins

          ans  layer             contrast     est      lo     hi
        field      8     T-C of D_partner  0.0092 -0.0875 0.0973
        field      8 T-C of D_topic_mpnet -0.0176 -0.0990 0.0623
        field     16     T-C of D_partner -0.0219 -0.1073 0.0646
        field     16 T-C of D_topic_mpnet -0.0379 -0.1144 0.0429
        field     24     T-C of D_partner -0.0325 -0.1134 0.0514
        field     24 T-C of D_topic_mpnet -0.0288 -0.1041 0.0459
        field     32     T-C of D_partner -0.0402 -0.1164 0.0369
        field     32 T-C of D_topic_mpnet -0.0388 -0.0992 0.0213
        field     40     T-C of D_partner -0.0348 -0.1032 0.0363
        field     40 T-C of D_topic_mpnet -0.0512 -0.1012 0.0003
        field     48     T-C of D_partner  0.0059 -0.0353 0.0457
        field     48 T-C of D_topic_mpnet -0.0009 -0.0310 0.0303
        field     56     T-C of D_partner  0.0037 -0.0012 0.0085
        field     56 T-C of D_topic_mpnet -0.0035 -0.0089 0.0018
 first_author      8     T-C of D_partner  0.0403  0.0228 0.0574
 first_author      8 T-C of D_topic_mpnet  0.0076 -0.0087 0.0239
 first_author     16     T-C of D_partner  0.0425  0.0255 0.0597
 first_author     16 T-C of D_topic_mpnet  0.0114 -0.0047 0.0266
 first_author     24     T-C of D_partner  0.0499  0.0330 0.0659
 first_author     24 T-C of D_topic_mpnet  0.0112 -0.0043 0.0266
 first_author     32     T-C of D_partner  0.0552  0.0381 0.0731
 first_author     32 T-C of D_topic_mpnet  0.0207  0.0048 0.0376
 first_author     40     T-C of D_partner  0.0603  0.0429 0.0776
 first_author     40 T-C of D_topic_mpnet  0.0284  0.0137 0.0447
 first_author     48     T-C of D_partner  0.0233  0.0158 0.0304
 first_author     48 T-C of D_topic_mpnet  0.0124  0.0051 0.0200
 first_author     56     T-C of D_partner  0.0003 -0.0011 0.0015
 first_author     56 T-C of D_topic_mpnet  0.0002 -0.0012 0.0016
surname_first      8     T-C of D_partner  0.0834  0.0418 0.1249
surname_first      8 T-C of D_topic_mpnet  0.0039 -0.0350 0.0440
surname_first     16     T-C of D_partner  0.1002  0.0590 0.1440
surname_first     16 T-C of D_topic_mpnet  0.0114 -0.0278 0.0511
surname_first     24     T-C of D_partner  0.1179  0.0769 0.1637
surname_first     24 T-C of D_topic_mpnet  0.0197 -0.0186 0.0601
surname_first     32     T-C of D_partner  0.1245  0.0811 0.1726
surname_first     32 T-C of D_topic_mpnet  0.0291 -0.0101 0.0725
surname_first     40     T-C of D_partner  0.1465  0.1022 0.1939
surname_first     40 T-C of D_topic_mpnet  0.0738  0.0357 0.1168
surname_first     48     T-C of D_partner  0.0443  0.0274 0.0620
surname_first     48 T-C of D_topic_mpnet  0.0223  0.0060 0.0398
surname_first     56     T-C of D_partner  0.0015 -0.0017 0.0049
surname_first     56 T-C of D_topic_mpnet  0.0015 -0.0020 0.0050
         year      8     T-C of D_partner  0.0003 -0.0062 0.0073
         year      8 T-C of D_topic_mpnet  0.0041 -0.0029 0.0109
         year     16     T-C of D_partner  0.0026 -0.0037 0.0091
         year     16 T-C of D_topic_mpnet  0.0011 -0.0057 0.0077
         year     24     T-C of D_partner  0.0044 -0.0019 0.0113
         year     24 T-C of D_topic_mpnet  0.0005 -0.0062 0.0069
         year     32     T-C of D_partner  0.0040 -0.0030 0.0106
         year     32 T-C of D_topic_mpnet  0.0016 -0.0052 0.0082
         year     40     T-C of D_partner  0.0019 -0.0048 0.0088
         year     40 T-C of D_topic_mpnet  0.0010 -0.0052 0.0076
         year     48     T-C of D_partner -0.0023 -0.0075 0.0026
         year     48 T-C of D_topic_mpnet -0.0034 -0.0081 0.0010
         year     56     T-C of D_partner  0.0010 -0.0009 0.0030
         year     56 T-C of D_topic_mpnet -0.0003 -0.0023 0.0018
