#!/bin/bash
#SBATCH -J b2ps_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_ps_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Items 2-7 / 2-9 tiny whole pipeline (CPU): GPU code on the random 2-layer Qwen3 (real tokenizer, 3 real sample papers;
# title / colon / x4tok compared with the frozen do_pscope / x4tok code) -> analysis with the hard-check code path against the
# frozen x1x4 analysis run on the frozen outputs. Root 381_stage13/b2_ps_tiny (fresh raw dir per job).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
export B2_TAG=$SLURM_JOB_ID
set -e
$PY -u stage13_b2_ps_gpu.py --tiny
$PY -u stage13_b2_ps_analyze.py --tiny
echo "B2 PS TINY PIPELINE DONE"
