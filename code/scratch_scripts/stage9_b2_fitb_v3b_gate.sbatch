#!/bin/bash
#SBATCH -J b2c_fitb3bgate
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_v3b_gate_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# D12-1 gate v3b (2026-11-09): identical command to stage9_b2_fitb_v3_gate.sbatch. Only change: submitted and RESUBMITTED by the CPU
# watchdog stage9_b2_fitb_v3b_watch.sbatch when the node epilog (/etc/slurm/epilog.d/00-slurm.epilog.clean.sh: pkill -KILL -U uid when its
# squeue finds no other job of the user on the node) SIGKILLs it (sacct FAILED 0:9). Full 45 min, no --time-min:
#   (submitted by the watchdog)
# Expected: ~1 min (part (a) from existing state files) + model load (10 s warm .. ~15 min on a crowded node) + prompt 66 (~6 min).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2c_fitb3gate $SLURM_JOB_ID on $(hostname) limit=$(squeue -h -j $SLURM_JOB_ID -o %l)"
free -g | head -2
cd ~/jlens_work/09_stage9
~/conda-envs/jlens/bin/python -u stage9_b2_fitb_v3.py gate
