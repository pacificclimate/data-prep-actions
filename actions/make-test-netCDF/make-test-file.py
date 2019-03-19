"""Generate test datafiles.

This script accepts an INPUT FILENAME, an OUTPUT FILENAME,
a VARIABLE NAME, and a NUMBER.

It creates a version of the INPUT at OUTPUT with identical 
data and metadata, except all values associated with VARIABLE 
will be replaced by NUMBER. Masks are left intact.

This file is an aid for situations where you're trying to
figure out what the heck some data transformation is actually
doing."""

from argparse import ArgumentParser
from netCDF4 import Dataset
import numpy as np
import time, shutil

parser = ArgumentParser('Generate a test file with constant data based on an input file')
parser.add_argument('infile', metavar='infile', help='file to base test file on')
parser.add_argument('outfile', metavar='outfile', help='location to create test file')
parser.add_argument('variable', metavar='variable', help='variable to replace')
parser.add_argument('value', metavar='value', help='replace data with this value')

args = parser.parse_args()

#make a copy of the original file
print("Copying file")
shutil.copyfile(args.infile, args.outfile)

with Dataset(args.outfile, "r+") as test:
    print("Setting {} to {}".format(args.variable, args.value))
    test_data = np.full_like(test.variables[args.variable][:], args.value)
    test.variables[args.variable][:] = test_data
    
    print("Updating history")
    entry = "make-test-file {} {} {} {}".format(args.infile.split("/")[-1],
                                                test.filepath().split("/")[-1],
                                                args.variable, args.value)
    test.history = "{}: {} ".format(time.ctime(time.time()), entry) + (test.history if "history" in test.ncattrs() else "")
        
        