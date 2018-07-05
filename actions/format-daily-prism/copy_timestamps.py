#!python
'''
This script copies timestamps (values of the "time" variable) from
on netCDF file to another. It is intended to repair files who've somehow
lost their timestamps. This is a script of last resort: in most cases,
recreating the file and fixing whatever tool chain ate the timestamps
is a *much* better way to go.
'''

import argparse
from netCDF4 import Dataset
import sys
import time

parser = argparse.ArgumentParser(description='Copy timestamps from one netCDF file to another')
parser.add_argument('infile', metavar='infile', help='netCDF source file')
parser.add_argument('outfile', metavar='outfile', help='destination for crs variable')

args = parser.parse_args()

source = Dataset(args.infile, "r", format="NETCDF4")
dest = Dataset(args.outfile, "r+", format="NETCDF4")

if not "time" in source.variables:
    print("Invalid operation: {} does not have a time variable!".format(args.infile))
    source.close()
    dest.close()
    sys.exit()
    
if not "time" in source.variables:
    print("Invalid operation: {} does not have a time variable!".format(args.outfile))
    source.close()
    dest.close()
    sys.exit()
    
source_time = source.variables["time"]
dest_time = dest.variables["time"]    

if not dest_time[:].mask.all():
    print("Invalid operation: {} already has timestamps.".format(args.outfile))
    source.close()
    sys.exit()


if not source_time.shape == dest_time.shape:
    print("Error: Source and destination file have different numbers of timestamps")
    print("{} vs {}".format(source_time.shape, dest_time.shape))
    source.close()
    dest.close()
    sys.exit()

for att in source_time.ncattrs():
    if not att in dest_time.ncattrs() or not source_time[att] == dest_time[att]:
        print("Error: Source and destinate time mismatch on attribute {}".format(att))
        source.close()
        dest.close()
        sys.exit()

dest_time[:] = source_time[:]
print("Timestamps sucessfully copied from {} to {}".format(args.infile, args.outfile))

source.close()
dest.close()