#!/bin/bash
#SBATCH -J h2fict_check2
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v2/logs/h2fict_check2_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# H2 fictitious titles v2 checks (CPU + Crossref 1 req/s). ROUND=n, or FINAL=1 (selection + exclusions + sample20 table).
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false
O=${OUTDIR:-/scratch/zhang.zhiqi2/jlens/391_groups/h2_fictitious/v2}
cd ~/jlens_work/15_h2fict
if [ -n "${FINAL:-}" ]; then
  ~/conda-envs/jlens/bin/python h2fict_check_v2.py --final --out $O && ~/conda-envs/jlens/bin/python h2fict_v2_sample20.py $O
else
  ~/conda-envs/jlens/bin/python h2fict_check_v2.py --round ${ROUND:?} --out $O
fi
