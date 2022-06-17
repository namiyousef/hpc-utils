from hpcutils.config import SCRIPTS_PATH, TEMPLATES_PATH, CLUSTER_RESOURCE_MAPPING, HELPERS_PATH
import os
import json
import subprocess

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
    if os.path.exists(job_path):
        return f"Job {job_name} already exists", 400

    os.mkdir(job_path)
    job_output_path = os.path.join(job_path, 'job_output')
    os.mkdir(job_output_path)

    metadata_path = os.path.join(project_path, 'metadata.json')
    try:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        github_username = metadata['github_username']
        github_repository = metadata['github_repository']
    except Exception as e:
        return f'Failed to retrieve GitHub username and password. Metadata.json not configured properly or does not exist', 400

    venv_path = os.path.join(job_path, 'venv')
    try:
        helper_path = os.path.join(HELPERS_PATH, f'{cluster}.sh')
        helper_path = os.path.join(HELPERS_PATH, f'{cluster}.sh')
        process = subprocess.Popen([f'source {helper_path}', f'prepare_virtualenv {venv_path} {github_username} {github_repository}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout)
        print(stderr)
    except subprocess.CalledProcessError as e:
        return f"Failed to source {helper_path}. Full logs: {e.output}", 400

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
    try:
        with open(job_script_function_path, 'w') as f:
            f.write(job_script_function)
    except Exception as e:
        return f"Failed to write {job_script_function_path}. Full logs: {e}", 400


    try:
        output = subprocess.check_output([f'qsub {job_script_path}'])
    except Exception as e:
        return f"Failed to submit job. Full logs: {e}", 400
    return 'Successfully submitted job', 200