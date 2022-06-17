from hpcutils.config import SCRIPTS_PATH, TEMPLATES_PATH, CLUSTER_RESOURCE_MAPPING
import os
import json

def health_check():
    return 'OK'

# TODO per project, has only a single repo attached
def create_cluster_config(cluster, project_name, github_username, github_repository):
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    if not os.path.exists(cluster_storage_dir):
        return "Can't find Scratch/ directory", 400

    job_metadata = os.path.join(cluster_storage_dir, 'job_metadata')
    if not os.path.exists(job_metadata):
        os.mkdir('job_metadata')

    project_path = os.path.join(job_metadata, project_name)
    if os.path.exists(project_path):
        return f"Project {project_name} already exists", 400
    else:
        os.mkdir(project_path)
        metadata_path = os.path.join(project_path, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(dict(
                github_username=github_username,
                github_repository=github_repository
            ), f)
        return f"Project {project_name} created.", 200

def run_gpu_job(cluster, project_name, job_name, walltime, storage_mem, script_template_name, env_vars):
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    project_path = os.path.join(cluster_storage_dir, project_name)
    if not os.path.exists(project_path):
        return f"Can't find project {project_name}. Create it using the /create endpoint first", 400

    job_path = os.path.join(project_path, job_name)
    if os.path.exists(job_path):
        return f"Job {job_name} already exists", 400
    else:
        os.mkdir(job_path)

    venv_path = os.path.join(job_path, 'venv')

    # TODO create venv

    # TODO save job metadata

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

    # run job # TODO do this properly
    os.system(
        f'qsub Scratch/job_scripts/job_script.sh'
    )
    return 'f', 200


def gpu_myriad(project_name, walltime, storage_mem, script_template_name, env_vars, job_name):

    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']

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

    # run job # TODO do this properly
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