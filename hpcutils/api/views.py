from hpcutils.config import SCRIPTS_PATH, TEMPLATES_PATH
import os
def health_check():
    return 'OK'

def gpu_myriad(walltime, storage_mem, script_template_name, env_vars, job_name):
    myriad_template_path = os.path.join(TEMPLATES_PATH, 'myriad.sh')
    job_script_template_path = os.path.join(SCRIPTS_PATH, script_template_name)

    with open(myriad_template_path, 'r') as f:
        myriad_script = f.read()
        myriad_script = myriad_script.format(
            walltime=walltime,
            storage_mem=storage_mem,
            script_template_name=script_template_name,
            job_name=job_name
        )

    with open(f'Scratch/job_scripts/job_script.sh', 'w') as f:
        f.write(myriad_script)

    # build job script
    with open(job_script_template_path, 'r') as f:
        job_script = f.read()
        job_script = job_script.format(
            **env_vars
        )

        job_script_function = f'run_job_script () {{' \
                              f'\n\t{job_script}\n' \
                              f'}}'

    with open(f'Scratch/{script_template_name}', 'w') as f:
        f.write(job_script_function)

    # run job
    os.system(
        f'qsub Scratch/job_scripts/job_script.sh'
    )
    return 'f', 200


if __name__ == '__main__':
    walltime='walltime'
    storage_mem='storage_mem'
    script_template_name='div_examples.sh'
    job_name='job_name'
    env_vars = {
        'MODEL_NAME': 'django', 'TRAINING_METHOD': 'TRAINING_METHOD', 'LANGS': 'LANGS', 'MAX_LENGTH': 'MAX_LENGTH', 'DATASET': 'DATASET', 'BATCH_SIZE':'BATCH_SIZE', 'EPOCHS': 'EPOCHS', 'VERBOSE': 'VERBOSE', 'SEED': 'SEED'}

    # build myriad script
    with open('../../templates/myriad.sh', 'r') as f:
        myriad_script = f.read()
        myriad_script = myriad_script.format(
            walltime=walltime,
            storage_mem=storage_mem,
            script_template_name=script_template_name,
            job_name=job_name
        )
        print(myriad_script)

    # build job script
    with open(f'../../scripts/{script_template_name}', 'r') as f:
        job_script = f.read()
        job_script = job_script.format(
            **env_vars
        )

        job_script_function = f'run_job_script () {{' \
                              f'\n\t{job_script}\n' \
                              f'}}'

    with open(f'Scratch/{script_template_name}', 'w') as f:
        f.write(job_script_function)

    # cleanup (delete temp job script)