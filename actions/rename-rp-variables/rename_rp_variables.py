#!python

'''The return period files as received have variables named
rp.20 or rp.5, no matter which type of 5-year or 10-year event they
describe. This script renames the variables to rp20tasmax or
rp5pr.

This is a procedure complicated enough to require a dedicated script
because (by design) the netCDF interface provides no way to rename a
variable. Unidata says:

  "Attributes are more dynamic than variables or dimensions; they can be
  deleted and have their type, length, and values changed after they are
  created, whereas the netCDF interface provides no way to delete a
  variable or to change its type or shape."

This script works by creating a copy of the original file with the 
variable name changed in the working directory, then deleting the
original file and replacing it with the copy.

It also corrects a minor error: in some of the return period files, 
_FillValue is an integer, even though the rp variable is a float.
Most tools will tolerate this, but some won't, and it's technically
wrong.'''

import argparse
from netCDF4 import Dataset
import random, string, re, time, os, sys

parser = argparse.ArgumentParser('Rename primary variable of a return period dataset')
parser.add_argument('file', metavar='file', help='a return period netCDF')
args = parser.parse_args()

filename = args.file

print("Processing {}".format(args.file.split("/")[-1]))

source = Dataset(filename, "r", format="NETCDF4")

#attempt to find the return period variable.
rpvar = None
for var in source.variables:
    if var.find("rp.") == 0:
        rpvar = var

if not rpvar:
    print("Error: {} contains no variables with return period prefix (rp.)".format(filename))
    source.close()
    sys.exit()
    
#attempt to determine the period
period = None
match = re.match(r'rp\.(\d*)', rpvar)
if(match):
    period = int(match.group(1))
else:
    print("Error: No numeric postfix in variable {}. Unable to determine period.".format(rpvar))
    source.close()
    sys.exit()
    
#try to determine what sort of return period this is from variable attributes.
model_output = None
attributes = source.variables[rpvar].ncattrs()
if "standard_name" in attributes:
    match = re.match(r'Annual Maximum (\w*)', source.variables[rpvar].standard_name)
    if match:
        model_output = match.group(1)    
if not model_output and "long_name" in attributes:
    match = re.match(r'Annual Maximum (\w*)', source.variables[rpvar].long_name)
    if match:
        model_output = match.group(1)
        
if not model_output:
    print("Error: Unable to determine model output of variable {} from name attributes".format(rpvar))
    source.close()
    sys.exit()
    
model_output = model_output.lower()
print("model output = {}".format(model_output))
model_output = "pr" if model_output == "precipitation" else model_output

#copy variables and attributes to temperary file:
random_filename = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
random_filename = "{}.nc".format(random_filename)
dest = Dataset(random_filename, "w", format="NETCDF4")
print("  Copying dimensions to temporary file.")
for dim in source.dimensions:
    size = None if source.dimensions[dim].isunlimited() else len(source.dimensions[dim])
    dest.createDimension(dim, size)

print("  Copying variables to temporary file.")
for var in source.variables:
    if var != rpvar:
        print("    Copying {}".format(var))
        dest.createVariable(var, source.variables[var].dtype, source.variables[var].dimensions)
        dest.variables[var].setncatts(source.variables[var].__dict__)
        dest.variables[var][:] = source.variables[var][:]
    else:
        newvar = "rp{}{}".format(period, model_output)
        print("    Copying {} as {}".format(var, newvar))
        fill = source.variables[var].getncattr("_FillValue")
        print("      Updating fill value for {}".format(newvar))
        dest.createVariable(newvar, source.variables[var].dtype, source.variables[var].dimensions, 
                            fill_value=fill)
        atts = source.variables[var].__dict__;
        for att in atts:
            if att != "_FillValue": #Fill value was set earlier.
                dest.variables[newvar].setncattr(att, source.variables[var].getncattr(att))
        dest.variables[newvar][:] = source.variables[var][:]
        
print("  Copying global attributes to temporary file.")
dest.setncatts(source.__dict__)

print("  Updating history in temporary file.")
entry = "rename_rp_variables {}".format(source.filepath().split("/")[-1])
dest.history = "{}: {} ".format(time.ctime(time.time()), entry) + (dest.history if "history" in dest.ncattrs() else "")

source.close()
dest.close()
print("  Replacing original file")
os.remove(filename)
os.rename(random_filename, filename)