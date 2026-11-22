#!/bin/bash
#SBATCH -J claims31
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=8G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/numcheck/claims/claims32_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
CLAIMS_DEFS=claims_defs_v32 bash /scratch/zhang.zhiqi2/jlens/351_stage10/reports/numcheck/claims/claims_run.sh
