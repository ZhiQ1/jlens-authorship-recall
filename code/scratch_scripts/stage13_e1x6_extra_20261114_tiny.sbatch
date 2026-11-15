#!/bin/bash
#SBATCH -J e1x6x_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/e1x6_extra_20261114_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# CPU precheck: (1) driver tiny (random 64-layer Qwen3-shaped fp32 model, 4 real papers); (2) analysis on the tiny output
# (5 title dirs: false_2..4 symlinked to false_1); (3) analysis on the REAL stored rows with no new rows -> parity with
# x6_recovery.csv / s1113_groups.csv / rerun_group_values.csv must be exact; (4) sbatch DRYRUN of the GPU file.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; D=/home/zhang.zhiqi2/jlens_work/13_stage13
T=/scratch/zhang.zhiqi2/jlens/381_stage13/e1x6_extra_20261114_tiny/test_$SLURM_JOB_ID; mkdir -p $T
echo "$(date -Is) e1x6x_tiny $SLURM_JOB_ID on $(hostname) -> $T"
RES=0
DRYRUN=1 TITLES=false_1,false_2 SHARDS=0-23 bash $D/stage13_e1x6_extra_20261114_gpu.sbatch || RES=1
$PY -u $D/stage13_e1x6_extra_20261114.py tiny --root $T || RES=1
for k in 2 3 4; do ln -sfn $T/stored/false_1 $T/stored/false_$k; ln -sfn $T/raw/false_1 $T/raw/false_$k; done
mkdir -p $T/stored_u0
$PY -u $D/stage13_e1x6_extra_analyze_20261114.py analyze --test --new $T/raw --out $T/summary_tiny --stored-e1 $T/stored/false_0 --stored-x6 $T/stored --stored-u0 $T/stored_u0 > $T/analyze_tiny.log 2>&1 || RES=1
tail -5 $T/analyze_tiny.log
$PY - $T <<'PYEOF' || RES=1
import sys, json, pandas as pd, numpy as np
from pathlib import Path
T = Path(sys.argv[1]); S = T / 'summary_tiny'; ok = {}
D = pd.read_csv(S / 'e1x6_recovery.csv'); G = pd.read_csv(S / 'e1x6_by_group.csv'); hc = json.load(open(S / 'hardcheck.json'))
lay = sorted(D.layer.unique()); ok['analysis: merged layers = stored 15 + new 9'] = lay == sorted(set([24,32,40,48,50,52,54,56,57,58,59,60,61,62,63]) | {41,42,43,44,45,46,47,49,51})
ok['analysis: new layers present for all titles and average'] = all(((D.layer == l) & (D.false_title == t) & (D.group == 'all')).any() for l in (41, 49, 51) for t in ['false_0', 'average'])
ok['analysis: target-control rows'] = (D.group == 'target - control').any()
ok['analysis: mean5 = average of titles'] = all(abs(D[(D.group=='all')&(D.false_title=='average')&(D.layer==l)].R.iloc[0] - D[(D.group=='all')&D.false_title.isin(['false_0','false_1','false_2','false_3','false_4'])&(D.layer==l)].R.mean()) < 1e-12 for l in (41, 48))
ok['analysis: hardcheck ran on overlap layers'] = sorted(int(k) for k in hc['false_0']['per_layer']) == [40, 48, 50, 52, 54, 56] and hc['false_0']['status'] == 'OK'
ok['analysis: by-group rows'] = len(G) > 0 and set(G.group) & {'A', 'B'} != set()
ok['report written'] = (S / 'report.md').exists()
for k, v in ok.items(): print('E1X6 TINY CHECK', 'PASS' if v else 'FAIL', k)
print('E1X6 TINY ANALYSIS', 'PASS' if all(ok.values()) else 'FAIL'); sys.exit(0 if all(ok.values()) else 1)
PYEOF
mkdir -p $T/empty_new
$PY -u $D/stage13_e1x6_extra_analyze_20261114.py analyze --new $T/empty_new --out $T/summary_realstored > $T/analyze_realstored.log 2>&1 || RES=1
echo "--- parity on real stored rows (no new rows):"; cat $T/summary_realstored/parity.txt
grep -q WARN <(grep -v "no new shards" $T/summary_realstored/parity.txt) && { echo "PARITY WARN"; RES=1; }
echo "E1X6 TINY OVERALL $([ $RES = 0 ] && echo PASS || echo FAIL)"
exit $RES
