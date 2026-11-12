#!/bin/bash
#SBATCH -J b2gnb_conf
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_conf_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b POST-HOC confidence replay (事后，探索性): shard list as the first argument (e.g. 0 or 1,2,...,47). Exit 3 = replay check < 0.99 (REPLAY_STOP).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2gnb_conf $SLURM_JOB_ID on $(hostname) shards=$1"
SHARDS="$1"; [ -n "$SHARDS" ] || { echo "no shard list argument"; exit 1; }
CMD=(/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_conf.py gpu --shards "$SHARDS" --minutes 41)
if [ "${DRYRUN:-0}" = 1 ]; then echo "DRYRUN: ${CMD[*]}"; exit 0; fi
"${CMD[@]}"
