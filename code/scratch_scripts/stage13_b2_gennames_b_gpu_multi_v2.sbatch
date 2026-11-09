#!/bin/bash
#SBATCH -J b2gnb_grp
#SBATCH -p gpu,gpu-short
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_grp_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b (addendum 15, locked) v2: shard list as the FIRST ARGUMENT (e.g. sbatch this.sbatch 1,2,3,4,5,6). v1 passed SHARDS via
# --export=ALL,SHARDS=1,2,... and sbatch split that on the commas, so every job got only its first shard. DRYRUN=1 only prints.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "$(date -Is) b2gnb_grp $SLURM_JOB_ID on $(hostname) shards=$1"
SHARDS="$1"; [ -n "$SHARDS" ] || { echo "no shard list argument"; exit 1; }
CMD=(/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_gpu_multi.py --shards "$SHARDS" --minutes 41)
if [ "${DRYRUN:-0}" = 1 ]; then echo "DRYRUN: ${CMD[*]}"; exit 0; fi
"${CMD[@]}"
