#!/bin/bash
#SBATCH -J b2cd_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/b2_cd_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 B: whole pipeline on a random 64-layer tiny Qwen3 (CPU): freeze -> E1/E2 units -> hard check (identical PASS,
# perturbed FAIL) -> skip/remaining -> analysis; then the hard-check unit test on stored Stage 11 shard 0.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/14_groups
PY=~/conda-envs/jlens/bin/python
$PY b2_cd.py tiny --root /scratch/zhang.zhiqi2/jlens/391_groups/test_b2_cd_tiny_$SLURM_JOB_ID; R1=$?
$PY b2_cd.py unittest; R2=$?
echo "tiny exit $R1 unittest exit $R2"
[ $R1 = 0 ] && [ $R2 = 0 ]
