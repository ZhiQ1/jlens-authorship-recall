#!/bin/bash
#SBATCH -J g391_b1p12f
#SBATCH -p gpu,gpu-short,gpu-interactive
#SBATCH --account=cs7980.202710
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=a100@80g
#SBATCH -c 8
#SBATCH --mem=96G
#SBATCH -t 00:45:00
#SBATCH --time-min=00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/b1_p12f_gpu_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# v2 (2026-11-06 21:00) of b1_p12f_gpu.sbatch (that file is unchanged): same b1_p12f.py work command.
# Changes: 3 partitions, --time-min 30 (was 20 until 2026-11-07 00:35; 20 min left room for only 1 unit after the ~8-min model load) (backfill; work() caps its budget at the real time left - 5 min),
# LANE=<units spec> so two disjoint chains can run in parallel; each lane resubmits itself while ITS units remain;
# analyze is submitted once (atomic mkdir lock) when no unit at all remains. A crash (work exit != 0) stops the lane.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
PY=~/conda-envs/jlens/bin/python; D=~/jlens_work/14_groups; SUM=/scratch/zhang.zhiqi2/jlens/391_groups/summary_b1_p12f
nvidia-smi --query-gpu=name,memory.total --format=csv || echo "WARN nvidia-smi failed"
cd $D
$PY b1_p12f.py work --units "$LANE" --max-minutes 40; RC=$?
echo "work exit $RC lane=$LANE"
LEFT_ALL=$($PY b1_p12f.py remaining | grep -o 'REMAINING [0-9]*' | awk '{print $2}')
LEFT_LANE=$($PY - "$LANE" <<'EOF'
import sys, importlib.util
spec = importlib.util.spec_from_file_location('p', '/home/zhang.zhiqi2/jlens_work/14_groups/b1_p12f.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(sum(not m.out_path(u).exists() for u in m.parse_units(sys.argv[1])))
EOF
)
HC=$(grep -o '"status": "[A-Z]*"' $SUM/hardcheck_a_rerun.json 2>/dev/null | tail -1)
ROUND=${ROUND:-1}
echo "left_all=$LEFT_ALL left_lane=$LEFT_LANE hardcheck_a=$HC round=$ROUND"
if [ "$RC" = 0 ] && [ "${LEFT_LANE:-0}" -gt 0 ] && [[ "$HC" == *PASS* ]] && [ "$ROUND" -lt 16 ]; then
  for i in 1 2 3; do sbatch --export=ALL,LANE="$LANE",ROUND=$((ROUND+1)) $D/b1_p12f_gpu_v2.sbatch && break; sleep 20; done
elif [ "$RC" = 0 ] && [ "${LEFT_ALL:-1}" = 0 ]; then
  if mkdir $SUM/.analyze_submitted 2>/dev/null; then sbatch $D/b1_p12f_analyze.sbatch; else echo "analyze already submitted by the other lane"; fi
fi
