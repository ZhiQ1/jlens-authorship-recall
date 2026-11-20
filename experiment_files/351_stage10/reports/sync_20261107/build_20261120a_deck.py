"""2026-11-20a: slide 27 ("The probe signal is paper-specific") n line. Only that slide's <span class="nn"> text changes.
Evidence (2026-11-20): the chart = talk/src/charts.py c16_probe_controls, from 381_stage13/summary_cpu_group/X1controls_4configs.csv
(split=group, excl=title-reuse; made by ~/jlens_work/13_stage13/stage13_e4b_group.py). Per-paper rows in perpaper_probe_spec.parquet
(group/title-reuse, X1 part, not dropped, spec not NaN) reproduce every bar exactly:
  probe / gold of another paper / gold of a same-field paper: 1,863 papers (target 896, control 499, excluded 433, guard 35);
  trained on false titles: 1,568 papers (target 810, control 399, excluded 325, guard 34; the false-trained probe's reuse rule drops more).
  (The E4b probe run on target+control only = 1,395 papers gives 0.051 / 0.061 / 0.075, not the plotted 0.050 / 0.066 / 0.080.)
Source = merged_deck/stage1_11_deck.html.before_20261120a -> merged_deck/stage1_11_deck.html. Idempotent (always rebuilds from the backup)."""
import re, json
from pathlib import Path
D = Path('/scratch/zhang.zhiqi2/jlens/351_stage10/reports/merged_deck')
SRC = D / 'stage1_11_deck.html.before_20261120a'; OUT = D / 'stage1_11_deck.html'
s = SRC.read_text(encoding='utf-8')
ms = list(re.finditer(r'<section class="slide.*?</section>', s, re.S)); assert len(ms) == 94, len(ms)
K = 27; t = ms[K - 1].group(0)
assert '<img alt="Stage 10-11 slide 21"' in t
OLD = '<span class="nn">n = 1,863 papers (X1-control pipeline, title reuse removed)</span>'
NEW = '<span class="nn">n = 1,863 papers (X1-control pipeline, title reuse removed); “trained on false titles” bars: n = 1,568 (stricter reuse rule)</span>'
assert s.count(OLD) == 1 and t.count(OLD) == 1
t2 = t.replace(OLD, NEW)
o = s[:ms[K - 1].start()] + t2 + s[ms[K - 1].end():]
OUT.write_text(o, encoding='utf-8')
rec = {'source': str(SRC), 'out': str(OUT), 'content_changed': {K: ['n line: add trained-on-false bars n = 1,568']}, 'old': OLD, 'new': NEW,
       'bytes_in': len(s.encode()), 'bytes_out': len(o.encode())}
(Path(__file__).parent / 'build_20261120a_deck.json').write_text(json.dumps(rec, indent=1, ensure_ascii=False))
print('ok', len(s), '->', len(o))
