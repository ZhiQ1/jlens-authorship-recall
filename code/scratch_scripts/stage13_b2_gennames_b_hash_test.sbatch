#!/bin/bash
#SBATCH -J b2gnb_htest
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=32G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_hash_test_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# CPU test: hash runner on a tiny model (temp root), verifier on that root (+ a deliberately broken copy), verifier on the real legacy shards (read-only)
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4
PY=/home/zhang.zhiqi2/conda-envs/jlens/bin/python; D=/home/zhang.zhiqi2/jlens_work/13_stage13; T=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b_tiny/hash_test_$SLURM_JOB_ID
DRYRUN=1 bash $D/stage13_b2_gennames_b_gpu_multi_v3.sbatch 2,3,4
$PY -u $D/stage13_b2_gennames_b_gpu_hash.py tiny --root $T || exit 1
echo "== verify tiny (expect ok)"; $PY -u $D/stage13_b2_gennames_b_verify.py --root $T --allow-partial; echo "rc=$?"
mkdir -p $T/broken/raw $T/broken/names $T/broken/papers $T/broken/h2
cp $T/raw/shard_005.npz $T/broken/raw/; cp $T/names/shard_005.parquet $T/broken/names/; cp $T/h2/shard_005.csv $T/broken/h2/
$PY -c "import pandas as pd; p=pd.read_csv('$T/papers/shard_005.csv'); p.loc[0,'run_id']='other-run'; p.to_csv('$T/broken/papers/shard_005.csv', index=False)"
echo "== verify broken copy (expect FAIL listing run_id)"; $PY -u $D/stage13_b2_gennames_b_verify.py --root $T/broken --allow-partial; echo "rc=$?"
echo "== verify real legacy shards (read-only; writes summary/verify.json)"; $PY -u $D/stage13_b2_gennames_b_verify.py --root /scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b --allow-partial; echo "rc=$?"
