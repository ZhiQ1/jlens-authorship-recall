#!/bin/bash
#SBATCH -J b2c_c3b
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2c_c3b_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 13 C-3b (batch 2 group C, CPU). MODE=selftest | tiny | full (default full). Full skips if the report exists.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
R=/scratch/zhang.zhiqi2/jlens/381_stage13
cd ~/jlens_work/13_stage13
case "${MODE:-full}" in
  selftest) exec ~/conda-envs/jlens/bin/python -u stage13_b2_c3b.py --selftest ;;
  tiny) exec ~/conda-envs/jlens/bin/python -u stage13_b2_c3b.py --tiny ;;
  full) [ -s $R/reports/c13_C3b.md ] && { echo "exists: $R/reports/c13_C3b.md (skip)"; exit 0; }
        exec ~/conda-envs/jlens/bin/python -u stage13_b2_c3b.py ;;
esac
