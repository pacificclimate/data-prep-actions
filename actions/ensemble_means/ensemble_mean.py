'''This script reads a list of models and runs from a csv file.
Then it opens every file in the data directory, and if the file matches a
model and run from the csv, puts it in a group based on its variable, domain,
frequency, experiment, method, and start and end years.
After scanning all the files in the data directory and sorting them into groups,
it uses CDO's ensmean command to generate an average file for any "complete" group
(a group that contains a file for each model/run in the CSV).
it does not update metadata; you'll have to do that seperately.'''
import os
from netCDF4 import Dataset
import re
from cdo import Cdo
import argparse
from csv import DictReader

cdo = Cdo()
parser = argparse.ArgumentParser('Run cdo ensmean on matched sets of climatologies')
parser.add_argument('ensemble_spec', help='a csV file listing models and runs to include')
parser.add_argument('ensemble_name', help='string to use as the name of the ensemble in filenames')
parser.add_argument('indir', metavar='indir', help='a directory containing matching climatologies')
parser.add_argument('outdir', metavar='outdir', help='directory to output ensemble means to')
args = parser.parse_args()

indir = args.indir.rstrip('/')
outdir = args.outdir.rstrip('/')

print("Reading ensemble specification")
ensemble_spec = []
with open(args.ensemble_spec) as csvfile:
    reader = DictReader(csvfile)
    for row in reader:
        ensemble_spec.append(row)
        
print(ensemble_spec)

ensembles = {}
print("Scanning data files...")

#PCIC's metadata system adds a new prefix to metadata attributes when
#the model described by those attributes is used as input to another
#model. We need to determine what the prefixes are.
gcm_prefix = None
ds_prefix = None

def find_attribute_prefix(attributes, final):
    #returns the prefix of an attribute that ends with final
    for att in attributes:
        match = re.match("^([a-zA-Z_]*)"+final, att)
        if match:
            return match.group(1)

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
    domain = None

    
    for v in nc.variables:
        if v not in ["time", "time_bnds", "lon", "lat", "climatology_bnds"]:
            variable = v
    
    globals = nc.__dict__
    gcm_prefix = find_attribute_prefix(globals, "experiment_id") if not gcm_prefix else gcm_prefix
    ds_prefix = find_attribute_prefix(globals, "method_id") if not ds_prefix else ds_prefix
    
    
    frequency = globals["frequency"]
    domain = globals["domain"]

    method = globals["{}method_id".format(ds_prefix)]

    
    
    experiment = globals["{}experiment_id".format(gcm_prefix)]
    experiment = experiment.replace(",", "+") if experiment else None
    experiment = experiment.replace(" ", "") if experiment else None
    
    model = globals["{}model_id".format(gcm_prefix)]
    run = "r{}i{}p{}".format(globals["{}realization".format(gcm_prefix)],
                                         globals["{}initialization_method".format(gcm_prefix)],
                                         globals["{}physics_version".format(gcm_prefix)])
                                         
    include_model = None
    for model_run in ensemble_spec:
        if model == model_run["model"] and run == model_run["run"]:
            include_model = True
            
    if not include_model:
        print("  WARNING: Unexpected model-run combination found: {} {}".format(model, run))
    
    startmatch = re.match(r'^(\d\d\d\d)-01-01T00:00:00Z$', globals["climo_start_time"])
    if(startmatch):
        startyear = startmatch.group(1) + "0101"
    
    # end match will accept either December 30 or December 31 - HadGEM uses a
    # 360 day calendar.
    endmatch = re.match(r'^(\d\d\d\d)-12-3\dT00:00:00Z$', globals["climo_end_time"])
    if(endmatch):
        endyear = endmatch.group(1) + "1231"   
    
    if variable and frequency and experiment and method and startyear and endyear and include_model:
        ensemble = "{}_{}_{}_{}_{}_rXi1p1_{}-{}_{}".format(variable, frequency, method,
                                                            args.ensemble_name, experiment, 
                                                            startyear, endyear, domain)
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
    if len(files) == len(ensemble_spec):
        print("Generating {}".format(e))
        cdo.ensmean(input=['{}/{}'.format(indir, f) for f in files], 
                    output='{}/{}.nc'.format(outdir, e))
    else:
        print("WARNING: {} has only {} files, skipping ensemble value".format(e, len(files)))
        for f in files:
            print("  {}".format(f))