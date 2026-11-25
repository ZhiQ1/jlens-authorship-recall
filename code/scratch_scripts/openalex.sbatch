#!/bin/bash
#SBATCH -J oa_fetch
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 00:45:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/ext/openalex_20261122/logs_%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
cd /tmp
timeout 2580 ~/conda-envs/jlens/bin/python -I ~/jlens_work/24_ext/openalex_fetch.py fetch
~/conda-envs/jlens/bin/python -I ~/jlens_work/24_ext/openalex_fetch.py build | tail -3
