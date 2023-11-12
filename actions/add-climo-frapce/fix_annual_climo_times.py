'''
This single-use script sets the time variable (data timestamps) in a file if all the following are true:

* annual resolution climatology
* has time_bnds variable
* has climo_start_time and climo_end_time attributes
* the climatology is 30 years
* time variable is a 1x1 array
* calendar is 365_day
* the value of the single time datum is "365"

It is made to correct a specific weird situation, and not intended for broad reuse.
'''

import argparse
import numpy as np
from datetime import datetime
from netCDF4 import Dataset



parser = argparse.ArgumentParser('Supply missing timestamp for an annual 30-year climatology')
parser.add_argument('file', metavar='file', help='an annual 30 year climatology netCDF')
args = parser.parse_args()

filename = args.file

print("Now processing {}".format(filename.split("/")[-1]))

with Dataset(filename, "r+") as file:
    assert file.frequency in ["aClimMean", "aClim2.5P", "aClim97.5P"], "Unrecognized frequency: {}".format(file.frequency)

    start_date = datetime.strptime(file.climo_start_time, '%Y-%m-%dT%H:%M:%SZ')
    start_year = start_date.year

    end_date = datetime.strptime(file.climo_end_time, '%Y-%m-%dT%H:%M:%SZ')
    end_year = end_date.year

    assert start_year >= 1950, "This script assumes a start year of 1950 or later. Start: {}".format(start_year)

    assert end_year - start_year == 29, "This script assumes a thirty year climatology. Climo: {}-{}".format(start_year, end_year)
    
    assert "time" in file.variables, "This dataset has no time variable"
    time = file.variables["time"]
    assert time[:].size == 1, "Time variable has unexpected length: {}".format(time[:].size)
    assert time[:][0] == 365, "Time data expected to be 365, instead of {}".format(time[:][0])
    
    calendar = time.getncattr("calendar")
    assert calendar == "365_day", "Calendar expected to be 365_day, instead of {}".format(calendar)
    
    units = time.getncattr("units")
    assert units == "days since 1950-01-01 00:00:00", "1950 expected as reference year, instead of {}".format(units)
    
    assert "time_bnds" in file.variables, "This dataset has no time_bnds variable"
    
    #calculate the value. July 1 of "middle" year of climatology (start year + 15)
    # this is an easy calculation because all datasets this script is intended for 
    # are 365 day.
    middle_year = start_year + 15
    
    timestamp = ((middle_year - 1950) * 365) + 182
    
    print("  Updating timestamp to {}".format(timestamp))
    time[:] = np.array([timestamp])
    
    #update the history to indicate this script was used
    entry = "{}: fix_annual_climo_times {}".format(datetime.now().strftime("%a %b %d %H:%M:%S %Y"), filename.split("/")[-1])
    file.history = "{} {}".format(entry, (file.history if "history" in file.ncattrs() else ""))
    print("  Updating history.")
    
