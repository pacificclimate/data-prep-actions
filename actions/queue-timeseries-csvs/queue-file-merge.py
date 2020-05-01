'''This script automates merge-csv.py to run on the queue. It reads a directory
and generates a jobfile for each set of CSVs to merge, by making a copy of
template.pbs with string substitutions.'''

import argparse
import os

parser = argparse.ArgumentParser('Output a script for csv merging')
parser.add_argument('directory', help='directory with files to process')
args = parser.parse_args()
dir = args.directory

groups = []

files = os.listdir(dir)
for f in files:
    prefix = f.split(".")[0]
    if not prefix in groups:
        groups.append(prefix)


for g in groups:
    with open("merge{}.pbs".format(g), "w") as jobfile, open("template.pbs", "r") as template:
        for line in template:
            line = line.replace("NAME", g)
            line = line.replace("DATADIR", dir)
            jobfile.write(line)
            
    