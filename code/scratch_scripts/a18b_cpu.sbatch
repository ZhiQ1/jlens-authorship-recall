#!/bin/bash
#SBATCH -J a18b_cpu
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 4
#SBATCH --mem=48G
#SBATCH -t 02:00:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/a18b/cpu_%x_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Addendum 18b CPU job (2026-11-17): tiny tests and analyses. env: ITEM, CMD (tiny | analyze | other subcommand), ARGS.
export HF_HOME=/scratch/zhang.zhiqi2/hf HF_HUB_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-4} A18B_TINY=${A18B_TINY:-0}
cd /home/zhang.zhiqi2/jlens_work/13_stage13
echo "$(date -Is) a18b item ${ITEM} ${CMD} ${ARGS} job $SLURM_JOB_ID on $(hostname)"
/home/zhang.zhiqi2/conda-envs/jlens/bin/python -u a18b_item${ITEM}.py ${CMD} ${ARGS}; RC=$?
echo "$(date -Is) exit $RC"; exit $RC
