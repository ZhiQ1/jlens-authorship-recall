#!/bin/bash
# One GPU job for two small checks (user 2026-10-31: one queue wait instead of two):
#  (1) X3 para_run ONE real shard (stage13_para_shard.py 0; skips if the shard already exists)
#  (2) Stage 12 P2 hook check U40, ONE shard (stage12_p2_hookcheck.py --real; skipped if its summary.json exists)
# The model is loaded once per step (two separate scripts, ~5 min each); a failure in one step does not stop the other.
#SBATCH --job-name=s13_combo
#SBATCH --partition=gpu-interactive
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH -t 00:50:00
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/combo_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
export HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) combo $SLURM_JOB_ID on $(hostname)"
cd ~/jlens_work/13_stage13 && ~/conda-envs/jlens/bin/python -u stage13_para_shard.py 0 || echo "STEP1 para_shard exit $?"
echo "$(date -Is) step 1 done"
if [ -f /scratch/zhang.zhiqi2/jlens/371_stage12/hookcheck_2026-10-30/summary.json ]; then echo "hookcheck already done, skipped"
else cd ~/jlens_work/12_stage12 && ~/conda-envs/jlens/bin/python -u stage12_p2_hookcheck.py --real || echo "STEP2 hookcheck exit $?"; fi
echo "$(date -Is) combo done"
