# This script reads a CSV thst indicates which conservation units overlap with 
# watersheds and outputs a CSV of which species are present in which watersheds.
#
# There's some difficulty due to bad data in the input - some watersheds are
# listed as overlapping conservation units from more than one basin, which is 
# an artifact of the interpolation process from shapefile. Accordingly,
# this script accepts a second CSV that canonically lists which basin each
# watershed is in, and ignores conservation units in a different basin.
#
# For example, let's say Watershed X is listed as overlapping and containing
# the following two conservation units: cc_ck_01 (central coast chinook) and
# fr_cm_02 (fraser chum). Watershed X cannot be in both the central coast
# and the Fraser, a watershed belongs to a single basin. In this case, we 
# would look up Watershed X in the canonical list of basins, discover it
# belongs to the central coast, and ignore the Fraser-related entry; only
# chinook would be listed for this watershed.
#
# This script meets very specific needs and is not reusable.

import argparse
import csv

parser = argparse.ArgumentParser('Output a CSV correlating watersheds with salmon species')
parser.add_argument('conservation_units', help='a CSV listing watersheds and their conservation units')
parser.add_argument('basin_corrections', help='a csv file listing watersheds and which basin they belong to')
parser.add_argument('output', help='name of CSV file to output data to')

args = parser.parse_args()



salmon_codes = {
    "ck": "Chinook",
    "cm": "Chum",
    "co": "Coho",
    "pke": "Pink_Even_Year",
    "pko": "Pink_Odd_Year",
    "sel": "Sockeye_Lake",
    "ser": "Sockeye_River"
}


basin_codes = {
    "cc": "Central Coast",
    "fr": "Fraser",
    "hg": "Haida Gwai",
    "na": "Nass",
    "sk": "Skeet",
    "vimi": "Vancouver Island And Mainland Inlets"
}

#map between the basin codes used in the conservation units CSV
#and the basin names in the canonical CSV. 
basin_canonical = {
    "cc": "COAST",
    "fr": "FRASER RIVER",
    "hg": "COAST",
    "na": "NASS RIVER",
    "sk": "SKEENA RIVER",
    "vimi": "COAST"
}

# first build a dictionary with the canonical basin for each
# watershed. conservation units from outside that basin will be ignored.
basins = dict()
with open(args.basin_corrections) as bc:
    bc_reader = csv.DictReader(bc)
    for row in bc_reader:
        basins[row["WTRSHDGRPC"]] = row["MJRDRAIN"]
        
print(basins)



# get the actual data
with open(args.conservation_units) as cu, open(args.output, "w") as output:
    cu_reader = csv.DictReader(cu)
    fields = ["WTRSHDGRPC", "Chinook", "Chum", "Coho", "Pink_Even_Year", "Pink_Odd_Year", "Sockeye_Lake", "Sockeye_River"]
    output_writer = csv.DictWriter(output, fields)
    output_writer.writeheader()

    for row in cu_reader:
        watershed = row["WTRSHDGRPC"]
        basin = basins[watershed]
        print("Parsing watershed {} in basin {}".format(watershed, basin))
        found_salmon = False

        out_dict = {
            "WTRSHDGRPC": watershed,
            "Chinook": False,
            "Chum": False,
            "Coho": False,
            "Pink_Even_Year": False,
            "Pink_Odd_Year": False,
            "Sockeye_Lake": False,
            "Sockeye_River": False            
        }

        for col in row:
            if row[col] == "1":
                ct = col.split("_")
                if basin_canonical[ct[0]] == basin:
                    print("  {} is a valid entry for {}: {}".format(col, watershed, salmon_codes[ct[1]]))
                    out_dict[salmon_codes[ct[1]]] = True
                    found_salmon = True
                else:
                    print("  {} is not a valid entry for {}".format(col, watershed))
                    print("    {} is in the {} basin, but this entry is for {} basin".format(watershed, basin, basin_canonical[ct[0]]))
        if not found_salmon:
            print("  No salmon found in this watershed")
        output_writer.writerow(out_dict)
        





