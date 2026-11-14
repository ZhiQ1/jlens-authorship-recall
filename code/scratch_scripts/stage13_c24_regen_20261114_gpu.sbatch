#!/bin/bash
#SBATCH -J c24regen
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/c24_regen_20261114_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# C24 item 1a option A (POST-HOC): regenerate shard 0 with saved per-step logits stats + replay + 1a rule. Checks are WARN only.
# Submit with killguard: EX=$(python ~/jlens_work/killguard.py exclude --name c24regen --minutes 45); sbatch $EX this_file
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) c24regen $SLURM_JOB_ID on $(hostname)"
CMD=(/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_c24_regen_20261114.py gpu)
if [ "${DRYRUN:-0}" = 1 ]; then echo "DRYRUN: ${CMD[*]}"; exit 0; fi
"${CMD[@]}"
