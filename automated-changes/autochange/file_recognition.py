import time
import queue
import threading
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class Watcher():
    '''
    The watcher object is used to observe changes in a given
    folder

    Attributes:
        observer: Observer object used for event handling

    '''
    def __init__(self):
        self.observer = Observer()

    def run(self, dir_to_watch, event_queue, 
            match_patterns=None, ignore_dir=True):
        '''
        The run method starts an observation of a given directory.
        Events will be handled by the QueueHandler class.

        Args:
            dir_to_watch (str): Path to dir that should be observed
            event_queue: Queue object to place file event objects
            match_patterns (list): Patterns for filenames
            ignore_dir (bool): Ignore directories

        '''
        event_handler = QueueHandler(event_queue,
                                     patterns=match_patterns,
                                     ignore_dir=ignore_dir)

        self.observer.schedule(event_handler,
                               dir_to_watch,
                               recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print(f"Observation of {dir_to_watch} has been stopped")

        self.observer.join()


class QueueHandler(PatternMatchingEventHandler):
    '''
    The QueueHandler object is an implementation of the
    PatternMatchinEventHandler, where the files created that
    match a given pattern are added to a queue object.

    Args:
        queue: Queue object to place file event objects
        patterns (list): Patterns for filenames
        ignore_dir (bool): Ignore directories

    Attributes:
        queue: To store the queue object

    '''
    def __init__(self, queue, patterns, ignore_dir):
        PatternMatchingEventHandler.__init__(self, patterns=patterns,
                                             ignore_directories=ignore_dir)
        self.queue = queue

    def add_to_queue(self, event):
        '''
        The add to queue method adds an event to the queue object.

        Args:
            event: An event object
        '''
        self.queue.put(event)

    def on_created(self, event):
        '''
        The on_created method overwrites the method of the base class.
        If the event is a file creation and matches the patterns, then the
        add to queue method is called.

        Args:
            event: An event object

        '''
        if event.is_directory:
            return None
        else:
            self.add_to_queue(event)


def process_events_queue(queue):
    '''
    The function process_events_queue monitors a queue of file events 
    and processes the events one at a time. The function is meant to be
    run by a Daemon thread, otherwise it will run infinitely.

    Args:
        queue: Queue object containing file events

    '''
    while True:
        if not queue.empty():
            event = queue.get()

            logging.basicConfig(filename='process_events_queue.log',
                                level=logging.INFO,
                                format='%(levelname)s: %(asctime)s - %(message)s',
                                datefmt='%Y/%m/%d %H:%M:%S')

            logging.info(f"Started processing {event.src_path}")
            # CALL something that handles the file

            time.sleep(1)

            # log the operation has been completed successfully
            logging.info(f"Finished processing {event.src_path}")

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

    w = Watcher()
    w.run(path, event_queue, match_patterns=patterns)
