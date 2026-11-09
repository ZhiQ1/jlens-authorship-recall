#!/bin/bash
#SBATCH -J b2gnb_s0extra
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -t 00:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_shard0_extra_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b shard-0 CPU addendum (sections a-c -> b2_gennames_b/shard0_cost_extra.md, link appended to shard0_cost.md).
# Submitted with --dependency=afterany:<shard-0 GPU job>. Submits NOTHING; the remaining 47 shards need a manual decision.
export PYTHONDONTWRITEBYTECODE=1
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u /home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_shard0_extra.py --root /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b
