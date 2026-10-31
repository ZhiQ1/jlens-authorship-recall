"""X3 para_run, ONE real shard first (fixed rule 2; prereg addendum 5). Runs unit ('para_run', None, SHARD) with the same
code as the work loop (381_stage13.compute / save), then checks (WARN only) that the stored lexical neighbour equals
config/x3_lexical_neighbour_j2.csv and that scores are finite. Usage: python stage13_para_shard.py [shard]"""
import importlib.util, sys
from pathlib import Path
import numpy as np, pandas as pd
H = Path.home() / 'jlens_work'
sp = importlib.util.spec_from_file_location('s13', H / '13_stage13/381_stage13.py'); s13 = importlib.util.module_from_spec(sp); sp.loader.exec_module(s13)
sh = int(sys.argv[1]) if len(sys.argv) > 1 else 0; u = ('para_run', None, sh); f = s13.out_path(u)
if f.exists(): s13.log('already done', f)
else:
    C = s13.Ctx(); d = s13.compute(C, u); s13.save(u, d, C.env); s13.log('saved', f)
z = np.load(f); j = pd.read_csv(s13.ROOT / 'config/x3_lexical_neighbour_j2.csv').set_index('paper_id')
ok_d = all(j.loc[p].lexical_neighbour_j2 == q for p, q in zip(z['paper_id'], z['lexical_neighbour']))
fin = all(np.isfinite(z[k]).all() for k in ('score_original', 'score_paraphrase', 'score_partner', 'score_lexical'))
print(f'{"OK" if ok_d else "WARN"} lexical neighbour equals the addendum-5 table ({len(z["paper_id"])} rows)')
print(f'{"OK" if fin else "WARN"} scores finite; resid {z["resid"].shape}')
print('mean score original / paraphrase / partner / lexical:', *[round(float(z[k].mean()), 3) for k in ('score_original', 'score_paraphrase', 'score_partner', 'score_lexical')])
