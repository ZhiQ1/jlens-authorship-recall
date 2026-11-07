#!/bin/bash
#SBATCH -J b3_tiny71w
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b3_tiny71warn_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 3 tiny test, 3-3 second half: HC33_POLICY=warn path (gate FAIL recorded, continue) -> --all (2 more papers) -> analysis.
# Needs the tiny root and tiny gate output of stage13_b3_tiny.sbatch.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 HC33_POLICY=warn
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
$PY -u stage13_b3_71b_gpu.py gate-check --tiny; echo "gate-check (warn) exit $?"
$PY -u stage13_b3_71b_gpu.py run --all --tiny --tiny-papers 2 --max-minutes 40; echo "all exit $?"
$PY -u stage13_b3_71b_gpu.py chain --tiny --dry; echo "chain exit $?"
$PY -u stage13_b3_71b_analyze.py --tiny; echo "analyze exit $?"
