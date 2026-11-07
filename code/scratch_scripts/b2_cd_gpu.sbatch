#!/bin/bash
#SBATCH -J b2cd_gpu
#SBATCH -p gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/b2_cd_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 11 B GPU. MODE=gate (default): hard-check re-run of Stage 11 shard 0 (E1+E2) + C shard 0 (E1+E2), one real shard.
# MODE=all: every remaining unit (claims, skip-if-exists, stops ~6 min before the limit). AUTO=1: resubmit itself while units
# remain (only if the hard check PASSED and work exited 0; ROUND <= 4); when nothing remains, submit the analysis.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python; D=~/jlens_work/14_groups
nvidia-smi --query-gpu=name,memory.total --format=csv
cd $D
if [ "${MODE:-gate}" = all ]; then A="--all"; else A="--gate"; fi
$PY b2_cd.py work $A --max-minutes 38; RC=$?
echo "work exit $RC"
LEFT=$($PY b2_cd.py remaining | grep -o 'REMAINING [0-9]*' | awk '{print $2}')
HC=$(grep -o '"status": "[A-Z]*"' /scratch/zhang.zhiqi2/jlens/391_groups/b2_cd/summary/hardcheck_rerun.json 2>/dev/null | tail -1)
ROUND=${ROUND:-1}; echo "left=$LEFT hardcheck=$HC round=$ROUND"
if [ "$RC" = 0 ] && [ "$AUTO" = 1 ] && [ "${LEFT:-0}" -gt 0 ] && [[ "$HC" == *PASS* ]] && [ "$ROUND" -lt 4 ]; then
  for i in 1 2 3; do sbatch --export=ALL,MODE=all,AUTO=1,ROUND=$((ROUND+1)) $D/b2_cd_gpu.sbatch && break; sleep 20; squeue -u $USER -n b2cd_gpu -h | grep -q . && break; done
elif [ "$RC" = 0 ] && [ "$AUTO" = 1 ] && [ "${LEFT:-1}" = 0 ]; then
  sbatch $D/b2_cd_analyze.sbatch
fi
exit $RC
