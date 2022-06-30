from hpcutils.config import CLUSTER, CLUSTER_RESOURCE_MAPPING
import re
def _is_job_output_file(filename):
    job_file_pattern = CLUSTER_RESOURCE_MAPPING[CLUSTER]['output_file_pattern']
    pattern = re.compile(job_file_pattern)
    pattern_found = bool(pattern.search(filename))
    return pattern_found

def _is_job_error_file(filename):
    job_file_pattern = CLUSTER_RESOURCE_MAPPING[CLUSTER]['error_file_pattern']
    pattern = re.compile(job_file_pattern)
    pattern_found = bool(pattern.search(filename))
    return pattern_found

def _is_job_output_data(filename):
    job_file_pattern = CLUSTER_RESOURCE_MAPPING[CLUSTER]['data_file_pattern']
    pattern = re.compile(job_file_pattern)
    pattern_found = bool(pattern.search(filename))
    return pattern_found

