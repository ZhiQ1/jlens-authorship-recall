#!/bin/bash
#SBATCH -J b2gnb_submit
#SBATCH -p short
#SBATCH --account=cs7980.202710
#SBATCH -c 1
#SBATCH --mem=1G
#SBATCH -t 12:30:00
#SBATCH -o /scratch/zhang.zhiqi2/jlens/381_stage13/logs/b2_gennames_b_submitter_%j.log
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=zhang.zhiqi2@northeastern.edu
# Submits stage13_b2_gennames_b_gpu.sbatch (shard 0) once: every 15 min, at most 48 rounds; before each attempt checks squeue/sacct
# for an existing b2gnb_shard0 job (pending/running/finished) and the marker file; stops after success.
S=/home/zhang.zhiqi2/jlens_work/13_stage13/stage13_b2_gennames_b_gpu.sbatch
M=/scratch/zhang.zhiqi2/jlens/381_stage13/b2_gennames_b/summary/shard0_submitted_jobid
for i in $(seq 1 48); do
  if [ -s "$M" ]; then echo "$(date -Is) marker present ($(cat $M)): done"; exit 0; fi
  q=$(squeue -u zhang.zhiqi2 -n b2gnb_shard0 -h -o %i 2>/dev/null | head -1)
  [ -z "$q" ] && q=$(sacct -u zhang.zhiqi2 -X -n -S now-2days --name=b2gnb_shard0 -o JobID 2>/dev/null | head -1 | tr -d ' ')
  if [ -n "$q" ]; then echo "$q" > "$M"; echo "$(date -Is) round $i: job $q already exists: done"; exit 0; fi
  o=$(sbatch "$S" 2>&1); echo "$(date -Is) round $i: $o"
  case "$o" in Submitted*) echo "$o" | awk '{print $4}' > "$M"; exit 0;; esac
  sleep 20
  q=$(squeue -u zhang.zhiqi2 -n b2gnb_shard0 -h -o %i 2>/dev/null | head -1)
  if [ -n "$q" ]; then echo "$q" > "$M"; echo "$(date -Is) round $i: submitted despite error ($q): done"; exit 0; fi
  sleep 880
done
echo "$(date -Is) 48 rounds without success"; exit 1
