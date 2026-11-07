#!/bin/bash
#SBATCH -J b2B_an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2B_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 2 group B analyses (CPU). Each item runs even if another fails; exit 3 if any HARD CHECK failed (the item's report says
# which). ITEMS="e1noise e1t5 x3role m3tok" (default all).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python; RC=0
for it in ${ITEMS:-e1noise e1t5 x3role m3tok}; do
  $PY stage13_b2B_analyze.py $it; r=$?; echo "ITEM $it exit $r"; [ $r != 0 ] && RC=3
done
exit $RC
