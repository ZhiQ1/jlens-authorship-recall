#!/bin/bash
#SBATCH -J b2B_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2B_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 2 group B (2-4, 2-8, 2-3, 2-10): whole pipeline on a random 64-layer tiny Qwen3 (CPU) -> GPU units + gate checks
# (identical PASS / perturbed FAIL) -> all analyses on the tiny outputs; then the hard-check unit tests on stored real data
# (identical -> PASS, perturbed -> FAIL) and the real CPU hard check of 2-8 (false_0 arm vs published E1t).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python; ROOT=/scratch/zhang.zhiqi2/jlens/381_stage13/b2B_tiny_$SLURM_JOB_ID
$PY stage13_b2B_gpu.py tiny --root $ROOT; R1=$?
$PY stage13_b2B_analyze.py tiny --root $ROOT; R2=$?
$PY stage13_b2B_analyze.py unittest; R3=$?
$PY stage13_b2B_analyze.py hardcheck_e1t5; R4=$?
echo "tiny-gpu $R1 tiny-analysis $R2 unittest $R3 hardcheck_e1t5 $R4"
[ $R1 = 0 ] && [ $R2 = 0 ] && [ $R3 = 0 ] && [ $R4 = 0 ]
