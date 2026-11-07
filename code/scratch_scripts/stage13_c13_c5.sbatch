#!/bin/bash
#SBATCH -J c13_c5
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/c13_c5_%x_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 13 C-5. Env: PART=x|fmt MODE=repro|ext [TINY=1]. Skip if the part's last output exists.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
R=/scratch/zhang.zhiqi2/jlens/381_stage13/summary_c13/c5${TINY:+_tiny}/$MODE
if [ "$PART" = x ]; then F=$R/X3_tc_spec_vs_logit.csv; else F=$R/X1_cond_by_first_role.csv; fi
[ -s "$F" ] && { echo "exists: $F (skip)"; exit 0; }
cd ~/jlens_work/13_stage13
~/conda-envs/jlens/bin/python -u stage13_c13_c5.py --part $PART --mode $MODE ${TINY:+--tiny}
