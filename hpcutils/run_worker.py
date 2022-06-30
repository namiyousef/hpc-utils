from hpcutils.worker.worker import Worker
from hpcutils.config import CLUSTER
def main():
    Worker(CLUSTER).run()

if __name__ == '__main__':
    Worker(CLUSTER).run()