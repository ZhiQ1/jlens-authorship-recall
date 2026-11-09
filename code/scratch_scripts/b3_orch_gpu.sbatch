#!/bin/bash
#SBATCH -J b3s10_gpu
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b3_s10_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch-3 orchestrator worker (b3_orch.py, 2026-11-08). Same python call as stage13_b3_s10_gpu.sbatch MODE=all, but:
#  - no AUTO chaining (b3_orch.py keeps the workers and submits the analysis);
#  - the python budget is capped at the REAL time left (job may start with --time-min=20 via backfill):
#    budget = min(38, minutes_left - 7). The frozen stage13_b3_s10_gpu.sbatch (fixed 38 min) is not edited.
# Env: ITEM=3-1|3-2. MODE=all only (the gate uses the original stage13_b3_s10_gpu.sbatch with the full 45 min).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
ITEM=${ITEM:-3-1}
LEFT=$(squeue -h -j "$SLURM_JOB_ID" -o %L 2>/dev/null | tail -1)
BUDGET=$($PY -c "
import sys
s=sys.argv[1].strip() if len(sys.argv)>1 else ''
try:
    d,_,hms=s.rpartition('-'); p=[int(x) for x in hms.split(':')]
    while len(p)<3: p.insert(0,0)
    m=int(d or 0)*1440+p[0]*60+p[1]+p[2]/60
except Exception: m=45
print(f'{max(8.0, min(38.0, m-7)):.1f}')" "$LEFT")
echo "time left ${LEFT:-?} -> python budget $BUDGET min"
nvidia-smi --query-gpu=name,memory.total --format=csv || true
$PY -u stage13_b3_s10_gpu.py run --item "$ITEM" --all --max-minutes "$BUDGET"
rc=$?
echo "run exit $rc (0 ok, 3 refused / hard check marker, other = crash)"
exit $rc
