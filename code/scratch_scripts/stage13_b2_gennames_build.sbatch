#!/bin/bash
#SBATCH -J b2c_gn_build
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_build_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 12 item 2-11 CPU build: per-name labels, chat-prompt token ids, positions, shards -> 381_stage13/b2_gennames/{names,papers}.parquet
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/13_stage13
[ -s /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames/names.parquet ] && { echo exists; exit 0; }
~/conda-envs/jlens/bin/python -u stage13_b2_gennames.py build
