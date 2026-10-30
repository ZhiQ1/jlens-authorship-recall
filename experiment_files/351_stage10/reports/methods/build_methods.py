"""Assemble the methods handbook from parts/*.html into methods_handbook.html (publish body, no <html> skeleton)."""
import re, html
from pathlib import Path

D = Path(__file__).parent; P = D / 'parts'
ORDER = [('A_global1.html', '一 全局（上）：模型、数据、标签、提示词、打分'), ('B_global2.html', '二 全局（下）：假标题、读出工具、统计、泄漏审计、预注册、算力'),
         ('C_stage1_9.html', '三 Stage 1–9'), ('D_stage10_11.html', '四 Stage 10–11'), ('E_stage12.html', '五 Stage 12'), ('F_stage13.html', '六 Stage 13'),
         ('G_appendix.html', '七 附录'), ('H_selfcheck.html', '八 自查'), ('I_unknown_research.html', '九 附表：未知项查证'), ('J_dua_package.html', '十 附表：Dreaming Up Authors 代码包核对')]
CSS = r"""
:root{--bg:#F7F7F4;--ink:#1F2937;--pen:#5B6474;--line:#E3E6EA;--card:#FFFFFF;--acc:#C2410C;--link:#1D6FB8;--code:#F2F3F5;--unk:#FFF1E6;--unk-ink:#9A3412;--fix:#EAF4EC;
 --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;--zh:"Noto Sans SC","PingFang SC","Microsoft YaHei",system-ui,sans-serif;--serif:"Noto Serif SC","Songti SC",serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#13171d;--ink:#E7EAF0;--pen:#A3ADBD;--line:#2D3645;--card:#1B2230;--acc:#F6A65A;--link:#7DC4F5;--code:#232B3A;--unk:#3A2A1C;--unk-ink:#FDBA74;--fix:#1E3325;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#13171d;--ink:#E7EAF0;--pen:#A3ADBD;--line:#2D3645;--card:#1B2230;--acc:#F6A65A;--link:#7DC4F5;--code:#232B3A;--unk:#3A2A1C;--unk-ink:#FDBA74;--fix:#1E3325;color-scheme:dark}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15.5px/1.75 var(--zh);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.wrap{max-width:1040px;margin:0 auto;padding:36px 0 80px}
h1{font-family:var(--serif);font-size:34px;line-height:1.25;margin:0 0 8px}
h2{font-family:var(--serif);font-size:24px;margin:44px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--line)}
h3{font-size:19px;margin:30px 0 8px}
h4{font-size:16px;margin:18px 0 4px;color:var(--acc)}
p,li,dd,dt,div,span{overflow-wrap:anywhere}
p,li{margin:6px 0}
a{color:var(--link)}
section{scroll-margin-top:12px}
h2,h3,h4{scroll-margin-top:12px}
.lead{color:var(--pen)}
.toc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 20px;margin:22px 0;font-size:14.5px}
.toc ol{margin:4px 0;padding-left:1.4em}.toc li{margin:2px 0}.toc .sub{font-size:13.5px;color:var(--pen)}
.toc a{text-decoration:none}
table.t{border-collapse:collapse;width:100%;margin:10px 0;font-size:13.8px;background:var(--card);table-layout:auto}
table.t th,table.t td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top;white-space:normal;overflow-wrap:anywhere;word-break:normal}
table.t th{background:var(--code);font-weight:600}
.tw{overflow-x:auto}
pre.code,pre{background:var(--code);padding:10px 12px;border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere;font:12.8px/1.55 var(--mono)}
code{font-family:var(--mono);font-size:.88em;background:var(--code);padding:0 3px;border-radius:3px;overflow-wrap:anywhere}
.src{display:inline;font-size:12px;color:var(--pen);font-family:var(--mono);overflow-wrap:anywhere}
.src::before{content:"⟶ 出处 ";font-family:var(--zh)}
.unk{background:var(--unk);color:var(--unk-ink);padding:0 4px;border-radius:4px;font-weight:600}
.st{display:inline-block;font-size:12px;font-weight:700;padding:0 7px;margin:0 3px;border-radius:4px;color:#fff;vertical-align:1px}
.st-done{background:#2F7D3B}.st-rechecked{background:#1D6FB8}.st-review{background:#B45309}.st-void{background:#B42318}.st-plan{background:#6B7280}
.fix{background:var(--fix);border-left:4px solid #2F7D3B;padding:10px 14px;margin:12px 0;border-radius:6px}
.note{color:var(--pen);font-size:14px}
.legend span{margin-right:10px}
@media print{body{background:#fff;color:#000;font-size:11pt}.wrap{max-width:none;padding:0}a{color:#000}
 table.t{font-size:9pt;page-break-inside:auto}tr{page-break-inside:avoid}h2{page-break-before:always}h2,h3,h4{page-break-after:avoid}
 pre{font-size:8.5pt}.toc{page-break-after:always}}
"""


def main():
    parts = []
    for f, title in ORDER:
        p = P / f
        if not p.exists(): parts.append((title, f'<section><h2>{title}</h2><p class="unk">本部分缺失：{f}</p></section>')); continue
        s = re.sub(r'<!--.*?-->', '', p.read_text(), flags=re.S)
        parts.append((title, s))
    toc = ['<nav class="toc" aria-label="目录"><b>目录</b><ol>']
    for title, s in parts:
        secs = re.findall(r'<section id="([^"]+)"[^>]*>\s*<h2[^>]*>(.*?)</h2>', s, re.S)
        toc.append(f'<li>{html.escape(title)}<div class="sub">' + ' · '.join(f'<a href="#{i}">{re.sub(r"<[^>]+>", "", t).strip()}</a>' for i, t in secs) + '</div></li>')
    toc.append('</ol></nav>')
    n_unk = sum(s.count('class="unk"') for _, s in parts)
    head = f'''<title>Stage 1–13 方法手册</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;600;700&family=Noto+Serif+SC:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header><p class="lead">jlens 项目 · Qwen3-32B 作者记忆 · 方法答辩用 · 2026-10-30</p>
<h1>Stage 1–13 方法手册</h1>
<p>本手册记录<b>实际做了什么</b>，不是计划。每个数字、参数和样本量后面都给了出处（脚本路径和行号或函数名、结果文件、作业号、git commit），出处标为 <span class="src">示例</span>。查不到的地方写成 <span class="unk">未知/需确认：向谁确认</span>，全文共 {n_unk} 处，汇总表见附录。</p>
<p class="legend">状态标签：<span class="st st-done">已完成</span><span class="st st-rechecked">复核过</span><span class="st st-review">待复核</span><span class="st st-void">作废</span><span class="st st-plan">计划未做</span>。每个实验节固定用 9 个小标题：1 问题与作用 · 2 材料 · 3 工具 · 4 步骤 · 5 公式 · 6 对照 · 7 结果 · 8 局限与质疑 · 9 状态。</p>
<p class="note">路径约定：除非另写，<code>R10</code> = /scratch/zhang.zhiqi2/jlens/351_stage10，<code>R11</code> = …/361_stage11，<code>R12</code> = …/371_stage12，<code>R13</code> = …/381_stage13；代码在 ~/jlens_work/&lt;NN_stage&gt;/；git 仓库是 /scratch/zhang.zhiqi2/jlens-authorship-recall_update（GitHub ZhiQ1/jlens-authorship-recall）。</p>
</header>'''
    body = head + '\n'.join(toc) + '\n'.join(s for _, s in parts) + '</div>'
    (D / 'methods_handbook.html').write_text(body)
    ids = re.findall(r'id="([^"]+)"', body); dup = {i for i in ids if ids.count(i) > 1}
    links = set(re.findall(r'href="#([^"]+)"', body)); missing = sorted(links - set(ids))
    print('written', len(body) // 1024, 'KB; sections', body.count('<section'), '; unk', n_unk, '; duplicate ids', len(dup), sorted(dup)[:10], '; broken links', len(missing), missing[:15])


if __name__ == '__main__':
    main()
