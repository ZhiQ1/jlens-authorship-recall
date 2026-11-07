#!/bin/bash
#SBATCH -J b2c_fitb_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_fitb_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-1 analysis (CPU): plan hard check (recompute66 vs backup; exit 2 on FAIL), then matrices / holdout / Stage 10 signal.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/09_stage9
if [ -z "$SKIP_HC66" ]; then ~/conda-envs/jlens/bin/python -u stage9_b2_fitb.py hardcheck66 || exit 2; fi
~/conda-envs/jlens/bin/python -u stage9_b2_fitb.py analyze
