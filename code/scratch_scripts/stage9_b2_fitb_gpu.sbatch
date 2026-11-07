#!/bin/bash
#SBATCH -J b2c_fitb
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-1 GPU worker. UNIT = gate | resume | recompute66 | holdout | read:<cond>:<k>, or ALL=1 (holdout + read units,
# claims, skip-if-exists). gate/recompute66 use the frozen Stage 9 loader (55 GiB GPU cap + CPU offload, as the original fit);
# resume runs the frozen stage9_fullfit.py under timeout. Hard checks exit 2 on FAIL.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2_fitb $SLURM_JOB_ID on $(hostname) part=$SLURM_JOB_PARTITION unit=${UNIT:-} all=${ALL:-0}"
cd ~/jlens_work/09_stage9
if [ -n "$UNIT" ]; then A="--unit $UNIT"; else A="--all"; fi
~/conda-envs/jlens/bin/python -u stage9_b2_fitb.py gpu $A --minutes 42
