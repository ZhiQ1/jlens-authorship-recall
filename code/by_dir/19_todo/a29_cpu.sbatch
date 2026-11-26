#!/bin/bash
#SBATCH -J a29_cpu
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a29/cpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: sbatch a29_cpu.sbatch tiny | analyze
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python
set -e
if [ "$1" = tiny ]; then
  export B3_TINY_SUFFIX=_a29
  $PY ~/jlens_work/13_stage13/stage13_b3_s10_gpu.py tiny-root
  $PY ~/jlens_work/13_stage13/stage13_b3_s10_gpu.py tiny-ref --shards 0
  $PY ~/jlens_work/19_todo/a29_layerfill.py run --tiny --shards 0
else
  $PY ~/jlens_work/19_todo/a29_layerfill.py "$@"
fi
