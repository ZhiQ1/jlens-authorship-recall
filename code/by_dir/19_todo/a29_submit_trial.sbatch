#!/bin/bash
#SBATCH -J a29_wait
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=2G
#SBATCH -t 00:40:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/391_groups/logs/a29/wait_%j.out
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# submits the addendum 29 one-shard trial (SHARDS=0, gate mode) once the user has < 8 GPU jobs; requeues itself (<= 12 times)
N=${ROUND:-1}
for i in $(seq 1 70); do
  n=$(squeue -u zhang.zhiqi2 -h -o '%P' 2>/dev/null | grep -c '^gpu')
  if [ -n "$n" ] && [ "$n" -lt 8 ]; then
    j=$(SHARDS=0 sbatch --parsable --export=ALL ~/jlens_work/19_todo/a29_gpu.sbatch) && { echo "$(date -Is) submitted a29 trial $j"; exit 0; }
    echo "$(date -Is) sbatch failed; check squeue/sacct"; exit 1
  fi
  sleep 30
done
if [ "$N" -lt 12 ]; then sbatch --export=ALL,ROUND=$((N+1)) ~/jlens_work/19_todo/a29_submit_trial.sbatch; echo requeued; else echo "STOP: no GPU slot after 12 rounds"; exit 1; fi
