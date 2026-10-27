#!/bin/bash
# Stage 12 queue keeper (CPU): keeps the A100 submit slots filled with s11w workers while units remain (see stage12_keeper.py).
#SBATCH --job-name=s12_keeper
#SBATCH --partition=short
#SBATCH --account=cs7980.202710
#SBATCH --time=1-23:50:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --signal=B:USR1@600
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
#SBATCH --output=/scratch/zhang.zhiqi2/jlens/371_stage12/logs/keeper_%j.log
ROUND=${ROUND:-1}; D=~/jlens_work/12_stage12; export PYTHONDONTWRITEBYTECODE=1
trap 'kill $PID 2>/dev/null; [ "$ROUND" -lt 6 ] && sbatch --export=ALL,ROUND=$((ROUND+1)) $D/stage12_keeper.sbatch; exit 0' USR1
~/conda-envs/jlens/bin/python -u $D/stage12_keeper.py &
PID=$!; wait $PID
