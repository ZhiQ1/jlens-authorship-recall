"""Build the method slides (v3, 2026-11-05): SVG per slide, method_preview.html, method_slides_preview.pptx (native shapes).
Primitives / back-ends: method_lib.py; slide definitions: method_slides.py.  v1/v2 outputs kept as *.v1 / *.v2."""
import sys
from pathlib import Path
D = Path(__file__).parent; sys.path.insert(0, str(D))
import method_slides as M
from method_lib import svg_of, pptx_render, words, section_tag

# deck order of the "Methods in pictures" section: (key, accessible title, builder)
ORDER = [('legend', 'Legend for the method figures', M.legend),
         ('groups', 'Groups and samples', getattr(M, 'groups', None)),
         ('scoring', 'Scoring: rank, log, spec', M.scoring),
         ('stats', 'Statistical conventions', getattr(M, 'stats', None)),
         ('replication', 'Independent replication (Stage 8)', getattr(M, 'replication', None)),
         ('readout', 'Layer-by-layer readout', getattr(M, 'readout', None)),
         ('patch', 'Replacement (patching)', M.patch),
         ('knockout', 'Knockout (block)', getattr(M, 'knockout', None)),
         ('probe', 'Probe', getattr(M, 'probe', None)),
         ('question', 'Changing the question', getattr(M, 'question', None)),
         ('paraphrase', 'Paraphrased title', getattr(M, 'paraphrase', None)),
         ('patchscope', 'Patchscope', getattr(M, 'patchscope', None)),
         ('compare', 'Group comparisons', getattr(M, 'compare', None))]


def slides():
    out = []
    for key, tag, fn in ORDER:
        if fn is None: continue
        out.append((key, tag, fn() + [section_tag()]))
    return out


if __name__ == '__main__':
    from pptx import Presentation
    from pptx.util import Emu
    only = sys.argv[1:]
    S = slides()
    svgs = []
    for key, tag, items in S:
        s = svg_of(items, tag, uid=key[:3]); (D / f'slide_{key}.svg').write_text(s, encoding='utf-8'); svgs.append(s)
    page = '''<title>Method slides preview</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Patrick+Hand&display=swap">
<style>
:root { --bg: #E9ECE4; --fg: #22304A; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #10141C; --fg: #EEF1F5; color-scheme: dark } }
:root[data-theme="dark"] { --bg: #10141C; --fg: #EEF1F5; color-scheme: dark }
body { background: var(--bg); color: var(--fg); font: 16px/1.5 "Patrick Hand", system-ui, sans-serif; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 48px; }
main { max-width: 1280px; margin: 0 auto; display: grid; gap: 26px; }
figure { margin: 0; box-shadow: 0 3px 18px rgba(0,0,0,.22); }
figure svg { display: block; width: 100%; height: auto; }
p { margin: 0; }
</style>
<main>
<p>Methods in pictures (v3): very light pink grid marks the method pages; worked example = Coifman, Bonanno &amp; Rafaeli (2007). The same primitives are exported as native PowerPoint shapes.</p>
''' + ''.join(f'<figure>{s}</figure>' for s in svgs) + '</main>'
    (D / 'method_preview.html').write_text(page, encoding='utf-8')
    prs = Presentation(); prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)
    for key, tag, items in S:
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        cnt = pptx_render(sl, items, prs.slide_width)
        print(f'{key:12s} words all={words(items):3d} excl. token labels={words(items, True):3d} | '
              f'native leaf shapes={cnt["leaf"]}, groups={cnt["group"]}, grid lines={cnt["grid"]}')
    prs.save(D / 'method_slides_preview.pptx')
    for k, v in M.SOURCES.items():
        for s in v: print('SOURCE', k, '|', s)
