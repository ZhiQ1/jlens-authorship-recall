#!/bin/bash
#SBATCH -J b2np_v2_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_v2_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# D11-1 v2 tiny test (CPU): Vpd unit test -> probe v2 on the tiny root (b2_np_tiny, existing tiny GPU data) at 5 layers ->
# report v2 --tiny -> hard check: old probe/report vs new, V0 / V5x0 incl. controls, max |diff| = 0.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
set -e
$PY -u stage13_b2_np_report_v2_test.py --unit
for L in 32 40 48 52 56; do $PY -u stage13_b2_np_probe_v2.py --tiny --layer $L; done
$PY -u stage13_b2_np_report_v2.py --tiny
$PY -u stage13_b2_np_v2_check.py --tiny
echo "B2 NP V2 TINY DONE"
