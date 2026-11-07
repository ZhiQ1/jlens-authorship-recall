#!/bin/bash
#SBATCH -J b2c_gennames2
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_v2_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# v2 GPU worker: UNIT=<unit> (one unit / gate) or ALL=1 (claims, skip-if-exists, clean budget). Hard checks exit 2.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2c_gennames2 $SLURM_JOB_ID on $(hostname) unit=${UNIT:-} all=${ALL:-0}"
cd ~/jlens_work/13_stage13
if [ -n "$UNIT" ]; then A="--shard $UNIT"; else A="--all"; fi
~/conda-envs/jlens/bin/python -u stage13_b2_gennames_v2.py gpu $A --minutes 42
