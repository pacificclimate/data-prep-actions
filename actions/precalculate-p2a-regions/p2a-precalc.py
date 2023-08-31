''' This script precalculates values needed by p2a. It has constant lists of
regions, variables, models, and emissions scenarios. For each
region, it outputs a CSV file where each row represents a single call to the
stats API endpoint for a particular dataset, region, and timestamp. Some of
the columns specify which dataset is called; the others contain the results.

These columns describe the dataset from which the data was calculated
    'unique_id': unique_id of the dataset 
    'model': GCM that generated the dataset 
    'scenario': emissions scenario 
    'climatology': a standard climatology year: 2020, 2050, or 2080 
    'start_date': actual start date of the dataset 
    'end_date': actual end date of the datatset 
    'variable': variable name
    'region': name of the region (also present in filename) 
    'timescale': monthly, yearly, or seasonal
    'timeidx': timestep: 0 for annual, 0-3 for seasonal, 0-11 for monthly 
    'op': mean or stdev - corresponds to cell methods for the dataset
    'modtime': when the dataset was last indexed - used to check if 
                precalculated data is outdated

These columns contain the results of a call to ce.api.stats() for the dataset in
question:
    'min': the minimum value in this region at this timestamp
    'max': the maximum value in this region at this timestamp
    'mean': the mean value in this region at this timestamp
    'median': the median value in this region at this timestamp
    'stdev',: the standard deviation of values in this region at this timestamp 
    'ncells': number of cells in the region
    'units': units the data is in
    
This column describes the calculation:
    'access_time' : when this script was run.
    
This script is intended to be run on the queue - therefore, while it has a
dictionary to allow it to parse any of several input regions, only one is
calculated at a time. 

It takes three metadata files: 

* a JSON dataset metadata file, the output of the PCEX multimeta query
* a CSV region metadata file, output from the geoserver
* a CSV region name file, created for this script
'''

import csv
import requests
import json
import argparse
from datetime import date
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ce.api.stats import stats
from ce.api.metadata import metadata

parser=argparse.ArgumentParser("Precalculate selected regional variables and output into a CSV")
parser.add_argument('-n', '--names', help='a csv matching region names with geoserver names')
parser.add_argument('-p', '--polygons', help='a csv describing regions from a geoserver')
parser.add_argument('-m', '--multimeta', help='dataset metadata obtained from PCEX /multimeta')
parser.add_argument('-r', '--region', help='the region to precalculate')
parser.add_argument('-t', '--tasmean', help='calculate tasmean from tasmin and tasmax',
                    action='store_const', const=True, default=False)
parser.add_argument('-f', '--ffd', help='calculate frost free days from frost days', 
                    action='store_const', const=True, default=False)
parser.add_argument('-b', '--baseline', default=False, help='YYYY,model include a historical baseline')
parser.add_argument('-d', '--dsn', help='connection string for a modelmeta database')

args = parser.parse_args()

# these are the variables plan2adapt needs
variables = ['tasmean', 'ffd', 'pr', 'prsn', 'gdd', 'hdd', 'cdd']

standard_climo_years = {
    "6190": (1961, 1990),
    "7100": (1971, 2000),
    "8110": (1981, 2010),
    "2020": (2010, 2039),
    "2050": (2040, 2069),
    "2080": (2070, 2099)
    }

# PCIC12 models
models = [
    "ACCESS1-0",
    "CanESM2",
    "CCSM4",
    "CNRM-CM5",
    "CSIRO-Mk3-6-0",
    "GFDL-ESM2G",
    "HadGEM2-CC",
    "HadGEM2-ES",
    "inmcm4",
    "MIROC5",
    "MPI-ESM-LR",
    "MRI-CGCM3",
    ]

#all scenarios
scenarios = ['historical, rcp85', 'historical,rcp85',
             'historical, rcp45', 'historical,rcp45',
             'historical, rcp26', 'historical,rcp26',
             ]
climatologies = [2020, 2050, 2080]

Session = sessionmaker(create_engine(args.dsn))
sesh = Session()

if args.tasmean:
    if "tasmin" not in variables or "tasmax" not in variables:
        raise Exception("Cannot calculate tasmean without tasmin and tasmax")
    else:
        tasmean_data = {"tasmax": [], "tasmin": []}

if args.ffd:
    if 'fdETCCDI' not in variables:
        raise Exception("Cannot calculate ffd without fdETCCDI")
    else:
        ffd_data = []
        
if args.baseline:
    # this argument allows precalculation of data to serve as a historical
    # baseline - one single model, one single time period - seperately from
    # the other specified time periods.
    baseline_datasets = 0
    baseline_clim = standard_climo_years[args.baseline.split(',')[0]]
    baseline_model = args.baseline.split(',')[1]
    print("historical baseline years: {} model: {}".format(baseline_clim, baseline_model))
    
#goes through a csv, returning the row where the attribute matches the value
def find_row_match(csv, att, val):
    for row in csv:
        if row[att] == val:
            return row
    raise Exception("Value not found: {}: {}".format(att, val))


def year_from_timestring(str):
    d = datetime.strptime(str, '%Y-%m-%dT%H:%M:%SZ')
    return d.year

# look up the name of the region 
with open(args.names) as region_names:
    names_csv = csv.DictReader(region_names, quotechar="'")
    geo_region = find_row_match(names_csv, 'parameter', args.region)['english_na']
    
# acquire dataset metadata
with open(args.multimeta) as multimeta:
    datasets = json.load(multimeta)

    #acquire region metadata
    with open(args.polygons) as regions:
        region_csv = csv.DictReader(regions)
        wkt = find_row_match(region_csv, "english_na", geo_region)["the_geom"]

    # fetch the WKT for the region.
    with open('{}.csv'.format(args.region), 'w') as outfile:
        fieldnames = [
            'unique_id', 
            'model', 
            'scenario', 
            'climatology', 
            'start_date', 
            'end_date', 
            'variable',
            'region', 
            'timescale',
            'timeidx',
            'timestamp', 
            'op',
            'modtime',
            'min',
            'max',
            'mean',
            'median',
            'stdev', 
            'ncells',
            'units',
            'access_time'
            ]
        outcsv = csv.DictWriter(outfile, fieldnames)
        outcsv.writeheader()
        
        files = 0
        rows = 0
        
        for ds_id in datasets:
            ds = datasets[ds_id]
            
            # There are two separate sets of filters for precalculating datasets
            # For projected datasets, they must match the variable, climatology,
            # scenario, models, and scenarios given in the lists at the beginning of
            # the script
            
            #see whether this particular dataset falls within the desired parameters
            valid_var = False
            data_vars = ds["variables"]
            for v in variables:
                if v in data_vars:
                    valid_var = True
                    
            valid_clims = False
            start = year_from_timestring(ds["start_date"])
            end = year_from_timestring(ds["end_date"])
            for c in climatologies:
                if start < c and end > c:
                    climatology = c
                    valid_clims = True
            
            valid_model = ds["model_id"] in models
            
            valid_scen = ds["experiment"] in scenarios
            
            valid_projection = valid_var and valid_clims and valid_model and valid_scen
            
            # optional baseline datasets are only precalculated if the --baseline argument
            # is provided, and must match model and climatology from that argument.
            valid_baseline = False
            if args.baseline:
                valid_baseline = (baseline_clim == (start, end) and
                                ds["model_id"] == baseline_model and
                                ds['experiment'] == "historical" and valid_var)
                if valid_baseline:
                    climatology = args.baseline.split(',')[0]
            
            if valid_projection or valid_baseline:
                timescale = ds["timescale"]
                numsteps = {"monthly": 12, "yearly": 1, "seasonal": 4}[timescale]
                
                #this is really kludgy. Don't extract metadata from filenames!
                op = "stdev" if "ClimSD" in ds_id else "mean"
                
                m = metadata(sesh, ds_id)
            
                for v in data_vars:
                    for i in range(numsteps):
                        s = stats(sesh, ds_id, "{}".format(i), wkt, v)[ds_id]
                        row = {
                            'unique_id': ds_id, 
                            'model': ds["model_id"],
                            'scenario': ds["experiment"],
                            'climatology': climatology, 
                            'start_date': ds["start_date"], 
                            'end_date': ds["end_date"], 
                            'variable': v,
                            'region': args.region,
                            'timescale': timescale,
                            'timeidx': i,
                            'timestamp': m[ds_id]["times"][i],
                            "op": op,
                            "modtime": ds["modtime"],
                            "min": s["min"],
                            'max': s["max"],
                            'mean': s["mean"],
                            'median': s["median"],
                            'stdev': s["stdev"], 
                            'ncells': s["ncells"],
                            'units': s["units"],
                            'access_time': date.today()
                            }
                        # if this data will be used to generate composite variables, save it
                        if args.tasmean and v in ["tasmax", "tasmin"]:
                            tasmean_data[v].append(row)
                        if args.ffd and v == 'fdETCCDI':
                            ffd_data.append(row)

                        outcsv.writerow(row)
                        rows += 1
                files += 1
        print("{}: {} rows from {} files calculated".format(args.region, rows, files))    
    
        #todo : think about ops!
        if args.tasmean:
            #go through collected tasmax and tasmin data, generate new tasmean rows
            tasmeans = 0
            for mx in tasmean_data["tasmax"]:
                matches = 0
                for mn in tasmean_data["tasmin"]:
                    atts_match = True
                    for att in ['model', 'scenario', 'climatology', 'timescale', 'timeidx', 'op']:
                        if mx[att] != mn[att]:
                            atts_match = False
                    if atts_match:
                        last_modified = mx["modtime"] if mx["modtime"] > mn["modtime"] else mn["modtime"]
                        matches += 1
                        tasmean_row = {
                                'unique_id': "null", 
                                'model': mx["model"],
                                'scenario': mx["scenario"],
                                'climatology': mx["climatology"], 
                                'start_date': mx["start_date"], 
                                'end_date': mx["end_date"], 
                                'variable': "tasmean",
                                'region': args.region,
                                'timescale': mx["timescale"],
                                'timeidx': mx["timeidx"],
                                'timestamp': mx["timestamp"],
                                "op": mx["op"],
                                "modtime": last_modified,
                                "min": (mx["min"] + mn["min"]) / 2,
                                'max': (mx["max"] + mn["max"]) / 2,
                                'mean': (mx["mean"] + mn["mean"]) / 2,
                                'median': (mx["median"] + mn["median"]) / 2,
                                'stdev': (mx["stdev"] + mn["stdev"]) / 2, 
                                'ncells': mx["ncells"],
                                'units': mx["units"],
                                'access_time': date.today()
                            }
                        outcsv.writerow(tasmean_row)
                        tasmeans += 1
            
            print("{}: {} tasmean values calculated, {} unmatched".format(args.region, tasmeans,
                                                                          (len(tasmean_data["tasmax"])
                                                                                  + len(tasmean_data["tasmin"]))
                                                                          - tasmeans * 2))    
            if args.ffd:
                #go through collected fdETCCDI data, generate new ffd rows
                ffd_rows = 0
                for d in ffd_data:
                    d["variable"] = "ffd"
                    d["unique_id"] = "null"
                    for v in ['min', 'max', 'mean', 'median']:
                        d[v] = 365 - d[v]
                    outcsv.writerow(d)
                    ffd_rows += 1
            print("{}: {} ffd values calculated".format(args.region, ffd_rows))

    outfile.close()
    
print("done!")
