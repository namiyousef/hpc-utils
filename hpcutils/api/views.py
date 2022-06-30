from hpcutils.config import SCRIPTS_PATH, TEMPLATES_PATH, CLUSTER_RESOURCE_MAPPING, HELPERS_PATH
import os
import json
import subprocess
import datetime
import logging
import shutil

def health_check():
    return 'OK'

def get_resource_metadata(cluster, project_name, job_id):
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    resource_path = os.path.join(cluster_storage_dir, 'job_metadata', project_name)
    if job_id:
        resource_path = os.path.join(resource_path, job_id)

    if not os.path.exists(resource_path):
        return f"Resource at: {resource_path} does not exist", 400

    metadata_path = os.path.join(resource_path, 'metadata.json')
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    return metadata, 200

def get_project_jobs(cluster, project_name):
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    project_name = os.path.join(cluster_storage_dir, 'job_metadata', project_name)
    if not os.path.exists(project_name):
        return f"Project at: {project_name} does not exist", 400

    metadata = {}
    for job_id in os.listdir(project_name):
        job_dir = os.path.join(project_name, job_id)
        if os.path.isdir(job_dir):
            metadata_path = os.path.join(job_dir, 'metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata[job_id] = json.load(f)
            else:
                logging.error(f'Path {job_id} does not have a metadata.json file')
        else:
            logging.info(f'Path {job_id} is not a directory')

    return metadata, 200



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

    job_path = os.path.join(project_path, 'tmp_job_dir')
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
    # LOGIC: re-write any temporary files
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


    # TODO needs very good testing this point onwards...
    try:
        output = subprocess.check_output([f'qsub {job_script_path}'], shell=True) # TODO not recommended
    except Exception as e:
        return f"Failed to submit job. Full logs: {e}", 400

    output = output.decode('utf-8')
    split_output = output.split()
    job_id = split_output[2]

    timestamp = datetime.datetime.now()
    metadata_dict = dict(
        job_date=timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
        script_template_name=script_template_name,
        env_vars=env_vars,
        job_metadata=body,
        job_id=job_id
    )

    job_map_path = os.path.join(job_path, 'metadata.json')

    logging.info('Updating job metadata')
    with open(job_map_path, 'w') as f:
        json.dump(metadata_dict, f)

    job_dir = os.path.join(project_path, job_id)
    os.rename(job_path, job_dir)


    return f'Successfully submitted job {job_id}', 200


def delete_job(cluster, project_name, job_id):
    # TODO danger with delete: you might delete something that does not have the files downloaded yet!
    # TODO need to know if job complete, can probably use the qstat command!
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    job_metadata_path = os.path.join(cluster_storage_dir, f'job_metadata/{project_name}/{job_id}')
    job_output_dir = os.path.join(job_metadata_path, 'job_output')
    scratch_files = os.listdir(cluster_storage_dir)
    output_scratch_file = [scratch_file for scratch_file in scratch_files if scratch_file.endswith(f'.o{job_id}')]
    if output_scratch_file:
        output_scratch_file = output_scratch_file[0]
        output_scratch_file_path = os.path.join(cluster_storage_dir, output_scratch_file)
        if os.path.exists(output_scratch_file_path):
            with open(output_scratch_file_path, 'r') as f:
                scratch_file_text = f.read()
                print(scratch_file_text)
            if not scratch_file_text:
                return f'Output scratch file: {output_scratch_file_path} is empty, job may not be complete yet. Deleting blocked so as not to lose any data', 400


    if any(job_id in scratch_file for scratch_file in scratch_files if scratch_file.endswith('.tar.gz') or scratch_file.endswith('.tar')):
        return f"There exists at least one job output .tar or .tar.gz file associated with job {job_id}. Deleting blocked so as not to lose any data", 400


    if any(os.scandir(job_output_dir)):
        return f"Job output directory is not empty for job {job_id}. Deleting blocked so as not to lose any data", 400


    # remove any files in scratch
    for scratch_file in scratch_files:
        if job_id in scratch_file:
            if scratch_file.endswith(f'.o{job_id}') or scratch_file.endswith(f'.e{job_id}'):
                scratch_file_path = os.path.join(cluster_storage_dir, scratch_file)
                os.remove(scratch_file_path)


    # remove any directory associated with the project\
    if os.path.exists(job_metadata_path):
        shutil.rmtree(job_metadata_path)

    return f"Successfully deleted items associated with job: {job_id}", 200


def get_logs(cluster, project_name, job_id, log_type):
    cluster_storage_dir = CLUSTER_RESOURCE_MAPPING[cluster]['cluster_storage_dir']
    log_path = os.path.join(cluster_storage_dir, f'job_metadata/{project_name}/{job_id}/job_output/{log_type}.txt')
    if not os.path.exists(log_path):
        return "Log does not exist", 400
    else:
        with open(log_path, 'r') as f:
            log_text = f.read()
        return log_text, 200


def create_venv(cluster, project_name):
    return 'Not implemented yet', 400


def delete_venv(cluster, project_name):
    return 'Not implemented yet', 400
