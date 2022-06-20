from hpcutils.worker.processors.complete_job import CompleteJobProcessor
import logging
import os
import datetime
import time

import logging

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
date_format = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s', datefmt=date_format)

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class MyriadJobCompletionEventWorker:
    # TODO this needs to be very robust... don't want to delete files by mistake!

    IGNORE_FILES = set()
    MESSAGES = {}

    def __init__(self):
        self.directory_to_monitor = 'Scratch'
        self.message = {}
        # initialize? e.g. if the directory does not exist?
        # logging?


        # TODO think about how to do files that maybe have not finished completing just yet (e.g.in terms of copying)

    def get_message(self):
        if not self.message or self.message['message_acknowledged']:
            for item in os.listdir(self.directory_to_monitor):
                if item not in self.IGNORE_FILES:
                    item_path = os.path.join(self.directory_to_monitor, item)
                    modification_time_kernel = os.path.getmtime(item_path)
                    modification_time_str = time.strftime(date_format, time.localtime(modification_time_kernel))
                    message = {
                        'last_modified': modification_time_str,
                        'data': {
                            'item': item,
                            'is_dir': os.path.isdir(item_path)
                        },
                        'message_acknowledged': False
                    }

                    split_message = item.split('.')
                    print(split_message)
                    if len(split_message) == 4 and split_message[1].isdigit() and split_message[2] == 'tar' and \
                            split_message[3] == 'gz':
                        message['data']['processor'] = 'complete_job_processor'
                        message['data']['project_path'] = os.path.join(self.directory_to_monitor)

                    self.message = message
                    logger.info(f'Received message: {self.message}')
                    return self.message

            self.message = {}

        return self.message



class Worker(MyriadJobCompletionEventWorker):
    PROCESSOR_MAPPING = {
        'complete_job_processor': CompleteJobProcessor
    }

    def __init__(self):
        super().__init__()

    def get_processors(self):
        message = self.get_message()
        message_data = message.get('data', {})
        requested_processor = message_data.get('processor', None)
        requested_processor = self.PROCESSOR_MAPPING.get(requested_processor, None)
        return requested_processor

    def run(self):
        while True:
            processor = self.get_processors()
            if not processor:
                if self.message:
                    self.message['message_acknowledged'] = True
                    item = self.message['data']['item']
                    self.IGNORE_FILES.add(item)
                    logger.info(f'No processor attached to message: {self.message}')
                else:
                    logger.info('No new messages')
            else:
                processor = processor(self.message['data'])
                try:
                    if processor.should_process():
                        processor = processor.preprocess()
                        processor = processor.process()
                        processor = processor.postprocess()
                        self.message['message_acknowledged'] = True
                        item = self.message['data']['item']
                        self.IGNORE_FILES.add(item)
                        logger.info(f'Processed message: {self.message}')
                    else:
                        logging.info(f'Nothing to do to message: {self.message}')
                except Exception as e:
                    logging.error(f'Failed to process message: {self.message}. Reason: {e}')


            time.sleep(2)
