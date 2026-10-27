#!/bin/bash
# Stage 11 queue keeper (CPU): keeps the A100 submit slots filled with s11w workers while units remain (see stage11_keeper.py).
#SBATCH --job-name=s11_keeper
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --time=1-23:50:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --signal=B:USR1@600
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/361_stage11/logs/keeper_%j.log
ROUND=${ROUND:-1}; D=~/jlens_work/11_stage11; export PYTHONDONTWRITEBYTECODE=1
trap 'kill $PID 2>/dev/null; [ "$ROUND" -lt 6 ] && sbatch --export=ALL,ROUND=$((ROUND+1)) $D/stage11_keeper.sbatch; exit 0' USR1
~/conda-envs/jlens/bin/python -u $D/stage11_keeper.py &
PID=$!; wait $PID
