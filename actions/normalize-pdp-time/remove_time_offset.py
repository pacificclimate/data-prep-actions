'''This script adjust timestamps on a netCDF file to be served by the PDP. 
The PDP assumes that the values of the time variable start at 0 when it
is determining the range represented by a file. This script changes the
reference timestamp in the units attribute to match the first day data
is available, and adjusts all time values accordingly.

For example, if your time variable looks like this:

    double time(time) ;
        time:units = "days since 1950-01-01 00:00:00" ;
        time:calendar = "365_day" ;
        time:long_name = "Time" ;
        time:standard_name = "Time" ;

    time = 365, 366, 367, 368, 369 ; 

The actual timestamps are the first five days of 1951. The time variable will 
be set to:

    double time(time) ;
        time:units = "days since 1951-01-01 00:00:00" ;
        time:calendar = "365_day" ;
        time:long_name = "Time" ;
        time:standard_name = "Time" ;

    time = 0, 1, 2, 3, 4 ; 
    

Use this script with care. It makes a major data change and has not been
tested outside the original dataset, BCCAQv2. 
'''

import argparse
import re, sys, datetime, math, time
from netCDF4 import Dataset

parser = argparse.ArgumentParser('Remove offset from the time variable of a CF-compliant netCDF file')
parser.add_argument('file', metavar='file', help='a netCDF file')
parser.add_argument('-d', '--dry-run', action="store_true", default = False,
                    help="dry run (no changes made to files, checks for errors)")
args = parser.parse_args()

filename = args.file

print("{}: Now {} {}".format(time.ctime(time.time()), 
                             "checking" if args.dry_run else "processing", 
                             filename))
nc = Dataset(filename, "r+")

# check assumptions
# 1. make sure file is in netCDF-4 format
if not nc.file_format == "NETCDF4":
    print("  ERROR: File is in {} format, not NETCDF4".format(nc.file_format))
    nc.close()
    sys.exit()

# 2. make sure there's a time variable
if not "time" in nc.variables:
    print("  ERROR: time variable not found".format(filename))
    nc.close()
    sys.exit()

timevar = nc.variables["time"]

# 3. make sure time has units of the form "days since YYYY-MM-DD"
if not "units" in timevar.ncattrs():
    print("  ERROR: time variable has no units attribute")
    nc.close()
    sys.exit()
units = timevar.units
# valid units formats:
#  "days since YYYY-MM-DD HH:MM:SS"
#  "days since YYYY-MM-DD"
# common invalid formats we accept as well:
#  "days since Y-MM-DD" ("days since 1-01-01")
#  "days since YYYY-M-D" ("days since 1850-1-1")
units_format = r'days since (\d\d?\d?\d?)-(\d\d?)-(\d\d?)( \d\d:\d\d:\d\d)?'
units_match = re.match(units_format, units)

if units_match:
    reference_date = datetime.datetime(int(units_match.group(1)), 
                                       int(units_match.group(2)), 
                                       int(units_match.group(3)))
else:
    print("  ERROR: time variable has invalid units format: {}".format(units))
    nc.close()
    sys.exit()

# 4. make sure time has a calendar attribute, and it's one we understand
if not "calendar" in timevar.ncattrs():
    print("  ERROR: time variable has no calendar attribute")
    nc.close()
    sys.exit()
calendar = timevar.calendar

if not calendar in ["standard", "gregorian", "proleptic_gregorian", 
                      "noleap", "365_day",
                      "360_day"]:
    print("  ERROR: invalid calendar: {}".format(calendar))
    nc.close()
    sys.exit()
    
# 5. make sure the file is daily frequency
if not "frequency" in nc.ncattrs() or not nc.frequency == "day":
    print("  Error: file is not daily resolution")
    nc.close()
    sys.exit()

# 6. make sure starting timestamp isn't already < 1
days = timevar[:]
if days[0] < 1:
    print("  ERROR: time variable has no offset; no correction needed")
    nc.close()
    sys.exit()
offset = math.floor(days[0])

# we're good to go! 
# figure out the actual starting date.
if calendar in ["standard", "gregorian", "proleptic_gregorian"]:
    first_timestamp = reference_date + datetime.timedelta(days=offset)
elif calendar in ["noleap", "365_day", "360_day"]:
    days_per_year = 360 if calendar == "360_day" else 365
    offset_years = math.floor(offset / days_per_year)
    offset_days = offset - (offset_years * days_per_year)
    # In every dataset I've seen, the first day is January 1. 
    # Not handling other cases, will quit if encountering one.
    if not offset_days == 0:
        print("  ERROR: This script is insufficiently sophisticated to handle partial nonstandard years")
        nc.close()
        sys.exit()
    
    delta_day = reference_date + datetime.timedelta(days=offset_days)
    first_timestamp = datetime.date(reference_date.year + offset_years, 
                                    delta_day.month, 
                                    delta_day.day)
    
# while not technically *required*, we strongly suspect
# the first timestamp is January 1 on a year encoded
# inside the filename - almost all daily PCIC datasets start
# January 1 and have years in the filename CMOR style.
# So this is an opportunistic check to catch inconsistencies
# in the file, such as the wrong calendar being listed
#
# (harken all ye unto the voice of bitter experience: 
#  the calendar attribute is wrong surprisingly often.
#  HadGem models are especially bad at this.)
filename_year_formats = r'.*_(\d\d\d\d)\d*-(\d\d\d\d)\d*.*nc'
years_match = re.match(filename_year_formats, filename)
if not years_match:
    print("  WARNING: filename dates not available for calendar verification")
    nc.close()
    sys.exit()
filename_start_year = int(years_match.group(1)[:4])
filename_end_year = int(years_match.group(2)[:4])
if not first_timestamp.year == filename_start_year or not first_timestamp.month == 1 or not first_timestamp.day == 1:
    print("  WARNING: calculated start date does not match expectations.")
    nc.close()
    sys.exit()

# if this is a dry run, exit before making any changes
if args.dry_run: 
    print("   INFO: Dry run found no errors!")
    nc.close()
    sys.exit()

# Update the timestamps
print("  Updating timestamps")
normalized = days - offset
timevar[:] = normalized

# update the units
print("  Updating units")
timevar.units = "days since {}".format(first_timestamp.strftime("%Y-%m-%d"))

# update history
print("  Updating history")
hist_entry = "remove_time_offset {}".format(filename.split("/")[-1])
nc.history = "{}: {} ".format(time.ctime(time.time()), hist_entry) + (nc.history if "history" in nc.ncattrs() else "")

# close file
nc.close()
