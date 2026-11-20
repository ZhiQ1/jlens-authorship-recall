"""2026-11-18: insert the r_frag_20261118 slides into the merged main deck and apply the text fixes.
Source = stage1_11_deck.html.before_20261118 (backup made before any change) -> stage1_11_deck.html. Idempotent."""
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
F = Path(__file__).parent / 'r_frag_20261118'
src = (D / 'stage1_11_deck.html.before_20261118').read_text(encoding='utf-8')
s = src
frag = lambda n: (F / f'{n}.html').read_text(encoding='utf-8')


def after_section(s, aria, new):
    key = f'<section class="slide mf" aria-label="{aria}">' if f'<section class="slide mf" aria-label="{aria}">' in s else f'<section class="slide lt" aria-label="{aria}">'
    i = s.index(key); assert s.count(key) == 1, (aria, s.count(key))
    j = s.index('</section>', i) + len('</section>')
    return s[:j] + new + s[j:]


def rep(s, old, new):
    assert s.count(old) == 1, (s.count(old), old[:80]); return s.replace(old, new)


# 1. C24 wording (exact per-layer residual over confidence, summary_c24_optB_20261114/report.md)
s = rep(s, '超出置信度的剩余部分 +0.05–0.06 只在 L40–L52（L48 +0.062 [0.025, 0.100]），与传递区（标题信息到达名字位置的层段）一致。',
        '超出置信度的剩余部分只在 L40–L52（+0.050 至 +0.062：L40 +0.059 [0.025, 0.094]，L48 +0.062 [0.025, 0.100]，L52 +0.050 [0.018, 0.084]），与传递区一致。')
# 2. section overview of the appendix
s = rep(s, '<li>1. Group comparisons A / B / C / D: three findings, intervention re-runs (E1 and P1 / P2 numerator / denominator), recognition</li>',
        '<li>1. Group comparisons A / B / C / D: three findings, intervention re-runs (E1 and P1 / P2 numerator / denominator), recognition; why recall fails: output format and name chain (addendum 16), fabricated names, exposure threshold (addendum 19)</li>')
# 3. new slides
s = after_section(s, 'Names the model writes itself: true vs fabricated (C24)', frag('a_item1') + frag('b_item5') + frag('c_item6') + frag('d_item4'))
s = after_section(s, 'P1 / P2: the same small-denominator effect', frag('e_a16') + frag('f_fab') + frag('g_exp19'))
n0, n1 = src.count('<section class="slide'), s.count('<section class="slide')
assert n1 == n0 + 7, (n0, n1)
(D / 'stage1_11_deck.html').write_text(s, encoding='utf-8')
print('slides', n0, '->', n1)
