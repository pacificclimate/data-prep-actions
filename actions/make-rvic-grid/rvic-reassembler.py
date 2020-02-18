'''
This is the companion script to rvic-queuer.py Rvic-queuer outputs
job scripts, each of which can be run on a compute node to calculate
streamflow for a single grid square in the watershed domain file. 

This script assembles the resulting individual files into a single
grid file.

As inputs, it takes:
* a directory containing streamflow result files
* the watershed domain file (determine extent of watershed)
* the baseflow file (for metadata about the model)
* the desired name for the finished file

This script does not produce complete PCIC-standards-compliant metadata;
some additional metadata munging  will be needed afterwards. It does copy
all relevant (and some irrelevant) metadata from individual streamflow
files and the baseflow file, so it makes a start on metadata.
'''

from netCDF4 import Dataset, default_fillvals
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser('Assemble RVIC routed streamflow output into a grid')
parser.add_argument('-b', '--baseflow', help='VICGL output file used to generate these streamflows')
parser.add_argument('-d', '--domain', help='a routing domain file')
parser.add_argument('-s', '--streamflow_dir', help='a directory containing routed streamflow')
parser.add_argument('-n', '--name', help='name of the file to create')
args = parser.parse_args()
            
# initialize output file
output = Dataset(args.name, "w")

def grid_object(x, y):
    return {"x": x, "y": y}

# the baseflow file contains modeled runoff and baseflow over time,
# based on the rainfall predicted by a model. 
# the finished output file's time data will match the baseflow,
# and we will also get metadata about the driving model from it.
with Dataset(args.baseflow) as baseflow:
    #output's time data matches the baseflow data
    print("Initializing time data")
    timesteps = len(baseflow.dimensions["time"])
    output.createDimension("time", timesteps)
    output.createVariable("time", baseflow.variables["time"].dtype, ("time"))
    output.variables["time"].setncatts(baseflow.variables["time"].__dict__)
    output.variables["time"][:] = baseflow.variables["time"][:]

    # copy global metadata from the baseflow file 
    # (this metadata is about the model and run that generated the
    # input data. It will be prefixed with "hydromodel__")
    global_atts_copied = 0
    for att in baseflow.__dict__:
        hm_att = "hydromodel__{}".format(att)
        output.setncattr(hm_att,baseflow.getncattr(att))
        global_atts_copied += 1
    print("{} hydromodel metadata attributes added".format(global_atts_copied))

# the domain file encodes the shape and characteristics of the watershed
# the final output file will use the domain file to determine 
# spatial layout of the watershed.
with Dataset(args.domain) as domain:
    # latitude and longitude variables match the domain file
    latsteps = len(domain.dimensions["lat"])
    output.createDimension("lat", latsteps)
    output.createVariable("lat", domain.variables["lat"].dtype, ("lat"))
    output.variables["lat"].setncatts(domain.variables["lat"].__dict__)
    output.variables["lat"][:] = domain.variables["lat"][:]

    lonsteps = len(domain.dimensions["lon"])
    output.createDimension("lon", lonsteps)
    output.createVariable("lon", domain.variables["lon"].dtype, ("lon"))
    output.variables["lon"].setncatts(domain.variables["lon"].__dict__)
    output.variables["lon"][:] = domain.variables["lon"][:]
    
    # determine which cells are part of the watershed, and which we need
    # streamflow data for
    # First make a list of all the grid cells we need
    missing_cells = []
    for y in range(domain.variables["lat"].size):
        for x in range(domain.variables["lon"].size):
            mask = domain.variables["mask"][y][x]
            if mask > 0: # this cell is in the watershed
                missing_cells.append(grid_object(x, y))

# create streamflow variable, copying metadata from an 
# arbitrary streamflow file
# some metadata is not applicable, because it only applies to a
# single grid cell and not the whole thing, but fixing them is
# left to update_metadata, not this script.
# select an arbitrary streamflow output
with Dataset("{}{}".format(args.streamflow_dir,
                            os.listdir(args.streamflow_dir)[1]), "r") as sf_meta:
    default_fill = default_fillvals['f4']
    sf_var = output.createVariable("streamflow", 
                                   sf_meta.variables["streamflow"].dtype,
                                   ("time", "lat", "lon"),
                                   fill_value=default_fill)
    sf_var.setncatts(sf_meta.variables["streamflow"].__dict__)
    output.setncatts(sf_meta.__dict__)

print("Looking for {} cells".format(len(missing_cells)))

files = 0

#for testing, you can subset this (and should)
filelist = os.listdir(args.streamflow_dir)

class NoDataFileError(Exception):
    pass

class WrongDataError(Exception):
    pass

# finally, read each streamflow file and add its data to the grid.        
for file in filelist:
    try:
        #todo - make resilient to final slash or not in dir.
        if file.find(".nc") == -1:
            raise NoDataFileError("Not a netCDF file")
        streamflow = Dataset("{}{}".format(args.streamflow_dir, file))
    
        # Make sure the file contains what we're looking for
        if "outlets" not in streamflow.dimensions:
            raise WrongDataError("No outlets dimension")
        if not "outlet_x_ind" in streamflow.variables:
            raise WrongDataError("Missing outlet_x_ind variable")            
        if not "outlet_y_ind" in streamflow.variables:
            raise WrongDataError("Missing outlet_y_ind variable")
        if not "streamflow" in streamflow.variables:
            raise WrongDataError("No streamflow data")
        if len(streamflow.dimensions["outlets"]) > 1:
            raise WrongDataError("This script assumes one outlet per file")
        
        # get the x and y indexes of this file. These are set by RVIC 
        # and correspond to the x and y positions in the original
        # grid (from the domain file)
        x = streamflow.variables["outlet_x_ind"][0]
        y = streamflow.variables["outlet_y_ind"][0]
        print("{}. Now processing {}. Detected x: {}, detected y: {}".format(files, file, x, y))
        grid = grid_object(x, y)
        
        if grid in missing_cells:
            missing_cells.remove(grid)
        else:
            raise WrongDataError("x: {}, y: {} is not in this watershed".format(x, y))
        
        sf_var[...,y,x] = streamflow.variables["streamflow"][:]
        
    except WrongDataError as e:
        print("ERROR with data in {}: {}".format(file, str(e)))
        streamflow.close()
    except NoDataFileError as e:
        print("ERROR with {}: {}".format(file, str(e)))
    else:
        files += 1
    
print("Processed {} streamflow files".format(files))
if len(missing_cells) > 0:
    print("WARNING: {} grid cells missing from this watershed".format(len(missing_cells)))
else:
    print("Watershed as defined in domain file is complete.")
            
output.close()