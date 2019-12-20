"""
Python script illustrating the use of the autochange package!

"""

# imports
import autochange.run

# initialize variables and functions
path = "C:\\Users\\B050080\\Documents"
patterns = ["*.xml"]


def process_func(file):
    '''
    Function that processes files.

    Arg:
        file (str): Path to file.

    '''

    print(file)


# run the autochange package
autochange.run.run(path, patterns, process_func)
