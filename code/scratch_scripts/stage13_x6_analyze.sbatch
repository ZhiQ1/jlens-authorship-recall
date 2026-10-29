#!/bin/bash
#SBATCH -J s13_x6
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 2
#SBATCH --mem=32G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x6_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
cd ~/jlens_work/13_stage13
# 1) self-test: all 5 titles = Stage 11 false_0 -> every R must equal Stage 11 E1, every difference 0
~/conda-envs/jlens/bin/python stage13_x6_analyze.py /scratch/zhang.zhiqi2/jlens/381_stage13/test_x6 > /scratch/zhang.zhiqi2/jlens/381_stage13/logs/x6_selftest_$SLURM_JOB_ID.txt 2>&1 || echo "WARN self-test crashed"
~/conda-envs/jlens/bin/python - <<'PY' || echo "WARN self-test comparison crashed"
import pandas as pd, numpy as np
D = pd.read_csv('/scratch/zhang.zhiqi2/jlens/381_stage13/summary_x6/x6_recovery.csv')
E = pd.read_csv('/scratch/zhang.zhiqi2/jlens/361_stage11/summary/E1_recovery.csv')
m = D[D.false_title == 'false_3'].merge(E, on=['group', 'layer']); dmax = float(np.abs(m.R - m.recovery).max())
diff = D[D.false_title.str.contains(' - ')]; z = float(np.abs(diff[['R', 'lo', 'hi']].to_numpy()).max())
print(f'SELFTEST R vs Stage 11 E1 max|diff| {dmax:.2e} over {len(m)} rows; per-title differences max|.| {z:.2e} ->', 'PASS' if dmax < 1e-9 and z < 1e-12 else 'WARN')
PY
# 2) real run
~/conda-envs/jlens/bin/python stage13_x6_analyze.py
