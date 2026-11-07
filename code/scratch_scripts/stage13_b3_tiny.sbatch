#!/bin/bash
#SBATCH -J b3_tiny
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 16
#SBATCH --mem=64G
#SBATCH -t 04:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b3_tiny_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch 3 tiny whole-pipeline test + unit tests (CPU). Random 64-layer Qwen3 (real tokenizer), random 64x64 lens, REAL data rows.
#  1 unit tests on real stored data (+ P1 prediction of the 3-3 hard check)
#  2 tiny Stage 10 root; frozen 351_stage10.run on the tiny model writes the tiny 'stored' L24/L48 reference (shard 0)
#  3 3-1 gate (shard 0, 7 conditions) -> gate.json PASS expected; re-run = skip-if-exists; remaining; chain --dry
#  4 perturbed copy -> gate-check exit 3; unperturbed -> exit 0
#  5 3-1 analysis (tiny); 3-2 gate + analysis (tiny)
#  6 3-3: tiny old-path reference (frozen Stage 5 helper.readout, 40 contexts) -> gate -> all (2 papers) -> analysis
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=16
cd ~/jlens_work/13_stage13
PY=~/conda-envs/jlens/bin/python
declare -A RC
step() { local n=$1; shift; echo "=== STEP $n: $*"; "$@"; RC[$n]=$?; echo "=== STEP $n exit ${RC[$n]}"; }
step U_real   $PY -u stage13_b3_unittest.py real
step root     $PY -u stage13_b3_s10_gpu.py tiny-root --item 3-1
step ref      $PY -u stage13_b3_s10_gpu.py tiny-ref --item 3-1 --shards 0
step g31      $PY -u stage13_b3_s10_gpu.py run --item 3-1 --shards 0 --tiny --max-minutes 100
step g31skip  $PY -u stage13_b3_s10_gpu.py run --item 3-1 --shards 0 --tiny --max-minutes 100
step rem31    $PY -u stage13_b3_s10_gpu.py remaining --item 3-1 --tiny
step chain31  $PY -u stage13_b3_s10_gpu.py chain --item 3-1 --tiny --dry
step U_pert   $PY -u stage13_b3_unittest.py pert
step an31     $PY -u stage13_b3_s10_analyze.py --item 3-1 --tiny
step g32      $PY -u stage13_b3_s10_gpu.py run --item 3-2 --shards 0 --tiny --max-minutes 150
step an32     $PY -u stage13_b3_s10_analyze.py --item 3-2 --tiny
step ref71    $PY -u stage13_b3_71b_gpu.py tiny-ref --tiny-contexts 40
step g71      $PY -u stage13_b3_71b_gpu.py run --gate --tiny --max-minutes 100
step all71    $PY -u stage13_b3_71b_gpu.py run --all --tiny --tiny-papers 2 --max-minutes 100
step chain71  $PY -u stage13_b3_71b_gpu.py chain --tiny --dry
step an71     $PY -u stage13_b3_71b_analyze.py --tiny
echo "=== SUMMARY"; for k in U_real root ref g31 g31skip rem31 chain31 U_pert an31 g32 an32 ref71 g71 all71 chain71 an71; do echo "$k ${RC[$k]}"; done
