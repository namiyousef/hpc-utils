#   This is the most basic QSUB file needed for this cluster.
#   Further examples can be found under /share/apps/examples
#   Most software is NOT in your PATH but under /share/apps
#
#   For further info please read http://hpc.cs.ucl.ac.uk
#   For cluster help email cluster-support@cs.ucl.ac.uk
#
#   NOTE hash dollar is a scheduler directive not a comment.

# These are flags you must include - Two memory and one runtime.
# Runtime is either seconds or hours:min:sec

#$ -m be
#$ -l tmem=32G
#$ -l gpu=true,gpu_type=(gtx1080ti|titanxp|titanx|rtx2080ti)
# #$ -l h_vmem=32G
#$ -l h_rt={walltime}

#These are optional flags but you probably want them in all jobs

#$ -S /bin/bash
#$ -j y
#$ -N {job_name}
#$ -wd /home/yousnami

#The code you want to run now goes here.

export PROJECT_NAME={project_name}
export PROJECT_PATH=job_metadata/$PROJECT_NAME
export JOB_PATH=$PROJECT_PATH/$JOB_ID
export SCRIPT_TEMPLATE_NAME={script_template_name}
# COPY NECESSARY FILES
cp -r $JOB_PATH/$SCRIPT_TEMPLATE_NAME $TMPDIR/$SCRIPT_TEMPLATE_NAME
cp -r $PROJECT_PATH/venv $TMPDIR/venv
cp -r $PROJECT_PATH/data $TMPDIR/data

cd $TMPDIR

# LOAD MODULES
module load python/3.7.2
module load cuda/10.1

source venv/bin/activate

source $SCRIPT_TEMPLATE_NAME
run_job_script

# DELETE FILES COPIED FROM JOB
rm -r venv
rm $SCRIPT_TEMPLATE_NAME
rm -r data


tar -zcvf $HOME/Scratch/$PROJECT_NAME.$JOB_ID.tar.gz $TMPDIR