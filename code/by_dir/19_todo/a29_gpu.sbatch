#!/bin/bash
#SBATCH -J a29_gpu
#SBATCH -p gpu
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH --exclude=d1028
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a29/gpu_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# usage: SHARDS=0 sbatch --export=ALL a29_gpu.sbatch (gate mode)   |   ALL=1 sbatch --export=ALL a29_gpu.sbatch
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
nvidia-smi --query-gpu=name,memory.total --format=csv
if [ "${ALL:-0}" = 1 ]; then A="--all"; else A="--shards ${SHARDS:-0}"; fi
~/conda-envs/jlens/bin/python ~/jlens_work/19_todo/a29_layerfill.py run $A --max-minutes 38
# gate mode (trial): queue the CPU gate after this job (cost check + remaining shards + analysis)
if [ "${ALL:-0}" != 1 ] && [ -z "$NO_GATE" ]; then
  sbatch --dependency=afterok:$SLURM_JOB_ID --export=ALL,ITEM=a29,TRIAL=$SLURM_JOB_ID ~/jlens_work/19_todo/todo_gate.sbatch || echo "WARN gate submit failed"
fi
