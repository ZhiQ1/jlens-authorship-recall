"""Item 2-11b, DRAFT addendum 15 rev3 (NOT locked), matcher v3b = v3 (stage13_b2_gennames_b_v3.py, used by jobs 11734690/92/95;
not edited, imported by path) with two corrections found on the stored texts of job 11734690:
  (a) particles (de, van, al, el, bin, ... ; plus abu, ibn, ben, ould) never count as the shared part of a partial (P) match
      ('A. M. El-Sayed' vs 'A. El-Samawaty' shared only 'el' and became P);
  (b) the space-written compound candidate ('Rakesh Kumar Mishra' read as surname 'kumar mishra') counts only for M (exact
      equality with a true hyphen group), never for P (a middle name would otherwise make a partial).
Everything else as v3. Commands: examples --root | compare --root | tiny --root
"""
import importlib.util, sys
from pathlib import Path

H = Path.home() / 'jlens_work'
_sp = importlib.util.spec_from_file_location('gnb_v3', H / '13_stage13/stage13_b2_gennames_b_v3.py'); V3 = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V3)
NOPART = V3.PARTICLES | {'abu', 'ibn', 'ben', 'ould'}


def rel(t, g, swap):
    if t is None: return None
    best = None
    for k, (sg, gi) in enumerate(V3.gcands(g, swap)):
        if t['ti'] and gi != t['ti']: continue
        if sg == t['sg']: return 'M'
        if not swap and k == 1: continue                                     # (b) space-written compound: M only
        tp = (set(t['sg']) | ({t['x']} if t['x'] else set())) - NOPART       # (a) particles are not a shared part
        if set(sg) - NOPART & tp: best = 'P'
    return best


V3.rel = rel
V3.NEW = V3.NEW + [('N7 article El-/Al- is not a shared part', ['A. El-Samawaty'], 'A. M. El-Sayed'),
                   ('N4 generated middle word is not a partial', ['Ranjit Kumar'], 'Rakesh Kumar Mishra'),
                   ('N4 true middle word = possible first surname part', ['Ravindra Kumar Singh'], 'Rajeev Kumar')]

if __name__ == '__main__':
    V3.main()
