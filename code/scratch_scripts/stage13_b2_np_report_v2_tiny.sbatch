#!/bin/bash
#SBATCH -J b2np_rep2_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_np_report_v2_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# D11-1 report v2 tiny test (CPU): Vpd unit test -> (re)build the tiny root b2_np_tiny exactly as stage13_b2_np_tiny.sbatch if its
# original report is missing (steps skip finished outputs) -> report v2 --tiny -> compare V0 / V5x0 with the original report.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
set -e
$PY -u stage13_b2_np_report_v2_test.py --unit
if [ ! -f /scratch/zhang.zhiqi2/jlens/381_stage13/b2_np_tiny/reports/b2_np_report.md ]; then
  $PY -u stage13_b2_np_gpu.py --tiny --shards 0,1 --max-minutes 90
  $PY -u stage13_b2_np_lens.py --tiny
  for L in 32 40 48 52 56; do $PY -u stage13_b2_np_probe.py --tiny --layer $L; done
  $PY -u stage13_b2_np_report.py --tiny
fi
$PY -u stage13_b2_np_report_v2.py --tiny
$PY -u stage13_b2_np_report_v2_test.py --tiny-compare
echo "B2 NP REPORT V2 TINY DONE"
