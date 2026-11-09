#!/bin/bash
#SBATCH -J b2np_v2_sh0
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=96G
#SBATCH -t 03:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_v2_shard0_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# D11-1 v2 hard check on 1 real shard (CPU): old probe vs probe v2 on the papers of real GPU unit shard_000 (all 6 conditions),
# same seeds / folds, 5 layers; old report vs report v2 on test roots 381_stage13/b2_np_v2check/{old,new}; max |diff| must be 0.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_b2_np_v2_check.py --real-shard0
