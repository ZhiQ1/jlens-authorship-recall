# Addendum 21 (injection / sufficiency test) texts for the docs, 2026-11-21. Numbers from 391_groups/summary_a21/ (verified).
SRC = '补充 21，2026-11-21 13:18 锁定，391_groups/config/prereg_addendum21.md sha256 bdbf80bd…；391_groups/summary_a21/ a21_results.json、primary.csv、rates.csv、tf.csv；1,200 篇（A 600、B 600），团队整群 bootstrap 2,000 次，Holm 校正 6 格'
SRC_EN = 'addendum 21, locked 2026-11-21 13:18, 391_groups/config/prereg_addendum21.md sha256 bdbf80bd…; 391_groups/summary_a21/; 1,200 papers (A 600, B 600), team-cluster bootstrap 2,000 draws, Holm over 6 cells'
A21 = ('<b>注入检验（补充 21，锁定的确认性检验，2026-11-21；结论 C37）：已经到达的信息够不够让模型写出作者？</b>'
       '在 1,200 篇（A 600 认得出·R0，B 600 认不出·R0；补充 16 B 样本）上，在提示尾部 L48 或 L52 的块输出加 β·Δ'
       '（Δ = 这篇论文真标题状态 − 5 个假标题状态均值，β = 1、2、4），对照为同范数的另一篇论文（同领域、同引用档）的 Δ 和随机方向。'
       '主指标是 A 组开放生成写对至少一位作者全名的比例。按锁定规则判为<b>不支持</b>：基线 3.8%；G = 自己 − 基线 在 6 格中 −0.010 到 +0.005，'
       'Holm 校正区间都含 0；S = 自己 − 另一篇 −0.002 到 +0.020（最大 L52 β2 +0.020 [0.003, 0.037]，未校正；Holm p 0.15）。'
       '次要（描述性）：teacher-forcing 下真名字的输出 log10(1/名次) 随 β 下降（A：L48 β4 −0.054 [−0.061, −0.047]，L52 β4 −0.102 [−0.113, −0.092]），'
       '与放大另一篇论文的分量相近（自己 − 另一篇 L52 β4 +0.012 [−0.002, +0.026]），是一般性损伤而不是论文特异的帮助；B 组相同。'
       '<b>读法：说不出不只是信号太弱——加强已经到达的信息不能让模型写出作者，瓶颈在后段把信息转成名字这一步（C29、C30）。</b>')
A21s = ('<b>注入检验（补充 21，锁定，2026-11-21；C37）：</b>把这篇论文已经到达的信息在 L48 / L52 放大 1、2、4 倍，'
        '认得出的论文写对作者的比例没有提高（基线 3.8%；自己 − 基线 −0.010 到 +0.005，Holm 区间都含 0；1,200 篇），判为<b>不支持</b>；'
        '放大只会让真名字的名次变差（L52 β4 −0.102 [−0.113, −0.092]），放大另一篇论文的分量也一样。说不出不只是信号太弱，卡在后段转成名字这一步。')
NOTE = '补充 21 第一次 gate 只覆盖了 30 个分片中的 24 个（953 篇，结论相同），补齐分片后在全部 1,200 篇上重算，以 1,200 篇为准。'
A21_EN = ('<b>Injection test (addendum 21, locked confirmatory, 2026-11-21; C37): is the arrived information enough for the model to write the author?</b> '
          'On 1,200 papers (A 600 recognised · R0, B 600 not recognised · R0), the block output at the prompt tail at L48 or L52 got + β·Δ '
          '(Δ = the paper\'s true-title state minus the mean of its 5 false-title states; β = 1, 2, 4), against equal-norm controls: another paper\'s Δ '
          '(same field and citation bin) and a random direction. Primary: group A writes ≥ 1 true author in full. By the locked rule: <b>not supported</b>. '
          'Baseline 3.8%; G = own − base −0.010 to +0.005 in the 6 cells, all Holm intervals include 0; S = own − other −0.002 to +0.020 '
          '(largest L52 β2 +0.020 [0.003, 0.037] unadjusted, Holm p 0.15). Teacher-forced output log10(1/rank) of the true name falls with β '
          '(L52 β4 −0.102 [−0.113, −0.092]) about as much as with another paper\'s Δ: generic damage, not paper-specific help. '
          '<b>Reading: not saying is not just a weak signal; strengthening what has arrived does not unlock the name — the bottleneck is the late conversion (C29, C30).</b>')
