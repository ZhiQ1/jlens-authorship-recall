#!/bin/bash
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -t 01:00:00
#SBATCH -J v22xlo
#SBATCH -o /home/zhang.zhiqi2/jlens_work/34_v75/lo_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
set -e
O=/home/zhang.zhiqi2/jlens_work/34_v75/lo; mkdir -p $O
soffice -env:UserInstallation=file:///scratch/zhang.zhiqi2/lo_profile_v22z --headless --convert-to pdf --outdir $O "$1"
B=$(basename "$1" .pptx)
PYTHONPATH=/scratch/zhang.zhiqi2/pylib2 ~/conda-envs/jlens/bin/python /home/zhang.zhiqi2/jlens_work/34_v75/raster.py $O/$B.pdf ${2:-131}
ls $O
