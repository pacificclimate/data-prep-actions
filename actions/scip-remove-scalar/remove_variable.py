# Accepts a netCDF files and a variable name as input arguments
# Writes a version of the input file without the variable
# copies it over the original file.
# This is intended to deal with scalar variables that our typical command
# line tools have trouble removing.

import datetime
from netCDF4 import Dataset
import argparse
import os

parser = argparse.ArgumentParser(description='Remove a variable from a netCDF file.')
parser.add_argument('input_file', type=str, help='Path to the input netCDF file')
parser.add_argument('variable_name', type=str, help='Name of the variable to remove')
args = parser.parse_args()  

input_file = args.input_file
var = args.variable_name

input = Dataset(input_file, 'r')
output = Dataset("temp.nc", "w")

print(f"Removing variable '{var}' from file '{input_file}'")

# Copy dimensions
print("  Copying dimensions...")
for name, dimension in input.dimensions.items():
    output.createDimension(name, (len(dimension) if not dimension.isunlimited() else None))

# Copy variables except the one to remove
print("  Copying variables...")
for name, variable in input.variables.items():
    if name == var:
        print(f"    Skipping variable '{var}'")
        continue
    output.createVariable(name, variable.dtype, dimensions=variable.dimensions)
    output.variables[name].setncatts(input.variables[name].__dict__)
    output.variables[name][:] = input.variables[name][:]

# Copy global attributes
print("  Copying global attributes...")
for attr_name in input.ncattrs():
    if attr_name != 'history':
        output.setncattr(attr_name, input.getncattr(attr_name))

print("  Updating history attribute...")
entry = f"{str(datetime.datetime.now())}: remove-scalar-variable {input_file} {var}"
output.history = entry + input.history


output.close()
input.close()

# Overwrite the original file with the new one
os.replace("temp.nc", input_file)