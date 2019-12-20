import queue
import threading
from . import filehandling


def run(path, patterns, process_func):
    '''
    Function that runs two seperate threads. One thread is watching
    a directory and adds file created events to a queue. The other
    thread checks the queue for new events. If events are in the
    queue the files are processed according to the process_func
    function.

    Args:
        path (str): String containing the path of the directory
        patterns (list): Patterns that files should obey to be processed
        process_func: Function expression. Should take a single input file
    '''

    # initialize a queue and abort event
    event_queue = queue.Queue()
    abort_event = threading.Event()

    try:
        # start a daemon thread to process files
        worker = threading.Thread(target=filehandling.process_queue,
                                  args=(process_func, event_queue,
                                        abort_event, path,))
        worker.setDaemon(True)
        worker.start()

        # start another thread that watches a directory for files
        # matching a pattern
        w = filehandling.Watcher()
        w.run(path, event_queue, abort_event, match_patterns=patterns)

    except FileNotFoundError:
        print("The path supplied does not point to a valid directory")

    except TypeError:
        print("The process function supplied is not valid. "
              "Only functions taking a single input can be used.")
