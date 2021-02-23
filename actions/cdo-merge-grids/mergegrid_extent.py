'''This script is a helper for CDO's mergegrid.
CDO's mergegrid combines data from two files with different
spatial coverage, but it doesn't change the spatial extent 
of the files. That is, if you do:

cdo mergegrid a.nc b.nc c.nc

The output in c.nc has the same spatial extent as a.nc, with a
combination of data from a.nc and b.nc

This script creates a blank file whose spatial extent covers
both input files to be used as an input to cdo mergegrid.

python mergegrid_extent.py a.nc b.nc elevation temp1.nc

gives you a temp1.nc with spatial extent covering both a.nc and
b.nc, and a.nc's metadata, and a blank elevation variable. Then you can
use cdo mergegrid:

cdo mergegrid temp1.nc a.nc temp2.nc
cdo mergegrid temp2.nc b.nc final.nc

To finally get what you wanted all along: a file combining
the elevation data and extents of a.nc and b.nc.

Not tested on data with a time dimension, would need additional
modification in that case. Works on only one variable at a time
but could be modified easily enough.
'''

from netCDF4 import Dataset
import argparse, time
import numpy as np
import numpy.ma as ma

parser = argparse.ArgumentParser(description='Create a blank netCDF file that matches the spatial extent of inputs')
parser.add_argument('file1', metavar='file1', help='main dataset - metadata will be used')
parser.add_argument('file2', metavar='file2', help='additional dataset')
parser.add_argument('outfile', metavar='outfile', help='file to write output to')
parser.add_argument('variable', metavar='variable', help='variable to use')

args = parser.parse_args()

file1 = Dataset(args.file1)
file2 = Dataset(args.file2)
var = args.variable

try:
    print("Checking variables")
    for f in [file1, file2]:
        if var not in f.variables:
            raise Exception("{} does not have a {} variable".format(f.filepath(), var))
    
    print("Checking grids")
    def regular_grid(grid, step):
        for i in range(0, len(grid)):
            if grid[i] != grid[0] + i * step:
                return False
        return True
    
    lons1 = file1.variables["lon"][:]
    lons2 = file2.variables["lon"][:]
    lonstep = lons1[1] - lons1[0]
    if not regular_grid(lons1, lonstep):
        raise Exception("{} does not have a regular longitude grid".format(file1.filename))
    if not regular_grid(lons2, lonstep):
        raise Exception("{} does not have a regular longitude grid".format(file2.filename))
    
    lats1 = file1.variables["lat"][:]
    lats2 = file2.variables["lat"][:]
    latstep = lats1[1] - lats1[0]
    if not regular_grid(lats1, latstep):
        raise Exception("{} does not have a regular latitude grid".format(file1.filename))
    if not regular_grid(lats2, latstep):
        raise Exception("{} does not have a regular latitude grid".format(file2.filename))
            
    #build the combined grid
    lons = np.sort(np.union1d(lons1, lons2))
    if not regular_grid(lons, lonstep):
        raise Exception("These files' longitudes are not compatible".format(lons))
        
    lats = np.sort(np.union1d(lats1, lats2))
    if not regular_grid(lats, latstep):
        raise Exception("These files' latitudes are not compatible: {}".format(lats))

    print("Creating output file")
    outfile = Dataset(args.outfile, "w")
    
    print("Writing dimensions")
    outfile.createDimension("lon", len(lons))
    outfile.createDimension("lat", len(lats))
    
    print("Writing latitude and longitude")
    outfile.createVariable("lon", "f8", ["lon"])
    outfile.variables["lon"][:] = lons
    outfile.variables["lon"].setncatts(file1.variables["lon"].__dict__)
    outfile.createVariable("lat", "f8", ["lat"])
    outfile.variables["lat"][:] = lats
    outfile.variables["lat"].setncatts(file1.variables["lat"].__dict__)
    
    print("Writing blank variable {}".format(var))
    outfile.createVariable(var, "f8", ["lat", "lon"])
    outfile.variables[var].setncatts(file1.variables[var].__dict__)
    
    print("Copying global metadata attributes and updating history")
    outfile.setncatts(file1.__dict__)
    entry = "mergegrid_extent {} {} {} ".format(args.file1, args.file2, args.outfile)
    outfile.history = "{}: {} ".format(time.ctime(time.time()), entry) + (outfile.history if "history" in outfile.ncattrs() else "")

except Exception as err:
    print(err)
finally:
    file1.close()
    file2.close()
    outfile.close()