''' This script accepts a netCDF file with a frost days (fdETCCDI) variable, and
outputs an identical file, except the variable has been switched to frost free days (ffd).
This is so that frost free days can be mapped in ncWMS - unlike our numerical displays, 
ncWMS can't do the calculation on the fly.'''

from netCDF4 import Dataset
import argparse
import os
import time
import numpy

parser = argparse.ArgumentParser('Create a frost free days dataset from a frost days dataset')
parser.add_argument('indir', help='directory containing input files')
parser.add_argument('outdir', help='directory to output new files to')
args = parser.parse_args()

for file in os.listdir(args.indir):
    try:
        with Dataset("{}/{}".format(args.indir, file), "r") as fdfile:
            print("Now processing {}".format(file))
            if 'fdETCCDI' in fdfile.variables:
                ffd_name = file.replace("fdETCCDI", "ffd")
                ffdfile = Dataset("{}/{}".format(args.outdir, ffd_name), "w")
            
                #copy dimensions
                print("  Now copying dimensions")
                for d in fdfile.dimensions:
                    size = None if fdfile.dimensions[d].isunlimited() else len(fdfile.dimensions[d])
                    ffdfile.createDimension(d, size)
                
                print("  Now copying variables")
                for v in fdfile.variables:
                    if v != "fdETCCDI":
                        ffdfile.createVariable(v, fdfile.variables[v].dtype, fdfile.variables[v].dimensions)
                        ffdfile.variables[v].setncatts(fdfile.variables[v].__dict__)
                        ffdfile.variables[v][:] = fdfile.variables[v][:]
                    else:
                        print("    Generating Frost Free Days")
                        fill = fdfile.variables[v].getncattr("_FillValue")
                        ffdfile.createVariable("ffd", fdfile.variables[v].dtype, fdfile.variables[v].dimensions,
                                           fill_value=fill)
                        ffdfile.variables["ffd"].setncattr("standard_name", "ffd")
                        ffdfile.variables["ffd"].setncattr("long_name", "Frost Free Days")
                        ffdfile.variables["ffd"].setncattr("units", "days")
                        ffdfile.variables["ffd"].setncattr("cell_methods", "time: sum within years time: mean over years")
                        ffdfile.variables["ffd"][:] = (fdfile.variables[v][:] * -1) + 365
            
                print("  Now copying global attributes")
                ffdfile.setncatts(fdfile.__dict__)
                print("  Now updating history")
                entry = "{}: frost_free_days {}".format(time.ctime(time.time()), file)
                ffdfile.history = "{} ".format(entry) + (ffdfile.history if "history" in ffdfile.ncattrs() else "")         
        
            else:
                print("{} is not a frost day datafile")
        
    except Exception as e:
        raise e
        print(e)
        print("{} is not a netCDF file".format(file))