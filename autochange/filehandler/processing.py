import time
import logging


def process_queue(queue):
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
