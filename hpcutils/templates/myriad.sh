#!/bin/bash -l

#$ -m be

# -- USER REQUESTS:
# - wall clock (hours:minutes:seconds).
#$ -l h_rt={walltime}

# - gpus
#$ -l gpu=1

# - request V100 only
#$ -ac allow=EF

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

export PROJECT_NAME={project_name}
export PROJECT_PATH=job_metadata/$PROJECT_NAME
export JOB_PATH=$PROJECT_PATH/$JOB_ID
export SCRIPT_TEMPLATE_NAME={script_template_name}
# COPY NECESSARY FILES
cp -r $JOB_PATH/$SCRIPT_TEMPLATE_NAME $TMPDIR/$SCRIPT_TEMPLATE_NAME
cp -r $PROJECT_PATH/venv $TMPDIR/venv

cd $TMPDIR

# LOAD MODULES
module unload compilers mpi
module load compilers/gnu/4.9.2
module load python/3.7.4
module load cuda/10.1.243/gnu-4.9.2
module load cudnn/7.5.0.56/cuda-10.1

# venv should have the most recent version of argminer installed
source venv/bin/activate

source $SCRIPT_TEMPLATE_NAME
run_job_script

# DELETE FILES COPIED FROM JOB
rm -r venv
rm $SCRIPT_TEMPLATE_NAME

# TODO where to add job_completion_metadata???
tar -zcvf $HOME/Scratch/$JOB_PATH/job_output/$PROJECT_NAME.$JOB_ID.tar.gz $TMPDIR
