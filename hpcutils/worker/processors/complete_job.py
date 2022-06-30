import os
import tarfile
import json

# TODO see if you can add logging here!
class CompleteJobProcessor:
    # can you generalise this for non-myriad jobs? ATM only for myriad!!!!
    def __init__(self, message_data):

        self.project_path = message_data['project_path']
        self.filename = message_data['item']
        self.project_name = self.filename.split('.')[0]
        self.job_id = self.filename.split('.')[1]
        self.metadata_path = os.path.join(self.project_path, f'{self.job_id}.json')
        self.job_successful = True # TODO not doing anything at the moment

    def should_process(self):
        project_job_path = os.path.join(self.project_path, f'job_metadata/{self.project_name}/{self.job_id}')
        if not os.path.exists(project_job_path):
            return None
        return self

    def preprocess(self):
        if not os.path.exists(self.metadata_path):
            self.metadata = metadata = {
                'unzipped': False,
                'moved_to_dest': False,
                'cleaned': False,
                'output_moved_to_dest': False,
                'error_moved_to_dest': False
            }
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f)
        else:
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)

        return self


    def process(self):

        # TODO get the project path
        tar_path = os.path.join(self.project_path, self.filename)


        if not self.metadata['unzipped']:
            try:
                # TODO extract all does not delete the tar file, consider adding a process for caching item (e.g. in .cache)
                # TODO also: need to think about the concept of a message queue, right now method is not ideal...
                
                tar = tarfile.open(tar_path, 'r:gz')
                tar.extractall(self.project_path)
                tar.close()
                self.metadata['unzipped'] = True
                with open(self.metadata_path, 'w') as f:
                    json.dump(self.metadata, f)

            except Exception as e:
                raise Exception(f'Failed to extract tarfile: {tar_path}. Reason: {e}')

        # TODO might not have the same file structure!!! (e.g if in beaker)
        job_output_src = os.path.join(
            self.project_path, f'tmpdir/job/{self.job_id}.undefined'
        )
        # TODO how to know if job successful? has to be from errors no?

        # TODO need to also think about caching data (defining a storage for it)
        # TODO this needs thinking: at the moment if the job has already been ingested but the files not deleted
        # then it would cause issues (e.g. if worker failed). it would keep failing at this stage. ALso needs to implement caching
        job_output_dest = os.path.join(self.project_path, f'job_metadata/{self.project_name}/{self.job_id}/job_output')
        if not self.metadata['moved_to_dest']:
            try:
                os.rename(job_output_src, job_output_dest)
                self.metadata['moved_to_dest'] = True
                with open(self.metadata_path, 'w') as f:
                    json.dump(self.metadata, f)
            except Exception as e:
                raise Exception(f'Failed to move job output to {job_output_dest}. Reason: {e}')

        job_logs = [item for item in os.listdir(self.project_path) if item.endswith(self.job_id)]
        for log in job_logs:
            log_file_ext = log.split('.')[-1]
            print(log_file_ext)
            if log_file_ext[0] == 'e':
                log_type = 'error'
            elif log_file_ext[0] == 'o':
                log_type = 'output'

            log_dest = os.path.join(self.project_path, f'job_metadata/{self.project_name}/{self.job_id}/job_output/{log_type}.txt')
            log_src = os.path.join(self.project_path, log)
            if not self.metadata[f'{log_type}_moved_to_dest']:
                try:
                    os.rename(log_src, log_dest)
                    self.metadata[f'{log_type}_moved_to_dest'] = True
                    with open(self.metadata_path, 'w') as f:
                        json.dump(self.metadata, f)
                except Exception as e:
                    raise Exception(f'Failed to move log {log_type}. Reason: {e}')

        return self

    def postprocess(self):

        # send an email
        # delete the metadata.json
        os.rmdir(os.path.join(self.project_path, 'tmpdir/job'))
        os.rmdir(os.path.join(self.project_path, 'tmpdir'))
        os.remove(os.path.join(self.project_path, f'{self.job_id}.json'))

        # cleans up the file
        return self