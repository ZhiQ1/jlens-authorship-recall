"""2026-11-25 coordinator: leader v17n -> v17o (results-only sync, rule 14): p66 #42 '... the same as the shuffled baseline (50.4% vs 50.5%) ...'
-> 'about half (50.4%) are not in the data'. Same change as HTML v76 slide 125 (user-approved)."""
from pptx import Presentation
D = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/gslides_20261112/'
prs = Presentation(D + 'jlens_leader_v17n.pptx'); s = prs.slides[65]
x = next(y for y in s.shapes if y.shape_id == 42)
rs = [r for p in x.text_frame.paragraphs for r in p.runs]
assert rs[0].text == 'Made-up names: about half are not in the data, the same as the shuffled baseline (' and rs[1].text == '50.4% vs 50.5%'
rs[0].text = 'Made-up names: about half ('; rs[1].text = '50.4%'
assert rs[2].text.startswith('); co-authors'); rs[2].text = ') are not in the data; co-authors' + rs[2].text[len('); co-authors'):]
prs.save(D + 'jlens_leader_v17o.pptx'); print('ok', x.text_frame.text)
