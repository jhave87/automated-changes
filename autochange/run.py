import queue
import threading
from . import filehandling


def run(path, patterns):
    '''
    Function that runs two seperate threads. One thread is watching
    a directory and adds file created events to a queue. The other 
    thread checks the queue for new events. If events are in the
    queue the files are processed.

    Args:
        - path (str): String containing the path of the directory
        - patterns (list): Patterns that files should obey

    '''

    # initialize a queue and abort event
    event_queue = queue.Queue()
    abort_event = threading.Event()

    # Set up a worker thread to process database load
    worker = threading.Thread(target=filehandling.process_queue,
                              args=(event_queue, abort_event, path,))
    worker.setDaemon(True)
    worker.start()

    # Start another thread that watches a directory for files
    # matching a pattern
    w = filehandling.Watcher()
    w.run(path, event_queue, abort_event, match_patterns=patterns)
