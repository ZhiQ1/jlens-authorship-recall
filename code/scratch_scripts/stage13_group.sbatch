#!/bin/bash
# CPU: rerun M2, M2b, M2c with team/donor-grouped folds (SPLIT=group); outputs in summary_cpu_group/.
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --job-name=s13_group
#SBATCH --time=06:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=96G
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/381_stage13/logs/group_%j.log
export PYTHONDONTWRITEBYTECODE=1 HF_HOME=/scratch/$USER/hf HF_HUB_OFFLINE=1 OMP_NUM_THREADS=16 SPLIT=group
P=~/conda-envs/jlens/bin/python; D=~/jlens_work/13_stage13
cp /scratch/$USER/jlens/381_stage13/summary_cpu/M1_*.csv /scratch/$USER/jlens/381_stage13/summary_cpu_group/ 2>/dev/null
$P -u $D/stage13_cpu.py m2 && $P -u $D/stage13_m2b.py && $P -u $D/stage13_m2c.py
