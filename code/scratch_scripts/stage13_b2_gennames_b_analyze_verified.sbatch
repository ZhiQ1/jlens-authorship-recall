#!/bin/bash
#SBATCH -J b2gnb_analyze
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -t 12:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_analyze_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b analysis behind the per-shard consistency check: stage13_b2_gennames_b_verify.py (run id / gen hash or legacy content
# check) must pass, then the unchanged stage13_b2_gennames_b_analyze.py runs. Mismatch -> exit 1, no analysis.
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8
PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; D=/home/zhang.zhiqi2/jlens_work/13_stage13; R=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b
$PY -u $D/stage13_b2_gennames_b_verify.py --root $R || { echo "VERIFY FAILED: analysis not run"; exit 1; }
$PY -u $D/stage13_b2_gennames_b_analyze.py --root $R
