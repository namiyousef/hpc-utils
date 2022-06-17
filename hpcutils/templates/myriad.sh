#!/bin/bash -l

#$ -m be

# -- USER REQUESTS:
# - wall clock (hours:minutes:seconds).
#$ -l h_rt={walltime}

# - gpus
#$ -l gpu=1

# - request A100 GPU node
# #$ -ac allow=L

# - Request RAM (must be an integer followed by M, G, or T)
#$ -l mem=32G

# - Request temp space
#$ -l tmpfs={storage_mem}G

# - Set the name of the job.
#$ -N {job_name}

# Set the working directory to somewhere in your scratch space.
#  This is a necessary step as compute nodes cannot write to $HOME.
# Replace "<your_UCL_id>" with your UCL user ID.
#$ -wd /home/ucabyn0/Scratch

# COPY NECESSARY FILES
cp -r {script_template_name} $TMPDIR/{script_template_name}
cp -r venv $TMPDIR/venv

cd $TMPDIR

# LOAD MODULES
module unload compilers mpi
module load compilers/gnu/4.9.2
module load python/3.7.4
module load cuda/10.1.243/gnu-4.9.2
module load cudnn/7.5.0.56/cuda-10.1

# venv should have the most recent version of argminer installed
source venv/bin/activate

source {script_template_name}
run_job_script

tar -zcvf $HOME/Scratch/{script_template_name}_$JOB_ID.tar.gz $TMPDIR
