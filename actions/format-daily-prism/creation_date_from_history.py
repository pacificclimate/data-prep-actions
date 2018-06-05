#!python

'''
This script attempts to construct a missing 'creation_date' netCDF
global attribute by formatting the most recent datestring it can find
in the history attribute. It's fairly fragile and will only match on 
specific formatting.
'''

import argparse
from netCDF4 import Dataset
import sys
import re
import time

parser = argparse.ArgumentParser(description='Generate a creation_date global attribute from a history attribute')
parser.add_argument('file', metavar='file', help='netCDF file to modify')

args = parser.parse_args()

nc = Dataset(args.file, "r+", format="NETCDF4")

if not "history" in nc.ncattrs():
    print("Invalid operation: {} does not have a history variable!".format(args.file))
    nc.close()
    sys.exit()
    
if "creation_date" in nc.ncattrs():
    print("Invalid operation: {} already has a creation_date attribute!".format(args.file))
    nc.close()
    sys.exit()

#try to find a date in history. History should start with the most recent date.
first_date = re.match(r'(.*:.*:.*):', nc.history)
cdate = time.strptime(first_date.group(1), "%a %b %d %H:%M:%S %Y")
print("Setting creation_date to {}".format(time.strftime("%Y-%m-%d-T%H:%M:%SZ", cdate)))
nc.creation_date = time.strftime("%Y-%m-%d-T%H:%M:%SZ", cdate)
nc.close()