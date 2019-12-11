'''Checks files in a directory to see which, if any, are missing.
Checks how many outputs are done by each process; reports any process
with fewer.'''

import os
import argparse
import re

parser = argparse.ArgumentParser('Check a directory of RVIC outputs for missing outputs')
parser.add_argument('directory', help='a folder containing RVIC outputs')
args = parser.parse_args()

filelist = os.listdir(args.directory)

print("Checking {} files in {}".format(len(filelist), args.directory))

# generate the set of processes and number of files each output
processes = {}
last_process = -1
most_points = 0
process_finder = r'_process(\d*)_point'
processes = {}
missing = False

for file in filelist:
    process = re.search(process_finder, file)
    if process:
        procnum = int(process.group(1))
        last_process = max(procnum, last_process)
        if procnum in processes:
            processes[procnum] = processes[procnum] + 1
        else:
            processes[procnum] = 1
        most_points = max(processes[procnum], most_points)
    else:
        print("{} is not an RVIC output".format(file))

if last_process == -1:
    print("No RVIC data in this directory")
    missing = True
else:
    print("Checking {} processes".format(last_process + 1))
    # check for missing files
    for i in range(last_process + 1):
        if i in processes:
            if processes[i] < most_points:
                if i == last_process:
                    print("Final process {} has only {} points".format(i, processes[i]))
                else:
                    print("ERROR: Only {} points for process {}. (Expected {})".format(processes[i], i, most_points))
                    missing = True
        else:
            print("ERROR: missing all data from process {}".format(i))
            missing = True

if not missing:
    print("No missing data found. Hooray!")
