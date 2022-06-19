# hpc-utils
A repository that contains helper function for using queue based cluster compute systems


# Deploying on Cluster (Development)

## Set Up App
1. First ssh into the desired cluster (see #3 and #4).
2. Clone the latest version of hpc-utils
3. Create a new venv and run `pip install -e .` from the hpc-utils directory
4. You should now be able to run the api and worker using `hpcutils-api` and `hpcutils-worker` respectively

## Sert Up Environment for Jobs
1. From the app, create a project
2. From the terminal, run `source hpc-utils/hpcutils/helpers/{cluster}.sh`
4. Create the virtual environment associated with your project using `prepare_virtual_env {venv_path} {github_user} {github_repo}` (alternatively if your project does not use a `setup.py` you can create your environment manually, but first make sure to run `get_gpu_modules`)
5. Move venv to project location, `cp -r {venv_path} {cluster_dir}/job_metadata/{project_name}/venv`
6. Now you should be able to run jobs fine and dandy

# Deploying on Cluster (Production)
nohup (to be updated)