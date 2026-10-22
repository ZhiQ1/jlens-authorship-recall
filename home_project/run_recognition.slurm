#!/bin/bash



#SBATCH --job-name=qwen32b_recog_a100

#SBATCH --partition=gpu-inter

#SBATCH --gres=gpu:a100:1

#SBATCH --cpus-per-task=4

#SBATCH --mem=32G

#SBATCH --time=01:00:00

#SBATCH --output=/scratch/zhang.zhiqi2/jlens/recog_%j.out

#SBATCH --error=/scratch/zhang.zhiqi2/jlens/recog_%j.err



module load miniforge3/26.7.2-0

conda activate /home/zhang.zhiqi2/conda-envs/jlens



export HF_HOME=/scratch/zhang.zhiqi2/hf



cd /home/zhang.zhiqi2/projects/dreaming-up-authors-code-v0



python 02_run_qwen3_recognition.py
