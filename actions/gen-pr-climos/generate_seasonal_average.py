from nchelpers import CFDataset
from argparse import ArgumentParser
from netCDF4 import num2date

def main(args):
    seasons = ["DJF", "MAM", "JJA", "SON"]
    output_file = args.input_file.replace("total", "average")
    if "pr" in output_file:
        clim_var = "pr"
    elif "snow" in output_file:
        clim_var = "snow"
    else:
        clim_var = "rain"

    with CFDataset(args.input_file) as src, CFDataset(output_file, mode="w") as dst:
        for name, dim in src.dimensions.items():
            dst.createDimension(name, len(dim))
        dst.setncatts({attr: src.getncattr(attr) for attr in src.ncattrs()})
    
        for name, var in src.variables.items():
            if name == clim_var:
                dst.createVariable(name, var.dtype, var.dimensions, fill_value = var.getncattr('_FillValue'))
            else:
                dst.createVariable(name, var.dtype, var.dimensions)
            dst.variables[name].setncatts({attr: var.getncattr(attr) for attr in var.ncattrs() if attr != '_FillValue'})
            dst.variables[name][:] = src.variables[name][:]
        
        dst.variables[clim_var].standard_name = src.variables[clim_var].standard_name.replace("Total", "Average")
        dst.variables[clim_var].long_name = src.variables[clim_var].long_name.replace("Total", "Average")
        ntimes = len(src.time_var)
        calendar = src.time_var.calendar
        for n in range(ntimes):
            if n == 0:
                if calendar == "360_day":
                    ndays = 30 + 30
                else:
                    ndays = 31 + 28
            else:
                seas = seasons[n % 4]
                timestep = src.time_var[n]
                year = num2date(timestep, src.time_var.units, calendar).year
                if calendar == "360_day":
                    ndays_per_season ={"DJF": 90, "MAM": 90, "JJA": 90, "SON": 90}
                elif calendar == "365_day":
                    ndays_per_season = {"DJF": 31+31+28, "MAM": 31+30+31, "JJA": 30+31+31, "SON": 30+31+30}
                else:
                    if year % 4 == 0:
                        ndays_per_season = {"DJF": 31+31+29, "MAM": 31+30+31, "JJA": 30+31+31, "SON": 30+31+30}
                    else:
                        ndays_per_season = {"DJF": 31+31+28, "MAM": 31+30+31, "JJA": 30+31+31, "SON": 30+31+30}
                    
                ndays = ndays_per_season[seas]
            dst.variables[clim_var][n] /= ndays

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file", metavar="input_file", help="Input seasonal totals file from which to compute means")
    args = parser.parse_args()
    main(args)
