#!/bin/bash
#SBATCH -J a20_gpu
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH --exclude=d1028
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a20/gpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 20 main GPU worker. Partition/GPU given on the sbatch command line (H200 gpu-interactive or A100-80 gpu,gpu-short).
# Env (via --export=ALL): SHARDS=<a-b+c...> (Stage 11 shard ids), PARITY=1 (shard-0 parity of true/false_0..4 vs Stage 10).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python
echo "$(date -Is) a20 gpu job $SLURM_JOB_ID on $(hostname) part=$SLURM_JOB_PARTITION shards=$SHARDS parity=$PARITY"
nvidia-smi --query-gpu=name,memory.total --format=csv
cd ~/jlens_work/15_h2fict
ARGS="--shards ${SHARDS:?}"; if [ "$PARITY" = "1" ]; then ARGS="$ARGS --parity"; fi
$PY -u h2_main_gpu.py work $ARGS --max-minutes 38
$PY -u h2_main_gpu.py remaining
echo "$(date -Is) end"
