#!/bin/bash
#SBATCH -J b2gnb_mtest
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:20:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_multi_v2_test_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# CPU test: (1) argument reaches the v2 GPU script intact (DRYRUN), (2) multi runner parses a comma list and skips finished shards
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
echo "own argument: $1"
DRYRUN=1 bash /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_gpu_multi_v2.sbatch "$1"
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_gpu_multi.py --shards 0,1,7,37
