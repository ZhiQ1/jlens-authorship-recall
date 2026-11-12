#!/bin/bash
#SBATCH -J b2gnb_ctest
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:50:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_conf_test_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# 2-11b post-hoc confidence: CPU test of the whole pipeline (tiny-model replay + gate; analysis on shard-0 data with synthetic confidence values)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; D=/home/zhang.zhiqi2/jlens_work/13_stage13; T=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b_tiny/conf_test_$SLURM_JOB_ID
R=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b
DRYRUN=1 bash $D/stage13_b2_gennames_b_conf_gpu.sbatch 0
$PY -u $D/stage13_b2_gennames_b_conf.py tiny --out $T || exit 1
A=$T/ana; mkdir -p $A/names $A/raw $A/conf
cp $R/names/shard_000.parquet $A/names/; cp $R/raw/shard_000.npz $A/raw/
$PY - <<PYEOF
import pandas as pd, numpy as np, json
N=pd.read_parquet('$A/names/shard_000.parquet'); K=N[N.status.isin(['M','H'])]; r=np.random.default_rng(0)
C=pd.DataFrame(dict(paper_id=K.paper_id, item_index=K.item_index, status=K.status, lp_first=-r.exponential(2,len(K)), ent_pre=r.exponential(1,len(K)),
   lp_mean=-r.exponential(1,len(K)), lp_sum=0.0, n_tok=1, tf_argmax_first_eq=True)); C.to_parquet('$A/conf/shard_000.parquet', index=False)
json.dump(dict(shard=0, agree=99, positions=100, h2_agree=10, h2_positions=10), open('$A/conf/replay_000.json','w'))
PYEOF
$PY -u $D/stage13_b2_gennames_b_conf_analyze.py --root $A --allow-partial --nb 200 --layers 16,56 --out $A/report_test.md && head -40 $A/report_test.md
