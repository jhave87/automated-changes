import time
import queue
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class Watcher():

    def __init__(self, path, event_queue, 
                 match_patterns=None, ignore_dir=True):
        self.observer = Observer()
        self.dir_to_watch = path
        self.queue = event_queue
        self.patterns = match_patterns
        self.ignore_dir = ignore_dir

    def run(self):
        event_handler = QueueHandler(self.queue,
                                     patterns=self.patterns,
                                     ignore_dir=self.ignore_dir)

        self.observer.schedule(event_handler,
                               self.dir_to_watch,
                               recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print("Watchdog has been stopped")

        self.observer.join()


class QueueHandler(PatternMatchingEventHandler):

    def __init__(self, queue, patterns=None, ignore_dir=True):
        PatternMatchingEventHandler.__init__(self, patterns=patterns,
                                             ignore_directories=ignore_dir)
        self.queue = queue

    def add_to_queue(self, event):
        self.queue.put(event)

    def on_created(self, event):
        if event.is_directory:
            return None
        else:
            self.add_to_queue(event)


def process_events_queue(queue):
    while True:
        if not queue.empty():
            event = queue.get()

            logging.basicConfig(filename='process_events_queue.log', level=logging.INFO,
                                format='%(levelname)s: %(asctime)s - %(message)s',
                                datefmt='%Y/%m/%d %H:%M:%S')

            logging.info("Started processing {0}\n".format(event.src_path))
            # CALL something that handles the file

            # log the operation has been completed successfully
            logging.info("Finished processing {0}\n".format(event.src_path))

        else:
            time.sleep(1)


if __name__ == '__main__':

    event_queue = queue.Queue()

    # Set up a worker thread to process database load
    worker = threading.Thread(target=process_events_queue, args=(event_queue,))
    worker.setDaemon(True)
    worker.start()

    path = "C:\\Users\\B050080\\Documents\\Python Scripts"
    patterns = ["*.xml"]

    w = Watcher(path, event_queue, match_patterns=patterns)
    w.run()
