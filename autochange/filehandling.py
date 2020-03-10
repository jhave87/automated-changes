import os
import sys
import time
import logging
from datetime import datetime
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler


def logSetup(file_name):
    """
    Function for setting up a new log to track the case creation process
    and for logging unhandled exceptions.

    Args:
    file_name (str): Filename and path to the log file

    Returns:
    logger: Custom logger to track progress

    """
    # Create a custom logger
    logger = logging.getLogger(__name__)

    # Setup file handler
    f_handler = logging.FileHandler(file_name)
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s',
                                 '%Y/%m/%d %H:%M:%S')
    f_handler.setFormatter(f_format)

    # Setup custom handler
    c_handler = logging.StreamHandler(stream=sys.stdout)
    c_format = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s',
                                 '%Y/%m/%d %H:%M:%S')
    c_handler.setFormatter(c_format)

    # Define function to log uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error("Uncaught exception",
                     exc_info=(exc_type, exc_value, exc_traceback))
    # Add hook to use the handle exception function when uncaught
    # exceptions happen
    sys.excepthook = handle_exception

    # Add handlers to the logger and return the logger
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)
    return logger


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
    # check if processed_files folder exists, otherwise create it
    if not os.path.exists(os.path.join(log_path, 'processed_files')):
        os.mkdir(os.path.join(log_path, 'processed_files'))
    if not os.path.exists(os.path.join(log_path, 'failed_files')):
        os.mkdir(os.path.join(log_path, 'failed_files'))
    if not os.path.exists(os.path.join(log_path, 'logs')):
        os.mkdir(os.path.join(log_path, 'logs'))

    # setup loggin configs
    dtm = datetime.now().strftime("%m%d%YT%H%M%S")
    log_name = os.path.join(log_path, 'logs', f"processed_files_{dtm}.log")
    logger = logSetup(log_name)

    while True:
        if not queue.empty():
            event = queue.get()
            logger.info(f"Started processing {event.src_path}")

            # call something that handles the file
            success = process_func(event.src_path)

            # store processed files
            path, fname = os.path.split(event.src_path)
            if success:
                new_path = os.path.join(log_path, 'processed_files', fname)
            else:
                new_path = os.path.join(log_path, 'failed_files', fname)

            try:
                os.rename(event.src_path, new_path)
                # log the operation has been completed successfully
                if success:
                    logger.info(f"Finished processing {event.src_path}")
                else:
                    logger.info(f"Failed processing {event.src_path}")
            except FileExistsError:
                logger.error(f"File {new_path} already exists ")
                abort_event.set()
                break
            queue.task_done()
        else:
            time.sleep(1)


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
