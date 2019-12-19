# Autochange
A small Python package used to monitor a directory in the file system for files matching a given pattern.
When new files are created in the directory, a file event is added to an event queue. The files in the queue
can then be processed according to what is needed.

## Installation
The package is currently not in pypi, but can be installed by running `pip install git+https://github.com/jhave87/automated-changes.git`, or by cloning the repository and running `pip install .` in the base directory.

## Using Autochange
A typical use example is included in the `use_template.py`.