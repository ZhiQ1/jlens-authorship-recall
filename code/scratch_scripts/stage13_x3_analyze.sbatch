#!/bin/bash
#SBATCH -J s13_x3an
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=24G
#SBATCH -t 01:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x3_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# X3 analysis (prereg.json X3 + addenda 1, 2, 4, 5). NOT submitted automatically: submit after all 24 para_run shards exist,
#   sbatch --dependency=afterok:<para_run job ids> ~/jlens_work/13_stage13/stage13_x3_analyze.sbatch
# Outputs: 381_stage13/summary_x3/x3_*.csv, 381_stage13/reports/x3_report.md (does not touch summary_x3/para_nli.csv).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/13_stage13
n=$(ls /scratch/zhang.zhiqi2/jlens/381_stage13/raw/para_run/shard_*.npz 2>/dev/null | wc -l)
echo "para_run shards present: $n / 24"; [ "$n" -lt 24 ] && echo "WARN: only $n of 24 shards; the analysis runs on what exists and marks the report PARTIAL"
for f in /scratch/zhang.zhiqi2/jlens/381_stage13/summary_x3/x3_gap.csv /scratch/zhang.zhiqi2/jlens/381_stage13/reports/x3_report.md; do
  [ -e "$f" ] && mv "$f" "$f.before_$(date +%Y%m%d_%H%M%S)" && echo "kept previous $f under a new name"
done
~/conda-envs/jlens/bin/python stage13_x3_analyze.py
