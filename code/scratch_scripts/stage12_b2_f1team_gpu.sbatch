#!/bin/bash
#SBATCH -J b2c_f1team
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/371_stage12/logs/b2_f1team_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-2 GPU worker. UNIT=fit:A | fit:B | read:<cond>:<k>  (one unit = gate)  or  ALL=1 (claim units, skip finished,
# stop cleanly before the 45-min limit). Hard check runs automatically once both halves are fitted (exit 2 on FAIL).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2_f1team $SLURM_JOB_ID on $(hostname) part=$SLURM_JOB_PARTITION unit=${UNIT:-} all=${ALL:-0}"
cd ~/jlens_work/12_stage12
if [ -n "$UNIT" ]; then A="--unit $UNIT"; else A="--all"; fi
~/conda-envs/jlens/bin/python -u stage12_b2_f1team.py gpu $A --minutes 42
