#!/bin/bash
#SBATCH -J b2np_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 A tiny whole pipeline (CPU): GPU data code on the random 64-layer Qwen3 (real tokenizer, real Stage 10 shards 0-1,
# all 6 title conditions; hard check 1 against the tiny addendum-9 states) -> lens table + hard check 2 (real Stage 10 ranks,
# shards 0-1) -> probe at all 5 layers (random vocab rows) -> report. Root 381_stage13/b2_np_tiny.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
set -e
$PY -u stage13_b2_np_gpu.py --tiny --shards 0,1 --max-minutes 90
$PY -u stage13_b2_np_lens.py --tiny
for L in 32 40 48 52 56; do $PY -u stage13_b2_np_probe.py --tiny --layer $L; done
$PY -u stage13_b2_np_report.py --tiny
echo "B2 NP TINY PIPELINE DONE"
