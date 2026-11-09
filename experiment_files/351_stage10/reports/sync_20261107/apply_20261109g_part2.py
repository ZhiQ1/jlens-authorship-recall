"""Round g, part 2: note 81 overflowed (969 px, job 11759920) after the longer batch-2 status. Shorter status in note 81 only; same facts. Appends to the manifest."""
import json
from pathlib import Path
R = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports'); N = R / 'talk/src/export/notes_zh.json'; d = json.loads(N.read_text(encoding='utf-8'))
a = ('X3 按 token 角色（2-3）、E1 批量舍入噪声（2-4）、E1t 用 5 个假标题（2-8）、M3 全部 token 分数（2-10）已完成；Patchscope（2-7、2-9）和名字位置 probe 的最终分析进行中；'
     '2-1 Fit B 门槛重跑中（集群作业结束脚本误杀，已加看护作业）；其余各项进行中')
b = '2-3、2-4、2-8、2-10 已完成；Patchscope 和名字位置 probe 最终分析进行中；2-1 门槛重跑中（作业被误杀，已加看护）'
assert d['81']['text'].count(a) == 1; d['81']['text'] = d['81']['text'].replace(a, b)
c = '（2-1、2-2 用较省但包含原始提示逐位复现重拟合的硬检查；2-11 重建标签、论文内 AUROC、两个基线、对照组只作描述）'
N.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8'); json.loads(N.read_text(encoding='utf-8'))
with open(R / 'sync_20261108c_manifest.md', 'a', encoding='utf-8') as fh: fh.write(f'| g2-1 | notes_zh.json #81 (overflow) | {a} | {b} | 1 |\n')
print('ok')
