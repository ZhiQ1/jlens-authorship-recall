#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:40:00
#SBATCH -J v22xpp
#SBATCH -o /home/zhang.zhiqi2/jlens_work/33_v73/pp_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
bash /home/zhang.zhiqi2/jlens_work/33_v73/pp.sh
