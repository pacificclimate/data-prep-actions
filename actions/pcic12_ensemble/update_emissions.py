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
for infile in os.listdir(indir):
    with CFDataset(indir + infile, mode="r+") as cf:
        if cf.GCM__experiment.startswith("ssp"):
            cf.GCM__experiment = "historical," + cf.GCM__experiment
            cf.GCM__experiment_id = "historical," + cf.GCM__experiment_id
