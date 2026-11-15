#!/bin/bash
#SBATCH -p short --account=cs7980.202710 -c 2 --mem=16G -t 00:40:00
#SBATCH -J a16repar -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/prereg16_reparse_20261115_%j.out
#SBATCH --mail-type=END,FAIL --mail-user=zhang.zhiqi2@northeastern.edu
# Frozen parse rule (D16-4): prereg16_a16.py reparse, script sha256 must be db7c7386...
# Usage: sbatch prereg16_reparse_20261115.sbatch "B D" "1,2,...,28"
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1
cd ~/jlens_work/14_groups
h=$(sha256sum prereg16_a16.py | cut -d' ' -f1)
[ "$h" = db7c7386359522500cd128aeb1fe0e6b3a70d06bbb25b76d5916069963208449 ] || { echo "SCRIPT SHA MISMATCH $h"; exit 2; }
for it in $1; do ~/conda-envs/jlens/bin/python prereg16_a16.py reparse --item $it --shards "$2" || exit 1; done
