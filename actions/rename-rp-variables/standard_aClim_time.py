#!python
'''
This single-use script generates missing time data for netCDF files
only if ALL the following conditions hold:

1. The file is an annual climatology
2. The climatology period is 30 years long
3. The climatology period start and stop years are in the filename as 4-digit numbers
4. The time variable exists, with units "days since 1-01-01 00:00:00"
5. The time variable is a 1x1 array
6. The only available time value is 1
7. The time_bnds variable does not exist
8. The calendar is gregorian or gregorian proleptic
9. The entire climatology takes place after 1950

This script is kludgy as heck, and its fondest, most treasured dream is 
never to be used again.
'''

import argparse
import numpy as np
import re, sys, datetime, math, time
from netCDF4 import Dataset

parser = argparse.ArgumentParser('Supply missing timestamps for an annual 30-year climtology')
parser.add_argument('file', metavar='file', help='an annual 30-year climatology netCDF')
args = parser.parse_args()

filename = args.file

print("Now processing {}".format(filename.split("/")[-1]))
# Try and determine climatology from the filename
template = r'.*_(\d\d\d\d)-(\d\d\d\d)\.nc'
yearMatch = re.match(template, filename)
if yearMatch:
    startYear = int(yearMatch.group(1))
    endYear = int(yearMatch.group(2))
    if(endYear - startYear != 29):
        print("  Error: {} spans {}-{}: a 30 year climatology is required".format(filename, startYear, endYear))
else:
    print("  Error: unable to determine climatology span of {}".format(filename))
    sys.exit()

if(startYear < 1950):
    print("  Error: this script assumes a start year of 1950 or later. Start: {}".format(startYear))
    sys.exit()

file = Dataset(filename, "r+")
# Check assumptions before changing anything.
if not "time" in file.variables:
    print("  Error: time variable not found.")
    file.close()
    sys.exit()
    
time = file.variables["time"]

expected_units = "days since 1-01-01 00:00:00"
units = time.getncattr("units")
if not units == expected_units:
    print("  Error: expected time.units to be {}, found {}".format(expected_units, units))
    file.close()
    sys.exit()

calendar = time.getncattr("calendar")
if calendar in ("gregorian", "standard", "proleptic_gregorian"):
    calendar = "standard"
elif calendar in ("365_day", "no_leap"):
    calendar = "365_day"
elif calendar == "360_day":
    calendar = "360_day"
else:
    print("  Error: unexpected calendar found: {}".format(calendar))
    file.close()
    sys.exit()

if "time_bnds" in file.variables:
    print("  Error: time_bnds variable already exists.")
    file.close()
    sys.exit()
    
if not time[:].size == 1:
    print("  Error: time variable has unexpected length: {}".format(time[:].size))
    file.close()
    sys.exit()

if not time[:][0] == 1:
    print("  Error: unexpected value for timevariable: {}".format(time[:][0]))
    file.close()
    sys.exit()

# calculate how many days between two dates for various calendars
def delta_days(cal, sYear, sMonth, sDay, eYear, eMonth, eDay):
    if cal == "standard":
        return (datetime.datetime(eYear, eMonth, eDay) - datetime.datetime(sYear, sMonth, sDay)).days
    elif cal == "365_day":
        per_year = 365
    elif cal == "360_day":
        per_year = 360
    
    year_delta = (eYear - sYear) * per_year
    day_delta = (datetime.datetime(1999, eMonth, eDay) - datetime.datetime(1999, sMonth, sDay)).days
    #scale days by the number of days in a year.
    day_delta = round((day_delta / per_year) * day_delta)
    return year_delta + day_delta


# set the baseline time: Jan 1, 1950
time.setncattr("units", "days since 1950-01-01 00:00:00")

# set time value
delta = delta_days(calendar, 1950, 1, 1, endYear, 1, 1)
time[:] = np.array([delta])
print("  Updated time units and values.")

# create the time_bnds variable
file.createDimension("bnds", 2)
time_bnds = file.createVariable("time_bnds", "f8", ("time", "bnds"))

start_delta = delta_days(calendar, 1950, 1, 1, startYear, 1, 1)
end_delta = delta_days(calendar, 1950, 1, 1, endYear, 12, 31)
time_bnds[:] = np.array([[start_delta, end_delta]])
print("  Created time_bnds")

entry = "{}: standard_aClim_time {}".format(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), filename.split("/")[-1])
file.history = "{} {}".format(entry, (file.history if "history" in file.ncattrs() else ""))
print("  Updated history.")


file.close()
