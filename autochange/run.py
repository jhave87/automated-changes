import queue
import sys
import threading
from . import filehandling


def setup_thread_excepthook():
    """
    Workaround for `sys.excepthook` thread bug from:
    http://bugs.python.org/issue1230540

    Call once from the main thread before creating any threads.

    """

    init_original = threading.Thread.__init__

    def init(self, *args, **kwargs):

        init_original(self, *args, **kwargs)
        run_original = self.run

        def run_with_except_hook(*args2, **kwargs2):
            try:
                run_original(*args2, **kwargs2)
            except Exception:
                sys.excepthook(*sys.exc_info())

        self.run = run_with_except_hook

    threading.Thread.__init__ = init


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

    # setup threads exception hook
    setup_thread_excepthook()

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
