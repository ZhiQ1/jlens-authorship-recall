#!/bin/bash
#SBATCH -J numcheck
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=12G
#SBATCH -t 01:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/351_stage10/reports/numcheck/out/numcheck_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
bash /scratch/zhang.zhiqi2/jlens/351_stage10/reports/numcheck/numcheck_run.sh
