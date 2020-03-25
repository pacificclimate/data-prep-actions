'''Accepts a JSON metadata file (as created by the multimeta endpoint) and uses the attributes
of each dataset to find pairs of matching tasmax / tasmin datasets. Generates a tasmean
dataset for each pair, where the values at each location and timestamp are the mean of the
tasmin and tasmax values. 

Copies all metadata from the parent tasmax file. Adds new metadata to the variable.'''

import json
import argparse
import csv
import numpy as np
from netCDF4 import Dataset
import time

parser=argparse.ArgumentParser("Create tasmean files from a list of metadata")
parser.add_argument('metadata', help='metadata csv from the modelmeta database')
parser.add_argument('outdir', help='directory to write files to')
args = parser.parse_args()

# first step through the metadata and sort tasmax or tasmin files
tasmins = []
tasmaxes = []
with open(args.metadata) as metadata:
    datasets = csv.DictReader(metadata)
    
    for row in datasets:
        if row["netcdf_variable_name"] == "tasmin":
            tasmins.append(row)
        if row["netcdf_variable_name"]== "tasmax":
            tasmaxes.append(row)
            
for tasmax in tasmaxes:
    for tasmin in tasmins:
        match = True
        for att in tasmax:
            if att != 'netcdf_variable_name' and att != 'filename':
                if tasmin[att] != tasmax[att]:
                    match = False
        if match:
            tasminfile = tasmin["filename"]
            tasmaxfile = tasmax["filename"] 
            print("{} matches {}!".format(tasminfile, tasmaxfile))
        

#print("There are {} tasmaxes and {} tasmins!".format(len(tasmaxes), len(tasmins)))


#tasminfile = "input/tasmin_sClimMean_BCCAQv2_PCIC12_historical+rcp85_rXi1p1_19610101-19901231_Canada.nc"
#tasmaxfile = "input/tasmax_sClim_BCCAQv2_PCIC12_historical+rcp85_rXi1p1_19610101-19901231_Canada.nc"

            tasmean_name = tasmaxfile.split('/')[-1].replace("tasmax", "tasmean")
            print("Creating {}".format(tasmean_name))
            with Dataset(tasminfile) as minfile, Dataset(tasmaxfile) as maxfile, Dataset("{}/{}".format(args.outdir, tasmean_name), "w") as meanfile:
                #copy dimensions
                print("  Now copying dimensions")
                for d in maxfile.dimensions:
                    size = None if maxfile.dimensions[d].isunlimited() else len(maxfile.dimensions[d])
                    meanfile.createDimension(d, size)
                
                print("  Now copying variables")
                for v in maxfile.variables:
                    if v != "tasmax":
                        meanfile.createVariable(v, maxfile.variables[v].dtype, maxfile.variables[v].dimensions)
                        meanfile.variables[v].setncatts(maxfile.variables[v].__dict__)
                        meanfile.variables[v][:] = maxfile.variables[v][:]
                    else:
                        print("    Generating tasmean data")
                        fill = maxfile.variables[v].getncattr("_FillValue")
                        meanfile.createVariable("tasmean", "d", maxfile.variables[v].dimensions,
                                                fill_value=fill)
                        meanfile.variables["tasmean"].setncattr("standard_name", "air_temperature")
                        meanfile.variables["tasmean"].setncattr("long_name", "Daily Mean Near-Surface Air Temperature")
                        meanfile.variables["tasmean"].setncattr("units", "degC")
                        meanfile.variables["tasmean"].setncattr("cell_methods", "time: mean within days time: mean over years")
                        meanfile.variables["tasmean"][:] = (maxfile.variables["tasmax"][:] + minfile.variables["tasmin"][:]) / 2.0
            
                print("  Now copying global attributes")
                meanfile.setncatts(maxfile.__dict__)
                print("  Now updating history")
                entry = "{}: tasmean {} {}".format(time.ctime(time.time()), tasminfile, tasmaxfile)
                meanfile.history = "{} ".format(entry) + (meanfile.history if "history" in meanfile.ncattrs() else "")         

    
    
    
    
print("Done!")