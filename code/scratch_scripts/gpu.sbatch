#!/bin/bash
#SBATCH -J a3x_gpu
#SBATCH -p gpu
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --exclude=d1028
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a3x/gpu_%x_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# env: SCRIPT (a30_h5.py | a31_dla.py | a32_sweep.py), SHARDS (e.g. 0 or 1-6)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) $SCRIPT work SHARDS=$SHARDS job $SLURM_JOB_ID on $(hostname)"; nvidia-smi --query-gpu=name,memory.total --format=csv || true
cd /home/zhang.zhiqi2/jlens_work/24_gpubatch; T0=$(date +%s)
/home/zhang.zhiqi2/conda-envs/jlens/bin/python $SCRIPT work --shards "$SHARDS" --max-minutes 38; RC=$?
echo "$(date -Is) exit $RC elapsed_s=$(( $(date +%s) - T0 ))"; exit $RC
