'''This primitive one-off script opens every file in a directory and reads
the metadata attributes, which it uses to group files by experiment, variable,
frequency, method, and climatology period. 
If any of the resulting groups contain twelve files, it will output an
ensemble mean using the cdo ensmean command.
This is intended to generate the PCIC12 ensemble means, assuming all
required climatologies (and no additional climatologies) are present - 
you'll need to make a directory containing all the needed climatologies.
It does not do any metadata updates; you'll have to do that separately.'''
import os
from netCDF4 import Dataset
import re
from cdo import Cdo
import argparse

cdo = Cdo()
parser = argparse.ArgumentParser('Run cdo ensmean on matched sets of 12 climatologies')
parser.add_argument('indir', metavar='indir', help='a directory containing matching climatologies')
parser.add_argument('outdir', metavar='outdir', help='directory to output ensemble means to')
args = parser.parse_args()

indir = args.indir.rstrip('/')
outdir = args.outdir.rstrip('/')

ensembles = {}
print("Parsing input files...")

for file in os.listdir(indir):
    print("Checking {}".format(file))
    # check metadata in each file, see what group it belongs to.
    nc = Dataset("{}/{}".format(indir, file), "r")
    variable = None
    frequency = None
    experiment = None
    method = None
    startyear = None
    endyear = None
    model = None
    
    for v in nc.variables:
        if v not in ["time", "time_bnds", "lon", "lat", "climatology_bnds"]:
            variable = v
    
    globals = nc.__dict__
    frequency = globals["frequency"]
    method = globals["method_id"]
    resolutions = {"aClimMean": "annual", "mClimMean": "monthly", "sClimMean": "seasonal"}    
    res = resolutions[frequency] if frequency else None

    experiment = globals["GCM__experiment_id"]
    experiment = experiment.replace(",", "+") if experiment else None
    experiment = experiment.replace(" ", "") if experiment else None
    experiment = experiment.split("+")[1] if experiment else None
    
    PCIC12_models = {
        "BCC-CSM2-MR": "r1i1p1f1",
        "NorESM2-LM": "r1i1p1f1",
        "MIROC-ES2L": "r1i1p1f2",
        "MPI-ESM1-2-HR": "r1i1p1f1",
        "MRI-ESM2-0": "r1i1p1f1",
        "UKESM1-0-LL": "r1i1p1f2",
        "EC-Earth3-Veg": "r1i1p1f1",
        "CMCC-ESM2": "r1i1p1f1",
        "INM-CM5-0": "r1i1p1f1",
        "FGOALS-g3": "r1i1p1f1",
        "TaiESM1": "r1i1p1f1",
        "IPSL-CM6A-LR": "r1i1p1f1",
        }
    model = globals["GCM__model_id"]
    ensemble_member = "r{}i{}p{}f{}".format(globals["GCM__realization_index"],
                                         globals["GCM__initialization_index"],
                                         globals["GCM__physics_index"],
                                         globals["GCM__forcing_index"])
    if model not in PCIC12_models:
        print("  WARNING: Unexpected model found: {}".format(model))
        model = None
    elif ensemble_member != PCIC12_models[model]:
        print("  WARNING: Non-PCIC12 run found: {}".format(ensemble_member))
        model = None
    
    startmatch = re.match(r'^(\d\d\d\d)-01-01T00:00:00Z$', globals["climo_start_time"])
    if(startmatch):
        startyear = startmatch.group(1)
    
    # end match will accept either December 30 or December 31 - HadGEM uses a
    # 360 day calendar.
    endmatch = re.match(r'^(\d\d\d\d)-12-3\dT00:00:00Z$', globals["climo_end_time"])
    if(endmatch):
        endyear = endmatch.group(1)  
    
    if variable and res and experiment and method and startyear and endyear and model:
        #if variable in ["tas", "tasmax", "tasmin"] and res == "annual":
        #    res_fname = "average_annual"
        #else:
        #    res_fname = "{}_average".format(res)
        #ensemble = "{}_{}_climatology_{}+PCIC-Blend_PCIC12_Ensemble_Average_{}_{}-{}".format(variable, res, method,
        #                                                    experiment, startyear, endyear)
        ensemble = file.replace(model, "PCIC12_Ensemble_Average")
        ensemble = ensemble.replace(ensemble_member + "_", "")
        ensemble = ensemble.replace(".nc", "")
        if ensemble in ensembles:
            l = ensembles[ensemble]
            l.append(file)
            ensembles[ensemble] = l
        else:
            ensembles[ensemble] = [file]
    else:
        print("  WARNING: {} is missing some metadata".format(file))
        if not variable:
            print("    Variable cannot be determined")
        if not frequency:
            print("    Frequency cannot be determined")
        if not experiment:
            print("    Experiment cannot be determined")
        if not method:
            print("    Method cannot be determined")
        if not startyear:
            print("    Start year cannot be determined")
        if not endyear:
            print("    End year cannot be determined")
    nc.close()

print("Generating outputs...")
for e in ensembles:
    files = ensembles[e]
    if len(files) == 12:
        print("Generating {}".format(e))
        cdo.ensmean(input=['{}/{}'.format(indir, f) for f in files], 
                    output='{}/{}.nc'.format(outdir, e))
    else:
        print("WARNING: {} has only {} files, skipping ensemble value".format(e, len(files)))
        for f in files:
            print("  {}".format(f))
