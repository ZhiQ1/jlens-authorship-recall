#!/bin/bash
#SBATCH -J b2c_d124decide
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 2-00:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_d124_decide_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-1 decider (CPU): waits for the original-code prompt-66 rerun (arg: its job id), applies the user's rule of 2026-11-09
# (A: WARN + locked D12-4 record + continuation chain; B: stays stopped, outcome for the limitations). See stage9_b2_fitb_d124_decide.py.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/09_stage9
~/conda-envs/jlens/bin/python -u stage9_b2_fitb_d124_decide.py "$@"
