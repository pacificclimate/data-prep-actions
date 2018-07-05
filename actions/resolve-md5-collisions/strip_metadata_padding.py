#! python
'''This script copies all dimensions, variables, and attributes from a netCDF
file into a new file. It differs from nccopy or plain old unix cp by NOT copying
allocated but unused metadata space, so it can be used to produce files without
metadata expansion space if further metadata changes are not anticipated.'''

import argparse
import os.path
import sys
import time
from pathlib import Path
from netCDF4 import Dataset

parser = argparse.ArgumentParser(description='Create a copy of a netCDF file, stripping unused metadata space')
parser.add_argument('source_file', metavar='source', help='source netCDF file')
parser.add_argument('dest_dir', metavar='copydir', help='destination directory')

args = parser.parse_args()

#Make sure we won't be overwriting the destination.
if not Path(args.dest_dir).is_dir():
    print("ERROR: {} is not a directory".format(args.dest_dir))
    sys.exit()
    
dest = args.dest_dir + '/' + args.source_file.split('/')[-1]

if Path(dest).is_file():
    print("ERROR: {} already exists".format(dest))
    sys.exit()

source = Dataset(args.source_file, "r")
dest = Dataset(dest, "w")

#dimensions
for dim in source.dimensions:
    print("Now copying dimension {}".format(dim))
    size = None if source.dimensions[dim].isunlimited() else len(source.dimensions[dim])
    dest.createDimension(dim, size)

#variables
for var in source.variables:
    print("Now copying variable {}".format(var))
    dest.createVariable(var, source.variables[var].dtype, source.variables[var].dimensions)
    dest.variables[var].setncatts(source.variables[var].__dict__)
    dest.variables[var][:] = source.variables[var][:]

#global attributes
print("Now copying global attributes")
dest.setncatts(source.__dict__)

print("Now updating history")
text = "strip_metadata_padding.py {}".format(source.filepath())
dest.history = "{}: {}\n".format(time.ctime(time.time()), text) + (dest.history if "history" in dest.ncattrs() else "")

source.close()
dest.close()