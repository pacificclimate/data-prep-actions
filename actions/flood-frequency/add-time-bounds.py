'''
The time bounds variable, time_bnds, indicates for each timestamp of
data, the start and end date of the period described by that data. It
is automatically added by CDO in the process of generating a climatology,
but sometimes other data creation paths at PCIC don't add it.

The PCEX backend uses it to compare climatologies.

This script will automatically add missing time_bnds variablesm using the
climo_start_time and climo_end_time global attributes. 
'''

import argparse, datetime, time
from netCDF4 import Dataset
import numpy as np

parser = argparse.ArgumentParser("Create a mising time_bnds variable")
parser.add_argument("infile", metavar="infile", help="input file")
parser.add_argument("outfile", metavar="outfile", help="output file")
args = parser.parse_args()

try:
    infile = Dataset(args.infile)
    outfile = Dataset(args.outfile, "w")
    
    #make sure input lacks time_bnds
    if "time_bnds" in infile.variables:
        raise Exception("Input file already has climatology bounds variable")
    
    #make sure input has necessary metadata
    for attribute in ["climo_start_time", "climo_end_time", "frequency"]:
        if not attribute in infile.ncattrs():
            raise Exception("Input file does not have {} attribute".format(attribute))
    
    #make sure input has a time variable
    if not "time" in infile.variables:
        raise Exception("Input file has no time variable!")
    
    #make sure input is annual
    if not infile.frequency.startswith("aClim"):
        raise Exception("Input file is not an annual climatology: {}".format(infile.frequency))
    
    #write output
    print("Creating dimensions")
    for d in infile.dimensions:
        size = None if infile.dimensions[d].isunlimited() else len(infile.dimensions[d])
        outfile.createDimension(d, size)
    outfile.createDimension("bnds", 2)
    
    print("Creating variables")
    for v in infile.variables:
        outfile.createVariable(v, infile.variables[v].dtype, infile.variables[v].dimensions)
        outfile.variables[v].setncatts(infile.variables[v].__dict__)
        outfile.variables[v][:] = infile.variables[v][:] 
    
    print("Filling in time_bnds")
    outfile.createVariable("time_bnds", "f8", ("time", "bnds"))
    
    #get reference date
    ref = infile.variables["time"].units
    ref_date = datetime.datetime.strptime(ref, 'days since %Y-%m-%d %H:%M:%S')
    
    #get start and end dates
    start_date = datetime.datetime.strptime(infile.climo_start_time, '%Y-%m-%dT%H%M%SZ')
    end_date = datetime.datetime.strptime(infile.climo_end_time, '%Y-%m-%dT%H%M%SZ')
    outfile.variables["time_bnds"][:] = np.array([[(start_date - ref_date).days, (end_date - ref_date).days]])    
    
    print("Creating attributes")
    for attr in infile.ncattrs():
        if attr != "_NCProperties":
            outfile.setncattr(attr, infile.getncattr(attr))
    
    print("Updating history")
    entry = "add_time_bounds {} {}".format(args.infile, args.outfile)
    outfile.history = "{}: {} ".format(time.ctime(time.time()), entry) + (outfile.history if "history" in outfile.ncattrs() else "")
    
except Exception as err:
    print(err)

finally:
    infile.close()
    outfile.close()