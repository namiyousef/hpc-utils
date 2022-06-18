from hpcutils.config import SCRIPTS_PATH, TEMPLATES_PATH, CLUSTER_RESOURCE_MAPPING, HELPERS_PATH
import os
import json
import subprocess
import datetime

def health_check():
    return 'OK'

# TODO per project, has only a single repo attached
def create_cluster_config(cluster, project_name, github_username, github_repository):
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    if not os.path.exists(cluster_storage_dir):
        return "Can't find Scratch/ directory", 400

    job_metadata = os.path.join(cluster_storage_dir, 'job_metadata')
    if not os.path.exists(job_metadata):
        os.mkdir(job_metadata)

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

def run_gpu_job(body, cluster, project_name, job_name, script_template_name, env_vars):
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    project_path = os.path.join(cluster_storage_dir, 'job_metadata', project_name)
    if not os.path.exists(project_path):
        return f"Can't find project {project_name}. Create it using the /create endpoint first", 400

    job_path = os.path.join(project_path, job_name)
    job_output_path = os.path.join(job_path, 'job_output')

    if not os.path.exists(job_path):
        os.mkdir(job_path)
        os.mkdir(job_output_path)

    venv_path = os.path.join(project_path, 'venv')
    if not os.path.exists(venv_path):
        return 'venv does not exist', 400

    myriad_template_path = os.path.join(TEMPLATES_PATH, f'{cluster}.sh')
    job_script_template_path = os.path.join(SCRIPTS_PATH, script_template_name)

    try:
        with open(myriad_template_path, 'r') as f:
            myriad_script = f.read()
            myriad_script = myriad_script.format(
                project_name=project_name,
                job_name=job_name,
                script_template_name=script_template_name,
                **body
            )
    except Exception as e:
        return f"Failed to read {myriad_template_path}. Full logs: {e}", 400


    job_script_path = os.path.join(job_path, 'job_script.sh')
    if not os.path.exists(job_script_path):
        try:
            with open(job_script_path, 'w') as f:
                f.write(myriad_script)
        except Exception as e:
            return f'Failed to write {job_script_path}. Full logs: {e}', 400

    # build job script
    try:
        with open(job_script_template_path, 'r') as f:
            job_script = f.read()
            job_script = job_script.format(
                **env_vars
            )

            job_script_function = f'run_job_script () {{' \
                                  f'\n\t{job_script}\n' \
                                  f'}}'
    except Exception as e:
        return f"Failed to read {job_script_template_path}. Full logs: {e}", 400

    job_script_function_path = os.path.join(job_path, script_template_name)
    if not os.path.exists(job_script_function_path):
        try:
            with open(job_script_function_path, 'w') as f:
                f.write(job_script_function)
        except Exception as e:
            return f"Failed to write {job_script_function_path}. Full logs: {e}", 400


    try:
        output = subprocess.check_output([f'qsub {job_script_path}'], shell=True) # TODO not recommended
        print(output)
    except Exception as e:
        return f"Failed to submit job. Full logs: {e}", 400

    split_output = output.split()
    job_id = split_output[2]
    print(split_output)
    print(job_id)

    timestamp = datetime.datetime.now()
    metadata_dict = dict(
        job_date=timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
        script_template_name=script_template_name,
        env_vars=env_vars,
        job_metadata=body
    )
    job_map_path = os.path.join(job_path, 'metadata.json')
    if os.path.exists(job_map_path):
        with open(job_map_path, 'r') as f:
            metadata_history = json.load(f)
    else:
        metadata_history = {}


    with open(job_map_path, 'w') as f:
        metadata_history[job_id] = metadata_dict
        json.dump(metadata_history, f)


    # TODO need to save some metadata for the get endpoints, e.g. checking the version of the venv

    return 'Successfully submitted job', 200