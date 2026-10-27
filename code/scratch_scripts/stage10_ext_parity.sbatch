#!/bin/bash
# Stage 10 extension parity (public lens + logit lens at L50-55,57-61; agreed 2026-10-23). Runs on gpu-short (2 h).
# Lists use ':' (sbatch --export splits on ','). If this run FAILs, its entry is moved out of reports/parity.json into
# reports/parity_ext_FAIL_<job>.json, so the main round's PASS gate is not broken; the ext pairs then stay unpassed.
# When the pool (stage10_pool.py) is active, only a run with FORCE=1 does anything (the old s10x_wait gates exit here).
#SBATCH --job-name=s10x_parity
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=01:55:00
#SBATCH --output=/scratch/%u/jlens/351_stage10/logs/parity_ext_%j.log
ROOT=/scratch/$USER/jlens/351_stage10; PY=~/conda-envs/jlens/bin/python
if [ -z "$FORCE" ] && [ -e $ROOT/logs/.pool_active ]; then echo "pool manages the extension; nothing to do"; exit 0; fi
READOUTS=${READOUTS:-jlens_public:logit}; LAYERS=${LAYERS:-50:51:52:53:54:55:57:58:59:60:61}
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "ext parity on $(hostname) readouts=$READOUTS layers=$LAYERS"; nvidia-smi --query-gpu=name,memory.total --format=csv
$PY -u ~/jlens_work/10_stage10/351_stage10_fix1.py parity --n ${N:-12} --readouts ${READOUTS//:/,} --layers ${LAYERS//:/,}
rc=$?
if [ $rc -ne 0 ]; then
  $PY - "$ROOT/reports" "$SLURM_JOB_ID" <<'PYEOF'
import json, os, sys
d, job = sys.argv[1], sys.argv[2]; p = os.path.join(d, 'parity.json'); j = json.load(open(p))
fails = [r for r in j['runs'] if r['status'] == 'FAIL' and any(int(k.split('@L')[1]) in (50, 51, 52, 53, 54, 55, 57, 58, 59, 60, 61) for k in r['max_abs_logit_diff'])]
if fails:
    json.dump(fails, open(os.path.join(d, f'parity_ext_FAIL_{job}.json'), 'w'), indent=2)
    j['runs'] = [r for r in j['runs'] if r not in fails]
    j['status'] = 'PASS' if j['runs'] and all(r['status'] == 'PASS' for r in j['runs']) else ('FAIL' if j['runs'] else 'not run')
    j['passed_pairs'] = sorted({k for r in j['runs'] if r['status'] == 'PASS' for k in r['max_abs_logit_diff']})
    tmp = p + '.tmp'; json.dump(j, open(tmp, 'w'), indent=2, sort_keys=True); os.replace(tmp, p)
    print('ext parity FAIL moved to', f'parity_ext_FAIL_{job}.json; main status now', j['status'])
PYEOF
  exit $rc
fi
