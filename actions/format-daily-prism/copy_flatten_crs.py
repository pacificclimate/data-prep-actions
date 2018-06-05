#!python

'''This script copies a crs variable from one netCDF file to a second file, 
removing the associated dimension.

Rationale: the CF Standards support declaring a CRS file whose attributes 
encode all relevant CRS information. While the standards do not explicitly
state this variable should be dimensionless, it is in all the examples.
However, some PCIC tools generate netCDF files with CRS as a variable that
has no data, but does have an associated time dimension.

(This may be CDO's fault, I've definitely seen it act hinky around 
dimensionless variables, but I don't actually know what tool chain
produced these files.)

A crs with a time time dimension is undesirable, because we neither want CRS
to be subject to the metadata reqs modelmeta enforces on dimensioned variables 
(like having to have units) nor would we want crs listed in the database to view
on a map or graph in PDP or climate explorer. So we need a dimensionless
version of crs.

NetCDF is deliberately designed to not support removing a dimension from a 
variable, so fixing this is a little roundabout.

(Unidata says:
"Attributes are more dynamic than variables or dimensions; they can be deleted 
and have their type, length, and values changed after they are created, whereas 
the netCDF interface provides no way to delete a variable or to change its type 
or shape.")

Step 1: Use nccopy to make a new netCDF file with every variable except crs
> nccopy -V time,lat,lon,pr file1.nc file2.nc

Step 2: Use this script to transfer all the crs attributes to the new file
> python copy_flatten_crs.py file1.nc file2.nc

Step 3: replace the original file with the new version
> rm file1.nc
> mv file2.nc file1.nc
'''

import argparse
from netCDF4 import Dataset
import sys
import numpy as np

parser = argparse.ArgumentParser(description='Encapsulate CRS variable in a new file')
parser.add_argument('infile', metavar='infile', help='netCDF source file')
parser.add_argument('outfile', metavar='outfile', help='destination for crs variable')

args = parser.parse_args()

source = Dataset(args.infile, "r", format="NETCDF4")

if not "crs" in source.variables:
    print("Invalid operation: {} does not have a crs variable!".format(args.infile))
    source.close()
    sys.exit()

if not source.variables["crs"][:].mask.all():
    print("Invalid operation: crs variable in {} is not empty.".format(args.infile))
    source.close()
    sys.exit()

if source.variables["crs"].dimensions == ():
    print("Redundant operation: crs is already a dimensionless variable in {}".format(args.infile))
    source.close()
    sys.exit()

dest = Dataset(args.outfile, "r+", format="NETCDF4")

if "crs" in dest.variables:
    print("Invalid operation: {} already has a crs variable!".format(args.outfile))
    source.close()
    dest.close()
    sys.exit()

dest.createVariable("crs", "i4", ())
dest.variables["crs"].setncatts(source.variables["crs"].__dict__)

dest.close()
source.close()