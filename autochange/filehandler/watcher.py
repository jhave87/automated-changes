import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class Watcher():
    '''
    The Watcher object is used to observe changes in a given
    folder

    Attributes:
        observer: Observer object used for event handling

    '''
    def __init__(self):
        self.observer = Observer()

    def run(self, dir_to_watch, event_queue, abort_event,
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

        try:
            while not abort_event.is_set():
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
