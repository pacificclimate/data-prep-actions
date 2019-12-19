'''This script splits a yaml file provided by hydrology containing metadata
for all model-run combinations into a seperate yaml file for each model-run
combination. The resultant yaml files are intended as inputs to the
update_metadata tool.

This is intended to be a single-use script; reusability is not a design goal.'''

import argparse
from yaml import load, dump

parser = argparse.ArgumentParser('Break a hydrology metadata yaml into one '
                                 'file for each model-experiment combination')
parser.add_argument('file', help='input yaml file')

args = parser.parse_args()
infile = open(args.file, "r")
input = load(infile)

for run in input["CMIP5"]["experiments"]:
    dict = {}
    for att in input["CMIP5"]["experiments"][run]:
        val = input["CMIP5"]["experiments"][run][att]
        #fix a metadata issue:
        if att in ['initialization_method', 'physics_version', 'realization']:
            val = val.strip('rip')
        dict["downscaling__GCM__{}".format(att)] = val
    output = {"global": dict}
    outfile = open("{}.yaml".format(run), "w")
    outfile.write(dump(output))
    outfile.close()
infile.close()
