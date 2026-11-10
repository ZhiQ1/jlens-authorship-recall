#!/bin/bash
#SBATCH -J b2_orch
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 00:10:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/orch_b2/slurm_%j.log
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Batch-2 orchestrator poll (b2_orch.py); resubmits itself every 15 min until all items are done/stopped or orch_b2/STOP exists.
# Mail on FAIL only (END would mail 4x per hour); the GPU jobs it submits mail END,FAIL themselves.
export PYTHONDONTWRITEBYTECODE=1
cd ~/jlens_work/13_stage13
OUT=$(~/conda-envs/jlens/bin/python b2_orch.py poll 2>&1); echo "$OUT"
if echo "$OUT" | tail -1 | grep -q AGAIN; then
  others=$(squeue -u $USER -h -n b2_orch -t PD -o %i | grep -v "^${SLURM_JOB_ID}$" | wc -l)
  if [ "$others" = 0 ]; then
    # 2026-11-09 killguard: the next poll avoids every node with a running job of ours (incl. cc_claude, blog-holder): a poll ending
  # next to them would be an epilog trigger (HANDOFF "Cluster gotchas").
  EX=$(~/conda-envs/jlens/bin/python ~/jlens_work/killguard.py cpu_exclude --ignore $SLURM_JOB_ID 2>/dev/null); echo "next poll ${EX:-without --exclude}"
    for i in 1 2 3; do sbatch --begin=now+15minutes $EX ~/jlens_work/13_stage13/b2_orch.sbatch && break; sleep 15
      squeue -u $USER -h -n b2_orch -t PD | grep -q . && break; done
  else echo "another b2_orch poll is already queued - not resubmitting"; fi
fi
