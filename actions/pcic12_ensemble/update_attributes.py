from nchelpers import CFDataset
from argparse import ArgumentParser
from datetime import datetime
import os

parser = ArgumentParser()
parser.add_argument('indir', metavar='indir', help='directory containing files on which to update attributes')

args = parser.parse_args()

indir = args.indir

#clim_vars = ["pr", "rain", "snow", "tas", "tasmax", "tasmin"]
#clim_vars = ["rl10pr", "rl20pr", "rl25pr", "rl30pr", "rl50pr", "rl5pr", "rl10tasmax", "rl20tasmax", "rl25tasmax", "rl30tasmax", "rl5tasmax", "rl10tasmin", "rl20tasmin", "rl25tasmin", "rl30tasmin", "rl5tasmin"]
clim_vars = {"tasmax": "rl50tasmax", "tasmin": "rl50tasmin"}
for infile in os.listdir(indir):
    with CFDataset(indir + infile, mode="r+") as cf:
        clim_var = clim_vars[infile.split("_")[0]]
        cf.variables[clim_var].cell_methods += " models: mean over ensemble"
        cf.variables["climatology_bnds"].calendar = cf.time_var.calendar
        cf.variables["climatology_bnds"].units = cf.time_var.units

        delattr(cf, "GCM__grid")
        delattr(cf, "GCM__grid_label")
        delattr(cf, "GCM__further_url_info")
        delattr(cf, "GCM__source_type")
        delattr(cf, "GCM__branch_method")
        delattr(cf, "GCM__data_specs_version")
        delattr(cf, "GCM__nominal_resolution")

        cf.creation_date = datetime.fromtimestamp(os.path.getctime(indir + infile)).strftime("%Y-%m-%dT%H:%M:%SPST")
        cf.Description = "CanDCS-M6 PCIC12-CMIP6 Ensemble Average Climatology"
        cf.GCM__institution = "Pacific Climate Impacts Consortium"
        cf.GCM__institution_id = "PCIC"
        cf.GCM__model_id = "PCIC12"
        cf.GCM__models = "CMIP6 PCIC12: BCC-CSM2-MR, NorESM2-LM, UKESM1-0-LL, MRI-ESM2-0, MPI-ESM1-2-HR, EC-Earth3-Veg, MIROC-ES2L, INM-CM5-0, CMCC-ESM2, FGOALS-g3, TaiESM1, IPSL-CM6A-LR"
        cf.GCM__source_id = "PCIC12"
        cf.GCM__forcing_index = "X"
