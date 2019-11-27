import queue
import threading
from filehandler import watcher, processing

event_queue = queue.Queue()

# Set up a worker thread to process database load
worker = threading.Thread(target=processing.process_queue, args=(event_queue,))
worker.setDaemon(True)
worker.start()

path = "C:\\Users\\B050080\\Documents\\Python Scripts"
patterns = ["*.xml"]

w = watcher.Watcher()
w.run(path, event_queue, match_patterns=patterns)
