#!/bin/bash
#SBATCH -J b2gnb_shard0
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH --time-min=00:20:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b (addendum 15, locked) real runner: SHARD=<k> (default 0, writes shard0_cost.md). H2 hard fail exits 2.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2gnb $SLURM_JOB_ID on $(hostname) shard=${SHARD:-0}"
cd /home/zhang.zhiqi2/jlens_work/13_stage13
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u stage13_b2_gennames_b_gpu.py gpu --shard ${SHARD:-0} --cost
