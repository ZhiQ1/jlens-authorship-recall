# Stage 13 — what the middle layers hold if not the name (2026-10-28)

- Plan and predictions: combined report Part IV (https://claude.ai/artifact/QB335qoaBWvSdFyfvc2bSe).
- M1 and M2 (CPU, existing outputs): `stage13_cpu.py` / `.sbatch`.
  - M1 classifies the lens top-1 token at the name positions.
  - M2 runs probes for field, year from the title, citations and recognition, at the last title token and at ':'.
- M3 (GPU): `381_stage13.py`, a task contrast (authors / year / field prompts) over all 9,108 papers.
  - `dry` runs a tiny-model CPU check (14/14 PASS).
  - Runs as a hand-over from the Stage 12 work loop (`371_stage12.py handover13`), enabled by `381_stage13/logs/accept_handover`.
- Outputs go to `/scratch/zhang.zhiqi2/jlens/381_stage13/`.
