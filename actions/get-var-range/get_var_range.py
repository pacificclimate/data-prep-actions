from argparse import ArgumentParser
from nchelpers import CFDataset

parser = ArgumentParser(description='Get min/max values of variable in netCDF file')
parser.add_argument("-f", "--file")
parser.add_argument("-v", "--variable")
args = parser.parse_args()

with CFDataset(args.file) as cf:
    print(cf.var_range(args.variable))
