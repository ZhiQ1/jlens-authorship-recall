#!/bin/bash
# CPU tiny test of stage13_m2_f5.py: whole pipeline (2 shards, 1 layer per position, NB=50) for all 5 titles, check, analyse.
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_m2f5_tiny
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/m2f5_tiny_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16
PY=~/conda-envs/jlens/bin/python; S=~/jlens_work/13_stage13/stage13_m2_f5.py
set -e
for k in 0 1 2 3 4; do $PY -u $S run --title false_$k --tiny; done
$PY -u $S run --title false_1 --tiny          # second call must SKIP (done)
$PY -u $S check --tiny || echo "tiny check returned $? (mismatches expected in tiny: 2 shards)"
$PY -u $S analyse --tiny
echo TINY_OK
