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
            }
        },
    }
}