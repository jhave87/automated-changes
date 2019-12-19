import os
import time
import logging
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler


def process_queue(process_func, queue, abort_event, log_path):
    '''
    The function process_events_queue monitors a queue of file events
    and processes the events one at a time. The processsed files will
    be moved to a processed file folder in the log_path directory. The
    function is meant to be run by a Daemon thread, otherwise it will
    run infinitely.

    Args:
        process_func: Function expression. Should handle a single input file.
        queue: Queue object containing file events
        stop_event: Event to stop main thread if processing fails
        log_path: Path to dir where log and processed files are stored

    '''
    # setup loggin configs
    log_name = os.path.join(log_path, 'processed_files.log')
    logging.basicConfig(filename=log_name,
                        level=logging.INFO,
                        format='%(levelname)s: %(asctime)s - %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')

    # check if processed_files folder exists, otherwise create it
    if not os.path.exists(os.path.join(log_path, 'processed_files')):
        os.mkdir(os.path.join(log_path, 'processed_files'))

    while True:
        if not queue.empty():
            event = queue.get()
            logging.info(f"Started processing {event.src_path}")

            # call something that handles the file
            process_func(event.src_path)

            # store processed files
            path, fname = os.path.split(event.src_path)
            new_path = os.path.join(log_path, 'processed_files', fname)

            try:
                os.rename(event.src_path, new_path)
                # log the operation has been completed successfully
                logging.info(f"Finished processing {event.src_path}")
            except FileExistsError:
                logging.error(f"File {new_path} already exists ")
                abort_event.set()
                break


class Watcher():
    '''
    The Watcher object is used to observe changes in a given
    folder

    Attributes:
        observer: Observer object used for event handling
        with_warning (bool): If true warnings will be send

    '''
    def __init__(self):
        self.observer = PollingObserver()

    def run(self, dir_to_watch, event_queue, stop_event,
            match_patterns=None, ignore_dir=True):
        '''
        The run method starts an observation of a given directory.
        Events will be handled by the QueueHandler class.

        Args:
            dir_to_watch (str): Path to dir that should be observed
            event_queue: Queue object to place file event objects
            abort_event: An thread event used to abort if other threads fail
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
        print(f"Observation of {dir_to_watch} has started")

        try:
            while not stop_event.is_set():
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
            print(f"Observation of {dir_to_watch} has been stopped")

        print("The program is aborting")
        self.observer.stop()
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
