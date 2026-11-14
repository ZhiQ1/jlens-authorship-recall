#!/bin/bash
#SBATCH -J c24regen_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/c24_regen_20261114_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# C24 1a option A: CPU tiny-model precheck of stage13_c24_regen_20261114.py (+ evaluate on the real shard-0 old replay files is not possible: needs positions)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
echo "$(date -Is) c24regen_tiny $SLURM_JOB_ID on $(hostname)"
DRYRUN=1 bash /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_c24_regen_20261114_gpu.sbatch
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_c24_regen_20261114.py tiny --out /scratch/zhang.zhiqi2/jlens/381_stage13/c24_regen_20261114_tiny/test_$SLURM_JOB_ID
