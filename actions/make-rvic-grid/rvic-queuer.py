'''This script generates PBS files for RVIC jobs for every grid cell in an
entire watershed.

It requires:
  1. a VICGL output dataset ("baseflow")
  2. a routing domain file ("domain")
  3. a routing parameters file ("parameters")

The script checks to make sure the three files have identical grids. If so, it
generates a .PBS job file for every square on the grid that is part of the domain
according to the domain file.

Each grid square will receive the casename MODEL.EXPERIMENT.LAT###.LON###

In order to run the resulting PBS jobs, the input files should be at some location
accessible to the queue.

If n is not 0, the resulting script is long and repetitive; it generates a new set of
config files for each point. Debugging may be difficult; it is recommended to run with
-n 1 for debugging.
'''

from netCDF4 import Dataset
import argparse
import numpy as np
import random
import string
import datetime
import re

watershed = "Peace"
environment = "/storage/data/projects/comp_support/climate_explorer_data_prep/hydro/peace_watershed/venv/bin/activate"

parser = argparse.ArgumentParser('Generate PBS files to queue RVIC calcuations')
parser.add_argument('-b', '--baseflow', help='a VICGL output ')
parser.add_argument('-d', '--domain', help='a routing domain file')
parser.add_argument('-p', '--parameters', help='a routing parameters file')
parser.add_argument('-u', '--unit_hydrograph', help='the unit hydrograph file')
parser.add_argument('-o', '--outdir', help="directory to place the scripts in")
parser.add_argument('-n', '--num_cells', help="the number of cells to calculate per process")
parser.add_argument('-r', '--results_dir', help="location to copy results to")
args = parser.parse_args()

domain = Dataset(args.domain, "r")
baseflow = Dataset(args.baseflow, "r")
parameters = Dataset(args.parameters, "r")
num_cells = int(args.num_cells)

# make sure all three files share the same grid.
if not np.allclose(domain.variables["lat"][:], baseflow.variables["lat"]):
    raise Exception("Latitudes in baseflow file do not match domain")
if not np.allclose(domain.variables["lat"][:], parameters.variables["lat"]):
    raise Exception("Latitudes in parameter file do not match domain")
if not np.allclose(domain.variables["lon"][:], baseflow.variables["lon"]):
    raise Exception("Longitudes in baseflow file do not match domain")
if not np.allclose(domain.variables["lon"][:], parameters.variables["lon"]):
    raise Exception("Longitudes in parameter file do not match domain")
    
# todo: check to make sure input files have the variables they should
    
# read metadata from the modeled input
# these will be used to configure the rvic runs
model = baseflow.downscaling_GCM_model_id
experiment = baseflow.downscaling_GCM_experiment_id
run = "{}{}{}".format(baseflow.downscaling_GCM_realization,
                         baseflow.downscaling_GCM_initialization_method,
                         baseflow.downscaling_GCM_physics_version)
    
    
    
# parse time metadata
time = baseflow.variables["time"]
calendar = time.calendar
time_units_format = r'days since (\d\d?\d?\d?)-(\d\d)-(\d\d)( \d\d:\d\d:\d\d)?'
time_units_match = re.match(time_units_format, time.units)

if time_units_match:
    reference_date = datetime.datetime(int(time_units_match.group(1)), 
                                       int(time_units_match.group(2)), 
                                       int(time_units_match.group(3)))
     
# returns a day that is delta days later than start for a given calendar
def date_addition(start, delta, calendar):
    if calendar in ["standard", "gregorian", "proleptic_gregorian"]:
        return start + datetime.timedelta(days=delta)
    elif calendar in ["noleap", "365_day", "360_day"]:
            days_per_year = 360 if calendar == "360_day" else 365
            delta_years = math.floor(delta / days_per_year)
            delta_days = delta - (delta_years * days_per_year)
    
    new_day = start + datetime.timedelta(days=delta_days)
    return datetime.date(start.year + delta_years, 
                                new_day.month, 
                                new_day.day) 
        
startdate = date_addition(reference_date, int(time[0]), calendar)
enddate = date_addition(reference_date, int(time[-1]), calendar)
    

    
process_points = []
all_processes = []
    
# step through the watershed gridwise, and group all points that are
# members of the watershed (ie, have mask = 1 in the domain file)
# into groups of n that will be processed together.
    
# you might expect that we would want to try and group the points by
# area, but according to RVIC documentation, because RVIC is a 
# "source to sink" model, it can't reuse any earlier calculations.
# so we can group points that run together pretty much arbitrarily.

for y in range(domain.variables["lat"].size):
    for x in range(domain.variables["lon"].size):
        mask = domain.variables["mask"][y][x]
        if mask > 0: # this cell is in the watershed
            if len(process_points) == num_cells:
                all_processes.append(process_points)
                process_points = []
            lat = domain.variables["lat"][y]
            lon = domain.variables["lon"][x]
            cellname = "{}_{}_{}_x{}_y{}".format(model, experiment, run, x, y)
            process_points.append("{},{},{}".format(lon, lat, cellname))
all_processes.append(process_points)
    
# now we need to write a PBS script for each process. Each one will have
# a different set of pour points to calculated, but otherwise they all take
# the same input.
    
# this function adds commands to the PBS script that will create a new
# file when the script is run. It is used to create the various config
# files RVIC needs to run.
def write_create_file(filename, lines, pfile):
    eof = "EOF{}".format(random.randint(0, 999999))
    write_progress("Creating {}".format(filename), pfile)
    pfile.write("cat > {} << {}\n".format(filename, eof))
    write_lines(lines, pfile)
    pfile.write("{}\n".format(eof))
    write_newline(pfile)
    
# this function takes a dictionary whose keys are strings and whose
# values are dictionaries. It outputs an array of strings representing
# a windows INI style config file. 
# Each key becomes a section header for a section containing all 
# key:value pairs in that section's dictionary.
# {section: {a: 1, b: 2}} becomes 
# [SECTION]
# #-- ==================================== --#
# A: 1
# B: 2
# 
def multidict_to_config(dict):
    lines = []
    for section in dict:
        lines.append("[{}]".format(section.upper()))
        lines.append("#-- ==================================== --#")
        for att in dict[section]:
            lines.append("{}: {}".format(att.upper(), dict[section][att]))
        lines.append("")
    return lines
        
    
# this function writes each line in line to file, and adds a \n
def write_lines(lines, pfile):
    for line in lines:
        pfile.write("{}\n".format(line))
    
# this function adds a progress report to the process
def write_progress(text, pfile):
    write_newline(pfile)
    pfile.write("echo $(date): {}\n".format(text))
    
# this function adds a comment to copy a file from one place to another
def write_file_copy(file, dir, pfile):
    write_progress("Copying {} to {}".format(file, dir), pfile)
    pfile.write("cp {} {}\n".format(file, dir))
    
#writes a blank line to the file. Useful for readability.
def write_newline(pfile, num=1):
    for i in range(num):
        pfile.write("\n")
    
# return the base name of a file, /home/tmp/x.txt => x.txt    
def file_basename(filepath):
    return filepath.split('/')[-1]

# writes an execution argument for PBS    
def write_pbs_argument(argument, value, pfile):
    pfile.write("#PBS -{} {}\n".format(argument, value))
    
point = 0    
for proc in range(len(all_processes)):
    print("writing file {}".format(proc))
    pbsfile = open("{}/rvic{}.pbs".format(args.outdir, proc), "w+")

    #allow 25 minutes per point, which should be plenty
    runtime = datetime.timedelta(minutes = 25 * num_cells)
    
    # allow 1 GB per point - RVIC outputs plot images and other
    # artifacts that take up a lot of room, even though the
    # output data itself is only about 7MB
    memory_size = 60 + num_cells
    
    # write the headers
    pbsfile.write("#!/bin/bash\n")
    pbsfile.write("#PBS -l nodes=1:ppn=1\n")
    pbsfile.write("#PBS -l vmem=12000mb\n")
    pbsfile.write("#PBS -l walltime={}\n".format(str(runtime)))
    pbsfile.write("#PBS -l file={}gb\n".format(memory_size))
    pbsfile.write("#PBS -o {}logs/\n".format(args.results_dir))
    pbsfile.write("#PBS -e {}logs/\n".format(args.results_dir))
    pbsfile.write("#PBS -m a\n")
    pbsfile.write("#PBS -N rvic_grid{}\n".format(proc))
    
    pbsfile.write("cd $TMPDIR\n")
    pbsfile.write("mkdir rvic_output\n")
    write_newline(pbsfile)
        
    write_progress("Copying files to $TMPDIR", pbsfile)
    write_file_copy(args.baseflow, "$TMPDIR", pbsfile)
    write_file_copy(args.domain, "$TMPDIR", pbsfile)
    write_file_copy(args.parameters, "$TMPDIR", pbsfile)
    write_file_copy(args.unit_hydrograph, "$TMPDIR", pbsfile)
    write_newline(pbsfile)
    
    # each point gets its own config files and RVIC run.
    # RVIC is theoretically able to do multiple points at once,
    # but I can't get that to work.
    # however, since copying the files takes so long (about as long
    # as generating results), doing multiple points for each file
    # copy makes sense.
    for pt in all_processes[proc]:

        write_progress("Generating RVIC configuration files for point {}".format(point), pbsfile)
        ppoints = ["lons,lats,name"]
        ppoints.append(pt)
        write_create_file("pour_points{}.txt".format(point), ppoints, pbsfile)
        
        # Now generate the config files. There are two: one for generating the
        # impulse response functions, the other for actually doing the routing.
        # There's no non-awkward way to do this.
    
        case_dir = "$TMPDIR/rvic_output"
        caseid = "{}_{}_{}_process{}_point{}".format(model, experiment, run, proc, point)
        casestr = "{}+{}+{}".format(model, experiment, run)
        
        # RVIC names the output impulse response file with the date it
        # is generated. We can't control the name of this file, which is
        # annoying when calculating streamflow with the queue, since you 
        # don't know in advance which day the script will be run, and you need
        # to pass its filename to the convolution calculations.
        # This shell command outputs the current date in the format rvic uses
        # in filenames. It's still possible for this to go wrong,
        # like if file starts generating before midnight, and finishes
        # after midnight or something, but it works almost all the time.
        # Make sure you end up with the number of streamflow files you
        # expect, just in case.
        # (It's 7845 for the peace watershed. Consider a quick ls | wc -l 
        # before starting the assembler script.)
        today = "$(date +%Y%m%d)"
    
        
        # These configuration options are used by both files:
        
        #general options
        shared_options_cfg = {
            "log_level": "INFO",
            "verbose": True,
            "case_dir": case_dir,
            "caseid": caseid
            }
        
        #options relating to the watershed domain file
        domain_cfg = {
            "file_name": "$TMPDIR/{}".format(file_basename(args.domain)),
            "longitude_var": "lon",
            "latitude_var": "lat",
            "land_mask_var": "mask",
            "fraction_var": "frac",
            "area_var": "area"
            }

        
        # these configuration options are for the impulse response calculations
        param_options_cfg = {
            "clean": True,
            "gridid": watershed,
            "temp_dir": "$TMPDIR",
            "remap": False,
            "aggregate": False,
            "agg_pad": 25,
            "netcdf_format": "NETCDF4",
            "netcdf_zlib": "False",
            "netcdf_complevel": 4,
            "netcdf_sigfigs": None,
            "subset_days": "",
            "constrain_fractions": False,
            "search_for_channel": False
            }
        param_options_cfg.update(shared_options_cfg)

        
        #pour points file, created previously
        pour_points_cfg = { "file_name": "$TMPDIR/pour_points{}.txt".format(point)}
        
        uh_box_cfg = {
            "file_name": "$TMPDIR/{}".format(file_basename(args.unit_hydrograph)),
            "header_lines": 1
            }

        routing_cfg = {
            "file_name": "$TMPDIR/{}".format(file_basename(args.parameters)),
            "longitude_var": "lon",
            "latitude_var": "lat",
            "flow_distance_var": "Flow_Distance",
            "flow_direction_var": "Flow_Direction",
            "basin_id_var": "Basin_ID",
            "velocity": "velocity",
            "diffusion": "diffusion",
            "output_interval": 86400,
            "basin_flowdays": 100,
            "cell_flowdays": 4,
            }
        parameter_config = {}
        parameter_config["options"] = param_options_cfg
        parameter_config["pour_points"] = pour_points_cfg
        parameter_config["uh_box"] = uh_box_cfg
        parameter_config["routing"] = routing_cfg
        parameter_config["domain"] = domain_cfg
        
        write_create_file("$TMPDIR/params{}.cfg".format(point), multidict_to_config(parameter_config), pbsfile)
        
        #these configruation options are for the convolution calculation configuration
        conv_options_cfg = {
            "rvic_tag": "1.1.1",
            "casestr": casestr,
            "calendar": calendar,
            "run_type": "drystart",
            "run_startdate": startdate.strftime("%Y-%m-%d-%H"),
            "stop_option": "date",
            "stop_n": -999,
            "stop_date": enddate.strftime("%Y-%m-%d"),
            "rest_option": "date",
            "rest_n": -999,
            "rest_date": enddate.strftime("%Y-%m-%d"),
            "rest_ncform": "NETCDF4",
            }
        conv_options_cfg.update(shared_options_cfg)
        
        history_cfg = {
            "rvichist_ntapes": 1,
            "rvichist_mfilt": 100000,
            "rvichist_ndens": 1,
            "rvichist_nhtfrq": 1,
            "rvichist_avgflag": "A",
            "rvichist_outtype": "array",
            "rvichist_ncform": "NETCDF4",
            "rvichist_units": "m3/s"
            }
        
        initial_state_cfg = {"file_name": None}
        
        param_filename = "{}/params/{}.rvic.prm.{}.{}.nc".format(case_dir, 
                                                                     caseid,
                                                                     watershed,
                                                                     today)
        param_file_cfg = {"file_name": param_filename}
        
        input_forcings_cfg = {
            "datl_path": "$TMPDIR",
            "datl_file": file_basename(args.baseflow),
            "time_var": "time",
            "latitude_var": "lat",
            "datl_liq_flds": "RUNOFF, BASEFLOW",
            "start": None,
            "end": None
            }
        convolution_config={}
        convolution_config["options"] = conv_options_cfg
        convolution_config["history"] = history_cfg
        convolution_config["domain"] = domain_cfg
        convolution_config["initial_state"] = initial_state_cfg
        convolution_config["param_file"] = param_file_cfg
        convolution_config["input_forcings"] = input_forcings_cfg
        
        write_create_file("$TMPDIR/convolve{}.cfg".format(point), multidict_to_config(convolution_config), pbsfile)

        write_newline(pbsfile)
        write_progress("Running RVIC for point {}".format(point), pbsfile)
        pbsfile.write("source {}".format(environment))
        write_progress("Generating impulse response functions", pbsfile)
        pbsfile.write("rvic parameters $TMPDIR/params{}.cfg".format(point))
        write_progress("Routing streamflow", pbsfile)
        pbsfile.write("rvic convolution $TMPDIR/convolve{}.cfg".format(point))

        write_progress("Saving results", pbsfile)
    
        casestr_subst = casestr.replace('+', '_')
        enddate_incremented = enddate + datetime.timedelta(days=1)
        resultfile = "{}/{}/{}.rvic.h0a.{}.nc".format(case_dir, "hist", caseid, 
                                                  enddate_incremented.strftime("%Y-%m-%d"))
        write_file_copy(resultfile, args.results_dir, pbsfile)
    
        point = point + 1
    
    write_progress("Process completed.", pbsfile)
    pbsfile.close()

domain.close()
baseflow.close()
parameters.close()
