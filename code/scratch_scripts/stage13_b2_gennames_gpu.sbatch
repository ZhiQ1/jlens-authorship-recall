#!/bin/bash
#SBATCH -J b2c_gennames
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-11 GPU: SHARD=k (gate: greedy first-name hard check on 50 papers, then shard k) or ALL=1 (claims, skip-if-exists,
# clean budget). The hard check runs once (summary/repro_check.json); exit 2 if < 90%.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2_gennames $SLURM_JOB_ID on $(hostname) shard=${SHARD:-} all=${ALL:-0}"
cd ~/jlens_work/13_stage13
if [ -n "$SHARD" ]; then A="--shard $SHARD"; else A="--all"; fi
~/conda-envs/jlens/bin/python -u stage13_b2_gennames.py gpu $A --minutes 42
