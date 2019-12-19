import queue
import threading
from autochange import watcher, processing

event_queue = queue.Queue()
abort_event = threading.Event()
path = "C:\\Users\\B050080\\Documents\\Code\\Python"
patterns = ["*.xml"]

# Set up a worker thread to process database load
worker = threading.Thread(target=processing.process_queue,
                          args=(event_queue, abort_event, path,))
worker.setDaemon(True)
worker.start()

w = watcher.Watcher()
w.run(path, event_queue, abort_event, match_patterns=patterns)
