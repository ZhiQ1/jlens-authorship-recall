"""Build the combined Stage 1–11 report from the two published reports (Stage 1–9, Stage 10–11) plus new sections.
Each part keeps its own stylesheet, scoped under a wrapper class so the two designs do not clash."""
import re, sys
from pathlib import Path

HERE = Path(__file__).parent
P19, P1011 = Path(sys.argv[1]), Path(sys.argv[2])
NEW = (HERE / 'new_sections.html').read_text() if (HERE / 'new_sections.html').exists() else ''
OVERVIEW = (HERE / 'overview.html').read_text()
PLAN13 = (HERE / 'plan13.html').read_text() if (HERE / 'plan13.html').exists() else ''


def scope_selector(sel, sc):
    sel = sel.strip()
    if not sel: return sel
    out = []
    for s in sel.split(','):
        s = s.strip()
        m = re.match(r'^(:root(?::not\(\[data-theme="light"\]\)|\[data-theme="dark"\])?)\s*(.*)$', s)
        if m:
            pre, rest = m.group(1), m.group(2)
            base = '' if pre == ':root' else pre + ' '
            out.append(f'{base}{sc}' + (f' {rest}' if rest else ''))
        elif re.match(r'^(html|body|main)\b', s):
            rest = re.sub(r'^(html|body|main)', '', s)
            out.append(f'{sc}{rest}')
        elif s.startswith('*'):
            out.append(f'{sc} {s}, {sc}')
        else:
            out.append(f'{sc} {s}')
    return ', '.join(out)


def scope_css(css, sc):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    out, i = [], 0
    while i < len(css):
        j = css.find('{', i)
        if j < 0: break
        head = css[i:j].strip()
        if head.startswith('@media'):
            depth, k = 1, j + 1
            while depth:
                depth += {'{': 1, '}': -1}.get(css[k], 0); k += 1
            out.append(f'{head}{{{scope_css(css[j + 1:k - 1], sc)}}}'); i = k
        else:
            k = css.find('}', j)
            out.append(f'{scope_selector(head, sc)}{{{css[j + 1:k]}}}'); i = k + 1
    return '\n'.join(out)


def parts(path):
    s = path.read_text()
    css = '\n'.join(c for c in re.findall(r'<style>(.*?)</style>', s, re.S) if 'until-found' not in c)   # drop the host skeleton style
    body = re.search(r'<main>(.*)</main>', s, re.S).group(1)
    links = re.findall(r'<link rel="stylesheet" href="([^"]+)"', s)
    return css, body, links


css19, body19, l19 = parts(P19)
css10, body10, l10 = parts(P1011)
# Part I: drop its own header/TOC and the bridge section (it moves to Part III, updated)
body19 = re.sub(r'<header>.*?</header>', '', body19, flags=re.S)
body19 = re.sub(r'<nav class="toc">.*?</nav>', '', body19, flags=re.S)
bridge = re.search(r'<section id="bridge">.*?</section>', body19, re.S).group(0)
body19 = body19.replace(bridge, '')
body19 = re.sub(r'id="(\w+)"', r'id="p1-\1"', body19).replace('href="#', 'href="#p1-')
# Part II: drop its header; label 6.12 as Stage 11 (user request, matches the deck)
body10 = re.sub(r'<header>.*?</header>', '', body10, flags=re.S)
body10 = body10.replace('<span class="stag">Stage 12 · CPU</span>', '<span class="stag">Stage 11 · CPU</span>')
# grouping sections of both parts point to the R0/R1 analysis (Part III)
G1 = '<p>Stage 1–9 比较的是 A vs B，Stage 10–11 比较的是 (A+C) vs (B+D)。多出来的 R1 论文几乎全在 target 一侧（C 511 篇，D 仅 34 篇）。</p>'
assert body19.count(G1) == 1
body19 = body19.replace(G1, G1 + '<div class="bx ok"><b>R0/R1 分层的结果（第三部分）</b>在全量数据上只比 A vs B（都是 R0），输出处的目标−对照标题特异差为 +0.199 [0.187, 0.212]，合并口径为 +0.207，各层形状相同；C 比 A 强（+0.11），但同样只在最后几层领先。两阶段的分组口径因此可以直接对照。<a href="#p3-r0r1">详见第三部分</a></div>')
G2 = '<p class="en">Relation to Stages 4–8: those stages used groups A/B/C/D'
i = body10.find(G2); j = body10.find('</div>', i) + 6
assert i > 0
body10 = body10[:j] + '<div class="pair"><p class="zh"><b>R0/R1 分层（第三部分）。</b>两组都只保留 R0（即 A vs B）时，输出处标题特异的目标−对照差为 +0.199 [0.187, 0.212]（合并口径 +0.207），各层形状不变；R1 目标论文（C）比 R0（A）多 +0.11，同样只在最后几层；R1 论文内部，模型写对的作者比没写对的高 +0.20，也只在 L54 之后出现。<a href="#p3-r0r1">详见第三部分</a></p><p class="en">R0/R1 split (Part III): with R0 papers only (A vs B) the output title-specific target − control gap is +0.199 [0.187, 0.212] (pooled +0.207) with the same layer profile; R1 targets (C) exceed R0 targets (A) by +0.11, also only in the last layers; inside R1 papers the authors the model wrote correctly exceed the missed ones by +0.20, again only after L54.</p></div>' + body10[j:]
# 2026-10-28 review (prereg addendum 2): probe statements are under review until E4b is re-run with team folds and the
# title-reuse exclusion. Marker only; the text itself is unchanged.
RV = '<span style="display:inline-block;font-size:12px;font-weight:700;padding:0 6px;margin-right:6px;border-radius:4px;background:#B42318;color:#fff">待复核 under review</span>'
RVN = '<a href="#p4-plan" style="font-size:12.5px">（probe 结果正在复核：同一标题跨训练和测试、标题一题两用、未按团队切分，见第四部分）</a>'
for old, new in (('标题最后一个 token 上，线性 probe', RV + '标题最后一个 token 上，线性 probe'),
                 ('<b>标题位置能不能读出作者。</b>', RV + '<b>标题位置能不能读出作者。</b>'),
                 ('<b>标题位置 probe 的对照检验。</b>', RV + '<b>标题位置 probe 的对照检验。</b>'),
                 ('<span><b>读得早，说得晚。</b>', '<span>' + RV + '<b>读得早，说得晚。</b>')):
    assert old in body10, old
    body10 = body10.replace(old, new)
# 2026-10-28: the 'moved onto the post-title tokens' wording is under review (Stage 12 P1 preview: most of it sits at the name positions)
RV2 = '<span style="display:inline-block;font-size:12px;font-weight:700;padding:0 6px;margin:0 4px;border-radius:4px;background:#B42318;color:#fff">待复核</span>'
for frag in ('搬到标题之后的位置', '搬到标题之后的几个 token 上'):
    assert frag in body10, frag
    body10 = body10.replace(frag, frag + RV2)
for h in ('6.11 Stage 11：干预实验', '6.12 名字先验'):
    i = body10.index(h); j = body10.index('</h3>', i) + 5; body10 = body10[:j] + '<p style="margin:4px 0 0">' + RV + RVN + '</p>' + body10[j:]
i = body10.index('<h2><span class="num">§7</span>'); j = body10.index('</h2>', i) + 5; body10 = body10[:j] + '<p style="margin:4px 0 0">' + RV + RVN + '</p>' + body10[j:]
sec_ids = iter(range(1, 100))
body10 = re.sub(r'<section>', lambda m: f'<section id="p2-{next(sec_ids)}">', body10)
BRIDGE_OLD = re.search(r'<div class="bx warn"><b>可比性提醒</b>.*?</div>', bridge, re.S).group(0)
BRIDGE_NEW = '<div class="bx ok"><b>可比性：已核对</b>Stage 1–9 的 A/B 都是 R0，Stage 10–11 的 target/control 合并了 R0 与 R1。在 Stage 10–11 上只保留 R0 后（上一节），结论不变：输出处 +0.199 vs +0.207，各层形状相同，Stage 11 曲线也不变。</div>'
fonts = sorted(set(l19 + l10 + ['https://fonts.googleapis.com/css2?family=Caveat:wght@700&display=swap']))

html = f'''<title>Stage 1–11 实验报告</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{''.join(f'<link rel="stylesheet" href="{u}">' for u in fonts)}
<style>
:root{{--pg:#F7F7F4;--pg-ink:#1F2937;--pg-pen:#5B6474;--pg-line:#E3E6EA;--pg-card:#FFFFFF;--pg-acc:#C2410C;--pg-b:#1D6FB8;
 box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--pg:#13171d;--pg-ink:#E7EAF0;--pg-pen:#A3ADBD;--pg-line:#2D3645;--pg-card:#1B2230;--pg-acc:#F6A65A;--pg-b:#7DC4F5;color-scheme:dark}}}}
:root[data-theme="dark"]{{--pg:#13171d;--pg-ink:#E7EAF0;--pg-pen:#A3ADBD;--pg-line:#2D3645;--pg-card:#1B2230;--pg-acc:#F6A65A;--pg-b:#7DC4F5;color-scheme:dark}}
html{{scroll-padding-top:env(safe-area-inset-top,0px)}}
*,*::before,*::after{{box-sizing:border-box}}
body{{margin:0;background:var(--pg);color:var(--pg-ink);font:16.5px/1.75 "PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans SC",system-ui,sans-serif;
 padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}}
.wrap{{max-width:920px;margin:0 auto;padding:40px 0 30px}}
.wrap h1{{font-family:"Caveat","Patrick Hand",cursive;font-size:58px;line-height:1.05;margin:6px 0 10px}}
.wrap h1 small{{display:block;font-size:30px;color:var(--pg-pen)}}
.kick{{color:var(--pg-pen);font-size:14.5px;margin:0}}
.ptoc{{display:grid;gap:6px;margin:22px 0 4px;padding:14px 18px;background:var(--pg-card);border:1px solid var(--pg-line);border-radius:10px;font-size:15px}}
.ptoc a{{color:var(--pg-b);text-decoration:none}}
.ptoc .sub{{color:var(--pg-pen);font-size:13.5px;padding-left:1.2em}}
.ov h2,.partbar h2{{font-size:25px;margin:34px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--pg-line)}}
.ov h3{{font-size:19px;margin:22px 0 8px}}
.ov p,.ov li{{margin:6px 0}}
.ov .tw{{overflow-x:auto;margin:12px 0}}
.ov table{{border-collapse:collapse;font-size:14.5px;width:100%;min-width:560px;background:var(--pg-card)}}
.ov th,.ov td{{border-bottom:1px solid var(--pg-line);padding:7px 10px;text-align:left;vertical-align:top}}
.ov th{{font-weight:600;color:var(--pg-pen);border-bottom:2px solid var(--pg-line)}}
.ov .ok{{color:#2F7D3B;font-weight:600}} .ov .ref{{color:var(--pg-acc);font-weight:600}} .ov .open{{color:#B42318;font-weight:600}}
.ov .bx{{border-radius:8px;padding:12px 16px;margin:16px 0;border-left:4px solid var(--pg-acc);background:var(--pg-card)}}
.ov .en{{display:block;font-family:"Source Serif 4",Georgia,serif;color:var(--pg-pen);font-size:15px;line-height:1.55}}
.ov .mono{{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.86em}}
.partbar{{max-width:920px;margin:48px auto 0;padding:0}}
.partbar .tagp{{display:inline-block;font-size:13px;font-weight:700;letter-spacing:.06em;padding:2px 10px;border-radius:12px;background:var(--pg-ink);color:var(--pg)}}
.partbar p{{color:var(--pg-pen);font-size:14.5px;margin:6px 0 0}}
@media (max-width:640px){{.wrap h1{{font-size:44px}}}}
/* ---- Part I (Stage 1–9) ---- */
{scope_css(css19, '.p19')}
/* ---- Part II (Stage 10–11) ---- */
{scope_css(css10, '.p1011')}
.p19,.p1011{{padding-left:0;padding-right:0;background:transparent}}
.p19 main,.p1011 main{{padding-top:10px}}
</style>
<div class="wrap">
<header>
<p class="kick">jlens 项目 · Section 3.5.1 · Qwen3-32B（revision 9216db57，BF16）· 更新于 2026-10-28</p>
<h1>Stage 1–11 实验报告<small>大模型在哪一层“记住”论文作者</small></h1>
<p class="kick">本报告合并原 Stage 1–9 报告（小样本：20 → 50 → 200 篇）与 Stage 10–11 报告（全量 9,108 篇），并加入跨阶段的 R0/R1 分层分析。之后的新实验都只更新本报告和 Stage 1–11 合并 PPT。</p>
</header>
<nav class="ptoc" aria-label="目录"><b>目录</b>
<a href="#ov">总览：四条论证线与主要结论</a>
<a href="#p1-sum">第一部分 · Stage 1–9：小样本阶段（建立信号、排除替代解释）</a>
<span class="sub"><a href="#p1-s1">Stage 1 分组</a> · <a href="#p1-s3">3 lens</a> · <a href="#p1-s4">4</a> · <a href="#p1-s5">5</a> · <a href="#p1-s6">6</a> · <a href="#p1-s7">7</a> · <a href="#p1-s8">8</a> · <a href="#p1-s9">9</a> · <a href="#p1-syn">综合</a> · <a href="#p1-open">待核实</a> · <a href="#p1-app">附录</a></span>
<a href="#p2-1">第二部分 · Stage 10–11：全量阶段（定位与干预）</a>
<span class="sub"><a href="#p2-1">§1 摘要</a> · <a href="#p2-3">§3 数据与分组</a> · <a href="#p2-4">§4 方法</a> · <a href="#p2-6">§6 结果</a> · <a href="#p2-7">§7 结论</a> · <a href="#p2-8">§8 局限</a></span>
<a href="#p3">第三部分 · 跨阶段：R0/R1 分层分析与两阶段对照</a>
<a href="#p4">第四部分 · Stage 13：中间层到底表示什么（计划与进展）</a>
</nav>
<div class="ov" id="ov">{OVERVIEW}</div>
</div>
<div class="partbar"><span class="tagp">第一部分</span><h2>Stage 1–9：小样本阶段</h2><p>原 Stage 1–9 报告全文（记录日期 2026-10-18 至 10-21）。“与 Stage 10–11 的对照”一节已移到第三部分并更新。</p></div>
<div class="p19"><main>{body19}</main></div>
<div class="partbar"><span class="tagp">第二部分</span><h2>Stage 10–11：全量阶段</h2><p>原 Stage 10–11 双语报告全文（2026-10-27）。6.12 节标签改为 Stage 11，与 PPT 一致。</p></div>
<div class="p1011"><main>{body10}</main></div>
<div class="partbar" id="p3"><span class="tagp">第三部分</span><h2>跨阶段：R0/R1 分层分析与两阶段对照</h2><p>Stage 1–9 只比 A vs B（都是 R0），Stage 10–11 比 target vs control（R0 + R1 合并）。这一部分把两者放到同一口径下。</p></div>
<div class="p19"><main>{NEW}{bridge.replace('id="bridge"', 'id="p3-bridge"').replace('<h2>与 Stage 10–11 的对照</h2>', '<h2>两阶段对照（Stage 1–9 与 Stage 10–11）</h2>').replace(BRIDGE_OLD, BRIDGE_NEW)}</main></div>
<div class="partbar" id="p4"><span class="tagp">第四部分</span><h2>Stage 13：中间层到底表示什么</h2><p>lens 读不出不等于信息不存在：中间层可能在表示任务或论文身份，而不是名字。计划、预测和进展都在这里更新。</p></div>
<div class="p19"><main>{PLAN13}</main></div>'''
out = HERE / 'stage1_11_report.html'; out.write_text(html); print('wrote', out, len(html) // 1024, 'KB')
