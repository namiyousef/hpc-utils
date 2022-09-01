import os
import hpcutils

DIR_PATH = os.path.dirname(hpcutils.__file__)
TEMPLATES_PATH = os.path.join(DIR_PATH, 'templates')
SCRIPTS_PATH = os.path.join(DIR_PATH, 'scripts')
HELPERS_PATH = os.path.join(DIR_PATH, 'helpers')


CLUSTER_RESOURCE_MAPPING = {
    'myriad': {
        'cluster_storage_dir': 'Scratch',
        'venv': {
            'gpu': {
                'torch': {
                }
            },
        },
        'output_file_pattern': r"(?<!^)(\.o\d+)$",
        'error_file_pattern': r"(?<!^)(\.e\d+)$",
        'data_file_pattern': r"(?<!^)(\.tar\.gz)$",
        'extract_file_pattern': '{job_id}.undefined',
        'extract_path_rootdir': 'tmpdir/job/'
    },
    'beaker': {
        'cluster_storage_dir': 'Scratch',
        'output_file_pattern': r"(?<!^)(\.o\d+)$",
        'error_file_pattern': r"(?<!^)(\.e\d+)$",
        'data_file_pattern': r"(?<!^)(\.tar\.gz)$",
        'extract_file_pattern': '{job_id}.1.gpu.q',
        'extract_file_rootdir': 'tmp'
    }
}

PORT = os.environ.get('PORT', 8080)
CLUSTER = os.environ.get('CLUSTER', None)

EMAIL = os.environ.get('EMAIL', 'nlp.fyp1800@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', None)