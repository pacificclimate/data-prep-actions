'''The CF Standards support using data variables with no associated dimensions
to store coordinate reference information. The variable is used to tightly group
attributes that specify various values for the CRS. Here's an example:

int crs ;
        crs:grid_mapping_name = "latitude_longitude" ;
        crs:long_name = "CRS definition" ;
        crs:longitude_of_prime_meridian = 0. ;
        crs:semi_major_axis = 6378137. ;
        crs:inverse_flattening = 298.257222101 ;
        crs:GeoTransform = "-140.0041666666665 0.008333333332999999 0 61.9958333333325 0 -0.008333333332999999 " ;
        crs:crs_wkt = "GEOGCS[\"NAD83\",DATUM[\"North_American_Datum_1983\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6269\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4269\"]]" ;

Unfortunately, the PDP cannot actually serve a dimensionless variable. 

This script is a quick hack. It takes a file with a dimensionless crs variable and
outputs a file identical except for the fact that the crs variable has a time
dimension and a single value (0). All other variables and attributes are simply copied.
'''

import argparse
from netCDF4 import Dataset
import time

parser = argparse.ArgumentParser('convert a dimensionless CRS variable to time-based')
parser.add_argument('infile', metavar='infile', help='input netCDF file')
parser.add_argument('outfile', metavar='outfile', help='location to write output file to')
args = parser.parse_args()

infile = Dataset(args.infile, "r", format="NETCDF4")

print("Processing {} to {}".format(args.infile, args.outfile))
# check to see if there's a dimensionless CRS variable
if not "crs" in infile.variables:
    print("Error: No CRS variable in {}".format(args.infile))
    infile.close()
    sys.exit()
elif infile.variables["crs"].dimensions is None:
    print("Error: CRS variable already has a dimension".format(args.infile))
    infile.close()
    sys.exit()
    
outfile = Dataset(args.outfile, "w", format="NETCDF4")

#Copy over everything else.

# Dimensions
for dim in infile.dimensions:
    size = None if infile.dimensions[dim].isunlimited() else len(infile.dimensions[dim])
    outfile.createDimension(dim, size)

# Non-CRS variables
for var in infile.variables:
    if var != "crs":
        print("    Copying variable {}".format(var))
        outfile.createVariable(var, infile.variables[var].dtype, infile.variables[var].dimensions)
        outfile.variables[var].setncatts(infile.variables[var].__dict__)
        outfile.variables[var][:] = infile.variables[var][:]

# Global attributes
print("    Copying global attributes")
outfile.setncatts(infile.__dict__)

# Update the CRS
print("    Updating CRS")
outfile.createVariable("crs", "i", ("time"))
outfile.variables["crs"].setncatts(infile.variables["crs"].__dict__)
outfile.variables["crs"][:] = 0        

# Update the history attribute
print("    Updating history global attribute")
entry = "{}: dimensionize_crs {} {}".format(time.ctime(time.time()), args.infile, args.outfile)
outfile.history = "{} {}".format(entry, outfile.history if "history" in outfile.ncattrs() else "")


# clean up
infile.close()
outfile.close()
print("Successfully updated CRS")