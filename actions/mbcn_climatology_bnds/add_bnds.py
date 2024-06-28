from nchelpers import CFDataset
from dp.generate_climos import generate_climo_time_var
from netCDF4 import date2num
import sys
import datetime
import dateutil.parser

filepath = sys.argv[1]
with CFDataset(filepath, mode="r+") as cf:
    start_year = int(filepath[-12:-8])
    end_year = int(filepath[-7:-3])
    calendar = cf.time_var.calendar
    end_day = 30 if calendar == "360_day" else 31
    t_start = datetime.datetime(start_year, 1, 1)
    t_end = datetime.datetime(end_year, 12, end_day)
    cf.climo_start_time = t_start.isoformat()[:19] + "Z"
    cf.climo_end_time = t_end.isoformat()[:19] + "Z"
    
    num_times_to_interval_set = {12: {"monthly"}, 4: {"seasonal"}, 1: {"annual"}}
    interval_set = num_times_to_interval_set[cf.time_var.size]
    interval = next(iter(interval_set))
    prefixes = {"monthly": "m", "seasonal": "s", "annual": "a"}
    prefix = prefixes[interval]
    if "tas" in cf.variables:
        cf.variable_id = "tas"
    cf.frequency = prefix + "ClimMean"
    
    times, climo_bounds = generate_climo_time_var(
                                                dateutil.parser.parse(cf.climo_start_time[:19]),
                                                dateutil.parser.parse(cf.climo_end_time[:19]),
                                                interval_set,
                                                )
    cf.time_var[:] = date2num(times, cf.time_var.units, calendar)

    if "bnds" not in cf.dimensions:
        cf.createDimension("bnds", 2)
    cf.time_var.climatology = "climatology_bnds"
    climo_bnds_var = cf.createVariable("climatology_bnds", "f4", ("time", "bnds"))
    climo_bnds_var.calendar = calendar
    climo_bnds_var.units = cf.time_var.units
    climo_bnds_var[:] = date2num(climo_bounds, cf.time_var.units, calendar)
