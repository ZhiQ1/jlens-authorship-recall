#!/bin/bash
#SBATCH -J pf_split
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=48G
#SBATCH -t 08:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b/logs_predfirst_split/%x_%A_%a.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# post-hoc split of probe (i) by item position (CPU only). LAYERS from env or array index.
export OMP_NUM_THREADS=16 MKL_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 HF_HUB_OFFLINE=1
L=${LAYERS:-$(echo 16 24 32 40 48 52 56 | cut -d' ' -f$((SLURM_ARRAY_TASK_ID+1)))}
~/conda-envs/jlens/bin/python ~/jlens_work/13_stage13/stage13_b2_gennames_b_predfirst_split_20261125.py --layers $L --nb ${NB:-2000} ${OUT:+--out $OUT}
