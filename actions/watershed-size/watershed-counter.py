'''This script accepts a "domain" RVIC file and reports how many grid cells are
part of the watershed.'''

from netCDF4 import Dataset
import argparse

parser = argparse.ArgumentParser('Count the number of watershed cells in a domain file')
parser.add_argument('domain', help='an RVIC domain netCDF')

args = parser.parse_args()

domain = Dataset(args.domain, "r")

variables_needed= ["lat", "lon", "mask"]
missing_variable = None

for checkvar in variables_needed:
    if checkvar not in domain.variables:
        missing_variable = checkvar

if missing_variable:
    print("{} variable missing from {}".format(missing_variable, args.domain))
else:
    watershed_size = 0
    for y in range(domain.variables["lat"].size):
        for x in range(domain.variables["lon"].size):
            mask = domain.variables["mask"][y][x]
            if mask > 0: # this cell is in the watershed
                watershed_size += 1
    print("This domain contains {} grid cells inside the watershed".format(watershed_size))
    
domain.close()