import os
import time
import logging
import xml.etree.ElementTree as ET


def do_something(filename):
    time.sleep(1)
    name_list = filename.split('.')
    new_filename = name_list[0] + '1.' + name_list[1]
    tree = ET.parse(filename)
    tree.write(new_filename)
    #root = tree.getroot()
    #for child in root:
    #    if child.text is not None:
    #        print((child.tag, child.text))


def process_queue(queue, abort_event, log_path):
    '''
    The function process_events_queue monitors a queue of file events
    and processes the events one at a time. The processsed files will
    be moved to a processed file folder in the log_path directory. The
    function is meant to be run by a Daemon thread, otherwise it will
    run infinitely.

    Args:
        queue: Queue object containing file events
        stop_event: Event to stop main thread if processing fails
        log_path: Path to dir where log and processed files are stored

    '''
    # setup loggin configs
    log_name = os.path.join(log_path, 'process_events_queue.log')
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
            do_something(event.src_path)

            # store processed files
            path, fname = os.path.split(event.src_path)
            new_path = os.path.join(log_path, 'processed_files', fname)

            try:
                os.rename(event.src_path, new_path)   
                # log the operation has been completed successfully
                logging.info(f"Finished processing {event.src_path}")
            except FileExistsError:
                logging.error(f"")
                abort_event.set()
                break
