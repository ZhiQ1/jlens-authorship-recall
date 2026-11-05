"""Handbook update 2026-11-05: new part K (答辩后新增, from the report v27 fragment), first-token caveat at E4b (D 11-7, 11-8),
status notes at M5 / X2 / X5 (F), header date. Backups *.before_20261105b.*. Then run build_methods.py."""
import re, shutil, base64, csv, html, os
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/methods'); P = D / 'parts'
def bk(p):
    b = p.with_name(p.stem + '.before_20261105b' + p.suffix)
    if not b.exists(): shutil.copy2(p, b)
    return b.read_text(encoding='utf-8')          # always edit from the backup (idempotent)
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:60]); return s.replace(a, b)

CAV = ('<div class="fix"><b>注意（2026-11-05 补）：E4b 只给每位作者名字的第一个 token 打分</b>（gold = 每位作者的第 1 个名字 token；73% 的名字以首字母开头，'
       '所以多数时候打分的是首字母，不是整个名字）<span class="src">stage11_analyze.py:163–171；本节“步骤”</span>。下文所有 E4b 数字（含按团队分折、剔除标题复用、训练折标准化的确认版）'
       '都只代表第一个名字 token。给全部名字 token 打分、按首字母 / 名 / 姓分开的版本按预注册补充 9 进行中'
       '<span class="src">381_stage13/config/prereg_addendum9.json（sha256 a9896357…）</span>，尚无结果；见 <a href="#k-running">十一 · 进行中</a>。</div>')

# --- D: E4b caveat
s = bk(P / 'D_stage10_11.html')
for hid in ['s1011-s11-e4b', 's1011-s11-e4b-check']:
    m = re.search(r'<h3 id="%s"[^>]*>.*?</h3>' % re.escape(hid), s, re.S); assert m, hid
    s = s[:m.end()] + '\n' + CAV + s[m.end():]
for o, n in [('R0 view final 标题特异 +0.199 [0.187, 0.212]', 'R0 view final 标题特异 +0.199 [0.188, 0.212]'), ('C − A +0.110 [0.086, 0.133]', 'C − A +0.110 [0.086, 0.135]'),
             ('"L48 恢复 83%"= all 0.825', '"L48 恢复 82%"= all 0.825')]:
    s = rep(s, o, n)
s = s.replace('（485 / 3,', '（r0_sensitivity.md；485 / 3,', 1)
(P / 'D_stage10_11.html').write_text(s, encoding='utf-8')

# --- F: status notes
s = bk(P / 'F_stage13.html')
NOTES = {
 's13-m5': '<div class="fix"><b>2026-11-05 补（事后分析）：</b>M5 中能用已有数据回答的部分已做（名字位置上的真假标题判别，lens 读出；标题 / “:” 位置用 probe 区分真标题与 false_0 运行），在名字位置做 probe / patchscope 需要新的 GPU 运行，未提交。结果见 <a href="#k-cpu">十一 · CPU 补充</a>。<span class="src">381_stage13/reports/m5_report.md</span></div>',
 's13-x2': '<div class="fix"><b>2026-11-05 状态：</b>按预注册补充 6 恢复（用户 2026-11-05 同意）：子空间已拟合，24 个 GPU shard 中第 0 个完成并通过检查，其余排在分组重跑之后。尚无结果。见 <a href="#k-running">十一 · 进行中</a>。<span class="src">381_stage13/config/prereg_addendum6.json（sha256 5eea3c4a…）；381_stage13/raw/x2/shard_000.npz</span></div>',
 's13-x5': '<div class="fix"><b>2026-11-05 补：</b>预注册的跨任务 top-1 检索曲线已补算（CPU，M3 残差缓存）：没有一层高于 L4 文字水平。见 <a href="#k-cpu">十一 · CPU 补充</a>。<span class="src">381_stage13/reports/x5_retrieval.md</span></div>',
}
for hid, note in NOTES.items():
    m = re.search(r'<h3 id="%s"[^>]*>.*?</h3>' % re.escape(hid), s, re.S); assert m, hid
    s = s[:m.end()] + '\n' + note + s[m.end():]
(P / 'F_stage13.html').write_text(s, encoding='utf-8')

# --- C, G: wording decisions (2026-11-05 afternoon)
s = bk(P / 'C_stage1_9.html'); s = rep(s, '重算，与报告一致；报告原始出处文件未找到）', '重算，与报告一致）'); (P / 'C_stage1_9.html').write_text(s, encoding='utf-8')
s = bk(P / 'G_appendix.html'); s = rep(s, 'L48 恢复 83%、L52 100%', 'L48 恢复 82%、L52 100%'); (P / 'G_appendix.html').write_text(s, encoding='utf-8')

# --- K: post-defence part, from the report fragment
fr = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/stage1_11/src/post_defence_v27.html').read_text(encoding='utf-8')
fr = re.sub(r'<div class="partbar".*?</div>\s*<div class="p19"><main>', '', fr, flags=re.S)
fr = fr.replace('</main></div>', '')
fr = fr.replace('<section id="pd-groups"><h2>', '<h3 id="k-groups">').replace('<section id="pd-cpu"><h2>', '<h3 id="k-cpu">').replace('<section id="pd-running"><h2>', '<h3 id="k-running">')
fr = re.sub(r'</h2>', '</h3>', fr); fr = fr.replace('</section>', '')
fr = re.sub(r'<h3>', '<h4>', fr); fr = re.sub(r'<h3>(.*?)</h3>', r'<h4>\1</h4>', fr)
# h3 without id were turned into h4 above; close tags of those: fix pairing
fr = re.sub(r'<h4>(.*?)</h3>', r'<h4>\1</h4>', fr, flags=re.S)
fr = fr.replace('<span class="ln lA">A 这篇论文？</span>', '').replace('<span class="ln lC">C 哪一层</span>', '')
fr = re.sub(r'<span class="st">([^<]*)</span>', r'<span class="st st-done">\1</span>', fr)
fr = fr.replace('<span class="st st-done">进行中</span>', '<span class="st st-plan">进行中</span>')
fr = fr.replace('<div class="bx">', '<div class="fix">').replace('<table>', '<table class="t">')
fr = fr.replace('见第四部分的说明', '见本手册 M5 节')
assert 'p19' not in fr
G = '/scratch/zhang.zhiqi2/jlens/391_groups'
for key, fn in [('{{FIG2}}', 'fig2_signal_vs_mc.png'), ('{{FIG3}}', 'fig3_primary_contrasts.png')]:
    fr = fr.replace(key, 'data:image/png;base64,' + base64.b64encode(open(f'{G}/figures/{fn}', 'rb').read()).decode())
rows = list(csv.reader(open(f'{G}/summary_table.csv', encoding='utf-8')))
H = ['组', '输出层信号，未写出作者（L63）', '输出层信号，写出的作者（参照）', 'E1 恢复 L48（未写出）', 'E1 恢复 L52（未写出）', 'E2 阻断损失 L52（未写出）',
     'E4b probe 标题特异 L40（只打分第一个名字 token）', 'M2“认得出”AUROC（对 B，“:” L52，描述）', 'X3 行为恢复，测试集（第一作者未写出）']
t = '<div class="tw"><table class="t"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in H) + '</tr></thead><tbody>' + ''.join(
    '<tr>' + ''.join(f'<td>{html.escape(c)}</td>' for c in r) + '</tr>' for r in rows[1:]) + '</tbody></table></div>'
fr = fr.replace('{{SUMMARY_TABLE}}', '<p class="note">表 P5.1 各组汇总</p>' + t)
assert '{{' not in fr
K = ('<section id="k-post"><h2>十一 答辩后新增（2026-11-05）</h2>\n'
     '<p class="lead">答辩材料 2026-11-02/03 定稿之后的工作。分组对比的分析计划在看结果前写定（补充 7、8）；其余 CPU 补充分析是事后分析，只作描述；进行中的实验只写状态。'
     '与《Stage 1–13 实验报告》第 27 版第五部分内容相同（图号、表号沿用报告）。</p>\n' + fr + '\n</section>')
(P / 'K_post_defence.html').write_text(K, encoding='utf-8')

# --- builder: add part K, header date
s = bk(D / 'build_methods.py')
s = rep(s, "('J_dua_package.html', '十 附表：Dreaming Up Authors 代码包核对')]",
        "('J_dua_package.html', '十 附表：Dreaming Up Authors 代码包核对'), ('K_post_defence.html', '十一 答辩后新增（2026-11-05）')]")
s = rep(s, '方法答辩用 · 2026-11-03 定稿', '方法答辩用 · 2026-11-03 定稿，2026-11-05 补充（第十一部分：答辩后新增；E4b 只打分第一个名字 token 的说明）')
(D / 'build_methods.py').write_text(s, encoding='utf-8')
print('ok')
