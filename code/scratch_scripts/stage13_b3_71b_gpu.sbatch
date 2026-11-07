#!/bin/bash
#SBATCH -J b3_71b_gpu
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b3_71b_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 3 item 3-3 (addendum 14) GPU step: Stage 7.1B on the Stage 10 fast path (Pilot50, 21 title conditions, all authors/tokens).
#   MODE=gate: the 7 papers holding the 1,166 old 7.1B contexts, then the hard check (rank match >= 99%; exit 3 = FAIL)
#   MODE=all : the other 43 papers (refuses unless summary_b3_71b/gate.json is PASS). AUTO=1: resubmit / then submit the analysis.
#   HC33_POLICY=plan (default, frozen rule) | warn (record the FAIL, continue; ONLY with the user's approval).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
MODE=${MODE:-gate}
nvidia-smi --query-gpu=name,memory.total --format=csv || true
if [ "$MODE" = "all" ]; then ARGS="--all"; else ARGS="--gate"; fi
$PY -u stage13_b3_71b_gpu.py run $ARGS --max-minutes 38
rc=$?
echo "run exit $rc (0 ok, 3 hard check failed / refused, other = crash)"
if [ $rc -eq 0 ] && [ "$MODE" = "all" ] && [ "${AUTO:-0}" = "1" ]; then
  $PY -u stage13_b3_71b_gpu.py chain || echo "WARNING: chain step failed (resubmit by hand)"
fi
exit $rc
