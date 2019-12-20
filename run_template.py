"""
Python script illustrating the use of the autochange package!

"""

# imports
import autochange.run

# initialize variables
path = "C:\\Users\\B050080\\Documents"
patterns = ["*.xml"]


# setup file processsing
process_func = 1


autochange.run.run(path, patterns, process_func)
