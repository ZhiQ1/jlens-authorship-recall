# Addendum 33 (LOCKED) — X4 surname signal, confirmatory

**Paper-specific:** paper-specific surname signal confirmed (T1 and T2 Holm CI > 0)
**Recognition:** recognition-specific (T3 Holm CI > 0)

prereg sha256 7a28ae2d1620b083103c314351761591037561080ac1220ec817759ab5a27532; missing shards []; 50-paper protocol check {"rows": 7574, "papers": 50, "exact_share": 1.0, "max_abs": 0.0, "mean_abs": 0.0, "status": "OK"}

## Sample (frozen before any run)

{
 "cohort": 9108,
 "outside_stage11_sample": 7922,
 "target_or_control": 6714,
 "with_context_and_field": 6714,
 "no_partner_any": 40,
 "with_all_partners": 6674,
 "flag_a": 11,
 "flag_b": 30,
 "flag_c": 596,
 "excluded_any": 626,
 "primary_n": 6048,
 "primary_with_surname_first": 6048,
 "by_group_all": {
  "target": 5053,
  "control": 1621
 },
 "by_group_primary": {
  "target": 4577,
  "control": 1471
 }
}

## Primary tests (team bootstrap 2,000, seed 33; Holm over T1–T3; Holm CI at α/(m − rank))

                                                     test    est    n      p  p_holm     lo     hi  holm_lo  holm_hi  z_qwen  z_text
                     T1 D_topic_mpnet (surname_first, L8) 0.0457 6048 0.0000  0.0000 0.0353 0.0559   0.0329   0.0583     NaN     NaN
         T2 standardised Qwen D_topic − BERT text D_topic 0.0448 6048 0.0170  0.0340 0.0078 0.0824   0.0025   0.0870  0.1136  0.0687
T3 target − control of D_topic_mpnet within citation bins 0.0246 6048 0.0220  0.0340 0.0030 0.0470   0.0030   0.0470     NaN     NaN

## Secondary (descriptive)

          ans  layer                       contrast    n     est       lo      hi
surname_first      8                      D_partner 6048  0.1031   0.0915  0.1141
surname_first      8                  D_topic_mpnet 6048  0.0457   0.0353  0.0559
surname_first      8                   D_topic_bert 6048  0.0672   0.0569  0.0772
surname_first      8               D_topic_mpnet_L0 6048  0.0012  -0.0012  0.0036
surname_first      8 P = ΣD_topic_mpnet / ΣD_random 6048  0.4432   0.3573  0.5211
surname_first      8           T−C of D_topic_mpnet 6048  0.0246   0.0030  0.0470
surname_first     16                      D_partner 6048  0.1188   0.1071  0.1298
surname_first     16                  D_topic_mpnet 6048  0.0558   0.0459  0.0661
surname_first     16                   D_topic_bert 6048  0.0795   0.0694  0.0895
surname_first     16               D_topic_mpnet_L0 6048  0.0000  -0.0020  0.0021
surname_first     16 P = ΣD_topic_mpnet / ΣD_random 6048  0.4695   0.3997  0.5358
surname_first     16           T−C of D_topic_mpnet 6048  0.0257   0.0036  0.0472
surname_first     24                      D_partner 6048  0.1337   0.1216  0.1452
surname_first     24                  D_topic_mpnet 6048  0.0659   0.0557  0.0761
surname_first     24                   D_topic_bert 6048  0.0929   0.0826  0.1034
surname_first     24               D_topic_mpnet_L0 6048  0.0006  -0.0011  0.0024
surname_first     24 P = ΣD_topic_mpnet / ΣD_random 6048  0.4926   0.4305  0.5497
surname_first     24           T−C of D_topic_mpnet 6048  0.0349   0.0132  0.0569
surname_first     32                      D_partner 6048  0.1463   0.1334  0.1588
surname_first     32                  D_topic_mpnet 6048  0.0758   0.0650  0.0862
surname_first     32                   D_topic_bert 6048  0.1053   0.0945  0.1166
surname_first     32               D_topic_mpnet_L0 6048 -0.0017  -0.0041  0.0006
surname_first     32 P = ΣD_topic_mpnet / ΣD_random 6048  0.5185   0.4622  0.5727
surname_first     32           T−C of D_topic_mpnet 6048  0.0501   0.0279  0.0722
surname_first     40                      D_partner 6048  0.1592   0.1468  0.1716
surname_first     40                  D_topic_mpnet 6048  0.0928   0.0826  0.1031
surname_first     40                   D_topic_bert 6048  0.1182   0.1066  0.1293
surname_first     40               D_topic_mpnet_L0 6048 -0.0001  -0.0018  0.0017
surname_first     40 P = ΣD_topic_mpnet / ΣD_random 6048  0.5827   0.5352  0.6294
surname_first     40           T−C of D_topic_mpnet 6048  0.0671   0.0465  0.0868
surname_first     48                      D_partner 6048  0.0462   0.0411  0.0510
surname_first     48                  D_topic_mpnet 6048  0.0270   0.0227  0.0312
surname_first     48                   D_topic_bert 6048  0.0347   0.0304  0.0392
surname_first     48               D_topic_mpnet_L0 6048 -0.0000  -0.0010  0.0009
surname_first     48 P = ΣD_topic_mpnet / ΣD_random 6048  0.5849   0.5184  0.6489
surname_first     48           T−C of D_topic_mpnet 6048  0.0151   0.0068  0.0229
surname_first     56                      D_partner 6048  0.0005  -0.0002  0.0012
surname_first     56                  D_topic_mpnet 6048  0.0002  -0.0005  0.0009
surname_first     56                   D_topic_bert 6048  0.0009   0.0002  0.0016
surname_first     56               D_topic_mpnet_L0 6048 -0.0001  -0.0008  0.0005
surname_first     56 P = ΣD_topic_mpnet / ΣD_random 6048  0.4537  -5.4771  4.8439
surname_first     56           T−C of D_topic_mpnet 6048 -0.0017  -0.0038  0.0005
 first_author      8                      D_partner 6048  0.0564   0.0521  0.0607
 first_author      8                  D_topic_mpnet 6048  0.0235   0.0195  0.0275
 first_author      8                   D_topic_bert 6048  0.0340   0.0300  0.0383
 first_author      8               D_topic_mpnet_L0 6048 -0.0002  -0.0014  0.0010
 first_author      8 P = ΣD_topic_mpnet / ΣD_random 6048  0.4159   0.3571  0.4732
 first_author      8           T−C of D_topic_mpnet 6048  0.0217   0.0128  0.0302
 first_author     16                      D_partner 6048  0.0610   0.0565  0.0653
 first_author     16                  D_topic_mpnet 6048  0.0275   0.0237  0.0315
 first_author     16                   D_topic_bert 6048  0.0388   0.0348  0.0428
 first_author     16               D_topic_mpnet_L0 6048 -0.0002  -0.0012  0.0009
 first_author     16 P = ΣD_topic_mpnet / ΣD_random 6048  0.4513   0.4013  0.5002
 first_author     16           T−C of D_topic_mpnet 6048  0.0250   0.0164  0.0336
 first_author     24                      D_partner 6048  0.0653   0.0608  0.0698
 first_author     24                  D_topic_mpnet 6048  0.0314   0.0276  0.0352
 first_author     24                   D_topic_bert 6048  0.0422   0.0380  0.0463
 first_author     24               D_topic_mpnet_L0 6048  0.0002  -0.0007  0.0011
 first_author     24 P = ΣD_topic_mpnet / ΣD_random 6048  0.4810   0.4367  0.5260
 first_author     24           T−C of D_topic_mpnet 6048  0.0278   0.0197  0.0363
 first_author     32                      D_partner 6048  0.0716   0.0669  0.0765
 first_author     32                  D_topic_mpnet 6048  0.0363   0.0322  0.0404
 first_author     32                   D_topic_bert 6048  0.0479   0.0434  0.0521
 first_author     32               D_topic_mpnet_L0 6048  0.0002  -0.0011  0.0013
 first_author     32 P = ΣD_topic_mpnet / ΣD_random 6048  0.5069   0.4640  0.5503
 first_author     32           T−C of D_topic_mpnet 6048  0.0303   0.0217  0.0386
 first_author     40                      D_partner 6048  0.0777   0.0730  0.0821
 first_author     40                  D_topic_mpnet 6048  0.0421   0.0384  0.0459
 first_author     40                   D_topic_bert 6048  0.0548   0.0507  0.0586
 first_author     40               D_topic_mpnet_L0 6048 -0.0004  -0.0012  0.0005
 first_author     40 P = ΣD_topic_mpnet / ΣD_random 6048  0.5427   0.5072  0.5793
 first_author     40           T−C of D_topic_mpnet 6048  0.0351   0.0273  0.0431
 first_author     48                      D_partner 6048  0.0260   0.0241  0.0279
 first_author     48                  D_topic_mpnet 6048  0.0161   0.0145  0.0178
 first_author     48                   D_topic_bert 6048  0.0195   0.0179  0.0213
 first_author     48               D_topic_mpnet_L0 6048  0.0001  -0.0003  0.0005
 first_author     48 P = ΣD_topic_mpnet / ΣD_random 6048  0.6188   0.5709  0.6668
 first_author     48           T−C of D_topic_mpnet 6048  0.0140   0.0104  0.0177
 first_author     56                      D_partner 6048  0.0004   0.0001  0.0007
 first_author     56                  D_topic_mpnet 6048  0.0004   0.0001  0.0007
 first_author     56                   D_topic_bert 6048  0.0004   0.0001  0.0007
 first_author     56               D_topic_mpnet_L0 6048 -0.0001  -0.0004  0.0002
 first_author     56 P = ΣD_topic_mpnet / ΣD_random 6048  0.8962   0.1898  2.5711
 first_author     56           T−C of D_topic_mpnet 6048 -0.0001  -0.0010  0.0007
         year      8                      D_partner 6048  0.0016   0.0001  0.0031
         year      8                  D_topic_mpnet 6048  0.0013  -0.0001  0.0027
         year      8                   D_topic_bert 6048  0.0024   0.0010  0.0038
         year      8 P = ΣD_topic_mpnet / ΣD_random 6048  0.7881  -0.3777  2.6620
         year      8           T−C of D_topic_mpnet 6048 -0.0015  -0.0054  0.0024
         year     16                      D_partner 6048  0.0005  -0.0008  0.0020
         year     16                  D_topic_mpnet 6048  0.0013  -0.0000  0.0026
         year     16                   D_topic_bert 6048  0.0013   0.0000  0.0027
         year     16 P = ΣD_topic_mpnet / ΣD_random 6048  2.4141 -17.8996 20.7527
         year     16           T−C of D_topic_mpnet 6048 -0.0008  -0.0045  0.0028
         year     24                      D_partner 6048  0.0007  -0.0008  0.0021
         year     24                  D_topic_mpnet 6048  0.0003  -0.0010  0.0016
         year     24                   D_topic_bert 6048  0.0020   0.0006  0.0033
         year     24 P = ΣD_topic_mpnet / ΣD_random 6048  0.3981  -7.7189  5.9450
         year     24           T−C of D_topic_mpnet 6048 -0.0016  -0.0052  0.0021
         year     32                      D_partner 6048  0.0043   0.0026  0.0059
         year     32                  D_topic_mpnet 6048  0.0037   0.0022  0.0053
         year     32                   D_topic_bert 6048  0.0046   0.0030  0.0061
         year     32 P = ΣD_topic_mpnet / ΣD_random 6048  0.8746   0.5825  1.2939
         year     32           T−C of D_topic_mpnet 6048  0.0019  -0.0022  0.0059
         year     40                      D_partner 6048  0.0115   0.0101  0.0129
         year     40                  D_topic_mpnet 6048  0.0095   0.0082  0.0108
         year     40                   D_topic_bert 6048  0.0091   0.0078  0.0104
         year     40 P = ΣD_topic_mpnet / ΣD_random 6048  0.8272   0.7254  0.9470
         year     40           T−C of D_topic_mpnet 6048  0.0023  -0.0010  0.0061
         year     48                      D_partner 6048  0.0061   0.0050  0.0072
         year     48                  D_topic_mpnet 6048  0.0043   0.0033  0.0053
         year     48                   D_topic_bert 6048  0.0052   0.0041  0.0063
         year     48 P = ΣD_topic_mpnet / ΣD_random 6048  0.7000   0.5549  0.8640
         year     48           T−C of D_topic_mpnet 6048  0.0018  -0.0010  0.0047
         year     56                      D_partner 6048 -0.0004  -0.0009  0.0001
         year     56                  D_topic_mpnet 6048 -0.0003  -0.0008  0.0001
         year     56                   D_topic_bert 6048 -0.0003  -0.0008  0.0001
         year     56 P = ΣD_topic_mpnet / ΣD_random 6048  0.8657  -1.6293  5.0737
         year     56           T−C of D_topic_mpnet 6048  0.0003  -0.0009  0.0016
        field      8                      D_partner 6048 -0.0047  -0.0252  0.0166
        field      8                  D_topic_mpnet 6048 -0.0209  -0.0388 -0.0019
        field      8                   D_topic_bert 6048 -0.0256  -0.0432 -0.0069
        field      8 P = ΣD_topic_mpnet / ΣD_random 6048  4.4479 -25.2869 23.1164
        field      8           T−C of D_topic_mpnet 6048  0.0017  -0.0500  0.0524
        field     16                      D_partner 6048 -0.0117  -0.0309  0.0086
        field     16                  D_topic_mpnet 6048 -0.0295  -0.0468 -0.0117
        field     16                   D_topic_bert 6048 -0.0221  -0.0393 -0.0052
        field     16 P = ΣD_topic_mpnet / ΣD_random 6048  2.5148 -13.7313 19.1800
        field     16           T−C of D_topic_mpnet 6048 -0.0048  -0.0530  0.0435
        field     24                      D_partner 6048 -0.0087  -0.0276  0.0103
        field     24                  D_topic_mpnet 6048 -0.0237  -0.0402 -0.0071
        field     24                   D_topic_bert 6048 -0.0293  -0.0448 -0.0137
        field     24 P = ΣD_topic_mpnet / ΣD_random 6048  2.7181 -19.5546 22.2392
        field     24           T−C of D_topic_mpnet 6048  0.0041  -0.0386  0.0469
        field     32                      D_partner 6048 -0.0042  -0.0204  0.0124
        field     32                  D_topic_mpnet 6048 -0.0287  -0.0419 -0.0159
        field     32                   D_topic_bert 6048 -0.0358  -0.0484 -0.0226
        field     32 P = ΣD_topic_mpnet / ΣD_random 6048  6.7856 -44.0745 53.8453
        field     32           T−C of D_topic_mpnet 6048  0.0043  -0.0315  0.0407
        field     40                      D_partner 6048 -0.0094  -0.0238  0.0067
        field     40                  D_topic_mpnet 6048 -0.0372  -0.0474 -0.0267
        field     40                   D_topic_bert 6048 -0.0469  -0.0568 -0.0356
        field     40 P = ΣD_topic_mpnet / ΣD_random 6048  3.9700 -28.0273 51.1309
        field     40           T−C of D_topic_mpnet 6048  0.0100  -0.0173  0.0387
        field     48                      D_partner 6048 -0.0046  -0.0129  0.0050
        field     48                  D_topic_mpnet 6048 -0.0133  -0.0197 -0.0067
        field     48                   D_topic_bert 6048 -0.0171  -0.0237 -0.0101
        field     48 P = ΣD_topic_mpnet / ΣD_random 6048  2.9249 -31.1488 23.6938
        field     48           T−C of D_topic_mpnet 6048 -0.0062  -0.0246  0.0123
        field     56                      D_partner 6048  0.0001  -0.0009  0.0012
        field     56                  D_topic_mpnet 6048 -0.0013  -0.0023 -0.0002
        field     56                   D_topic_bert 6048  0.0010   0.0001  0.0020
        field     56 P = ΣD_topic_mpnet / ΣD_random 6048 -8.6369 -37.7763 33.1656
        field     56           T−C of D_topic_mpnet 6048 -0.0029  -0.0060  0.0000
surname_first      8      T1 with exclusions lifted 6674  0.0442   0.0346  0.0545
