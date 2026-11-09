#!/bin/bash
#SBATCH -J b2gnb_xtest
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=4G
#SBATCH -t 00:15:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_shard0_extra_test_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# test of the shard-0 CPU addendum on tiny outputs: (1) runner tiny 11736505 (no names), (2) copy of the v3b pipeline replay (names)
export PYTHONDONTWRITEBYTECODE=1
PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; X=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_shard0_extra.py
T=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b_tiny
$PY -u $X --root $T/runner_11736505 --layers 0,1,2 || exit 1
R=$T/extra_test_$SLURM_JOB_ID; S=$T/run_v3b_11734831
mkdir -p $R/raw $R/names $R/papers
cp $S/resid_replay.npz $R/raw/shard_000.npz; cp $S/names_replay.parquet $R/names/shard_000.parquet; cp $S/papers_replay.csv $R/papers/shard_000.csv
$PY -u $X --root $R --layers 0,1,2
