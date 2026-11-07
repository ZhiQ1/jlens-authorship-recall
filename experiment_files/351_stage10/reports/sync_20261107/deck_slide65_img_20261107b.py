"""2026-11-07 ~02:30 (decision F): deck HTML slide 65 (v17 64) image -> downloads/Stage13_hypotheses_table_v29_en_tableonly.png. Idempotent; backup = stage1_11_deck.before_20261107b.html (made by apply_20261107c.py)."""
import re, base64
P = '/scratch/zhang.zhiqi2/jlens/351_stage10/reports/'
s = open(P + 'merged_deck/stage1_11_deck.html', encoding='utf-8').read()
EN = P + 'downloads/Stage13_hypotheses_table_v29_en_tableonly.png'
s, c = re.subn(r'(<img alt="Hypotheses H1–H3 against readouts M1–M3 and the current results" src=")data:image/png;base64,[A-Za-z0-9+/=]+"', lambda m: m.group(1) + 'data:image/png;base64,' + base64.b64encode(open(EN, 'rb').read()).decode() + '"', s); assert c == 1
open(P + 'merged_deck/stage1_11_deck.html', 'w', encoding='utf-8').write(s); print('ok')
