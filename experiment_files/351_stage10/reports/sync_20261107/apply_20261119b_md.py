"""2026-11-19 b: user's exact wording for bottleneck C (fabricated names) in conclusions (+ repo copy), STATUS, README. Run after apply_20261119_a18b_md.py."""
import re
ZH = '编造的名字约一半不在数据中，与打乱基线相同（50.4% vs 50.5%）；是合作者的只有 4.0%（随机 1.3%）'
EN = 'about half are not in the data, the same as the shuffled baseline (50.4% vs 50.5%); co-authors are only 4.0% (chance 1.3%)'
def R(t, a, b, n=1):
    assert t.count(a) == n, (a[:60], t.count(a)); return t.replace(a, b)
cf = '/home/zhang.zhiqi2/jlens_work/conclusions_v30_draft.md'; t = open(cf, encoding='utf-8').read()
t = R(t, '瓶颈 C（邻居混淆）不支持：编造的名字大多来自数据中不存在的人（事后，已有数据）', '瓶颈 C（邻居混淆）不支持：' + ZH + '（事后，已有数据）')
t = R(t, '- **结论**（用户 2026-11-17 确定的措辞）：不支持——编造的名字大多来自数据中不存在的人（50.4% [49.0, 51.7] 不在数据中）；合作者比例 4.0% [3.0, 5.2] 高于同领域打乱基线 1.3%，但改用',
      '- **结论**（用户 2026-11-17 确定的措辞，2026-11-19 用户改定前半句）：不支持——' + ZH + '；改用')
t = R(t, '编造的名字大多来自数据中不存在的人（50.4% [49.0, 51.7]）；合作者 4.0% 对同领域打乱 1.3%，但全名键', ZH + '；全名键')
t = R(t, 'C27：不支持，编造的名字大多来自数据中不存在的人。', 'C27：不支持，' + ZH + '（2026-11-19 用户改定措辞）。')
t = t.replace('**新增**；同时更新"进行中"中补充 18b 一条和第五节对照表。\n',
  '**新增**；同时更新"进行中"中补充 18b 一条和第五节对照表。\n21. **C27 措辞（2026-11-19，用户改定）**：前半句改为"' + ZH + '"，数字不变。**措辞**。\n', 1)
open(cf, 'w', encoding='utf-8').write(t)
open('/scratch/zhang.zhiqi2/jlens-authorship-recall_update/docs/conclusions_v30.md', 'w', encoding='utf-8').write(t)
sf = '/scratch/zhang.zhiqi2/jlens/STATUS.md'; t = open(sf, encoding='utf-8').read()
t = re.sub(r'fabricated names mostly come from people who do not exist in the data \(50\.4% \[49\.0, 51\.7\] not in the data; co-author 4\.0% \[3\.0, 5\.2\] vs shuffled same-field 1\.3%, but with (.*?) ≈ 0\)',
           lambda m: EN + '; with ' + m.group(1) + ' ≈ 0', t, count=1)
assert EN in t
t = t.replace('00000000000000. **2026-11-19 — addendum 18b', '000000000000000. **2026-11-19 b — user decisions synced locally:** C27 wording "' + EN + '"; C29 → settled; report/handbook process chapters dissolved by topic (report part 5 = limitations only; handbook 十一 removed); item-2 step-2 doc spots marked for the fix rerun.\n\n00000000000000. **2026-11-19 — addendum 18b', 1)
open(sf, 'w', encoding='utf-8').write(t)
rf = '/scratch/zhang.zhiqi2/jlens-authorship-recall_update/README.md'; t = open(rf, encoding='utf-8').read()
t = R(t, 'not supported — fabricated names mostly come from people who do not exist in the data (50.4% [49.0, 51.7]); co-authors 4.0% vs shuffled same-field 1.3%, but with', 'not supported — ' + EN + '; with')
t = R(t, 'not supported: mostly people not in the data (50.4% [49.0, 51.7]); co-author 4.0% vs shuffled 1.3%, target', 'not supported: ' + EN + '; target')
open(rf, 'w', encoding='utf-8').write(t)
print('ok')
