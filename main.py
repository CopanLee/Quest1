import configparser
import pathlib
import queue
import random
import time
from threading import Thread, Lock

GENERAL_CONFIG = {
    'queue_size': 10,
    'producer_num': 1,
    'consumer_num': 1,
    'produce_speed': 0.1,
    'consume_speed': 0.15,
}

class Simulates():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self._init_config()

        self.lock = Lock()
        self.running = False
        self.job_queue = queue.Queue(maxsize=int(self.config['General']['queue_size']))
        self.producer_threads = []
        self.consumer_threads = []

    def _init_config(self):
        if not pathlib.Path('config.ini').exists():
            self.config['General'] = GENERAL_CONFIG
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
        else:
            self.config.read('config.ini')

    def _get_from_queue(self):
        try:
            return self.job_queue.get_nowait()
        except queue.Empty:
            return None

    def _put_to_queue(self, job: int):
        try:
            # if queue is full, directly discard the job
            # without considering the issue of the queue being full and unable to accommodate it
            self.job_queue.put_nowait(job)
            return True
        except queue.Full:
            return False

    def _producer(self, producer_id: int):
        while self.running:
            with self.lock:
                job = random.randint(1, 100)
                if self._put_to_queue(job):
                    print(f'[producer-{producer_id}] produce a job: {job}')
                else:
                    print(f'[producer-{producer_id}] queue is full, can not produce job')
            time.sleep(float(self.config['General']['produce_speed']))
    
    def _consumer(self, consumer_id: int):
        while self.running:
            with self.lock:
                job = self._get_from_queue()
                if job:
                    print(f'[consumer-{consumer_id}] consume a job: {job}')
                else:
                    print(f'[consumer-{consumer_id}] No job in queue')
            time.sleep(float(self.config['General']['consume_speed']))

    def start(self):
        print('Simulate start')
        self.running = True
        for i in range(int(self.config['General']['producer_num'])):
            _producer = Thread(target=self._producer, args=(i,))
            _producer.start()
            self.producer_threads.append(_producer)
        for i in range(int(self.config['General']['consumer_num'])):
            _consumer = Thread(target=self._consumer, args=(i,))
            _consumer.start()
            self.consumer_threads.append(_consumer)

    def stop(self):
        self.running = False
        for producer in self.producer_threads:
            producer.join()
        for consumer in self.consumer_threads:
            consumer.join()

    
if __name__ == '__main__':
    simulate = Simulates()
    simulate.start()
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        simulate.stop()
        print('User stop the program')
    