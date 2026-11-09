#!/bin/bash
# CPU: Stage 13 M2 with all 5 false titles (CHK A3; user approval 2026-11-08). Usage:
#   sbatch stage13_m2_f5.sbatch run --title false_k     (one title)
#   sbatch stage13_m2_f5.sbatch hardcheck               (run --title false_0, then compare with the published false_0 rows; exit 1 on mismatch)
#   sbatch stage13_m2_f5.sbatch analyse                 (five-title mean table + reports/m2_f5_report.md)
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_m2f5
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/m2f5_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16
PY=~/conda-envs/jlens/bin/python; S=~/jlens_work/13_stage13/stage13_m2_f5.py
echo "job $SLURM_JOB_ID host $(hostname) args: $*"; lscpu | grep -E 'Model name' || true
if [ "$1" = hardcheck ]; then
  $PY -u $S run --title false_0 || exit 2
  $PY -u $S check; exit $?
fi
$PY -u $S "$@"
