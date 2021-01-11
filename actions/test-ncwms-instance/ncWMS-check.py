'''This script checks that an ncWMS instance is able to serve every file in a
specific ensemble in a PCIC modelmeta database.'''

import sys
import os
import requests
import xmltodict
import collections
from argparse import ArgumentParser



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modelmeta import DataFile, DataFileVariable, Ensemble
from modelmeta import EnsembleDataFileVariables

parser = ArgumentParser()
parser.add_argument('-d', '--dsn', 
                    help="PostgreSQL connection string of the form " + 
                    "postgresql://user:password@host:port/database")
parser.add_argument('-s', '--ncwms',
                    help="ncWMS base url of the form https://example.org/dir/ncwms")
parser.add_argument('-v', '--version', type=int, default=1, choices=[1,2],
                    help="ncWMS version format")
parser.add_argument('-p', '--prefix', help="prefix to use (iff a dynamic ncWMS instance)")
parser.add_argument('ensemble', help="name of data ensemble to check")


args = parser.parse_args()

def parse_ncWMS_exception(xml):
    '''if ncWMS has returned an error message, extract it'''
    try:
        ed = xmltodict.parse(xml)
        if 'ServiceExceptionReport' in ed and 'ServiceException' in ed['ServiceExceptionReport']:
            return ed['ServiceExceptionReport']['ServiceException']
        return None
    except:
        raise("ncWMS did not return an XML response. Check your ncWMS URL")
        

# connect to the database
engine = create_engine(args.dsn)
Session = sessionmaker(bind=engine)
sesh = Session()

# get list of all variables in the ensemble
query = sesh.query(DataFileVariable).join(EnsembleDataFileVariables, Ensemble).filter(Ensemble.name == args.ensemble)
vars = [(
        dfv.file.unique_id,
        dfv.file.filename,
        dfv.netcdf_variable_name,
        dfv.range_min,
        dfv.range_max,
        dfv.variable_alias.standard_name
    ) for dfv in query.all()]

files = 0
errors = 0
error_files = set()

for unique_id, filename, var_name, range_min, range_max, variable_standard_name in vars:
    # for a dynamic dataset, maps are called via a prefix and the filepath
    # for a static dataset, maps are called via unique_id.
    identification = "{}{}".format(args.prefix, filename) if args.prefix else unique_id
    style = "boxfill/default" if args.version == 1 else "default"
    
    
    print("Now checking {}".format(identification))
    
    # make a GetCapabilities query on this dataset
    gc_params = {
        "REQUEST": "GetCapabilities",
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "DATASET": identification,
        }
    response = requests.get('{}'.format(args.ncwms), params=gc_params)
    
    if response.status_code != 200:
        error = parse_ncWMS_exception(response.content)
        print("  ERROR: GetCapabilities returned {} ({})".format(response.status_code, 
                                                        error if error else "unable to parse error"))
        errors += 1
        error_files.add(identification)
    else:
        print("  GetCapabilites call OK")
        
        
        # extract spatial and temporal extent from xml returned by GetCapabilities
        # we'll need this for the other queries
        cap_metadata = xmltodict.parse(response.content)
        layers = cap_metadata['WMT_MS_Capabilities']['Capability']['Layer']['Layer']['Layer']
        if isinstance(layers, collections.OrderedDict):
            # this dataset contains only one layer
            layer_metadata = layers
        elif isinstance(layers, list):
            # there are multiple layers corresponding to different variables in this file.
            # we could go through each layer seeking the one that has the current
            # variable name on it, but we don't actually care -- netCDF's data schema
            # requires that *all* variables in a file share spatial and temporal dimensions,
            # so *any* layer in the file will provide the extent metadata we need. 
            # Use the 0th one.
            layer_metadata = layers[0]
        else:
            print("  ERROR: cannot parse GetCapabilities response")
            errors += 1
            error_files.add(identification)
            continue
        
    
    
        #get spatial info: bounding box and SRS
        bounding_box = layer_metadata['BoundingBox']
        srs = bounding_box['@SRS']
        minx = bounding_box['@minx']
        miny = bounding_box['@miny']
        maxx = bounding_box['@maxx']
        maxy = bounding_box['@maxy']
        bbox = "{},{},{},{}".format(minx, miny, maxx, maxy)
    
        # get a valid timestamp
        default_timestamp = layer_metadata["Extent"]["@default"]
    
        # make a GetFeatureInfo query on this dataset
        # build the query
        gfi_params = {
            "REQUEST": "GetFeatureInfo",
            "SERVICE": "WMS",
            "VERSION": "1.1.1",
            "QUERY_LAYERS": "{}/{}".format(identification, var_name),
            "LAYERS": "{}/{}".format(identification, var_name),
            "WIDTH": 100,
            "HEIGHT": 100,
            "SRS": srs,
            "BBOX": bbox,
            "INFO_FORMAT": "text/xml",
            "X": 50,
            "Y": 50
            }
    
        response = requests.get('{}'.format(args.ncwms), params=gfi_params)
        if response.status_code == 200:
            print("  GetFeatureInfo call OK")
        else:
            error = parse_ncWMS_exception(response.content)
            print("  ERROR: GetFeatureInfo returned {} ({})".format(response.status_code, 
                                                        error if error else "unable to parse error"))
            errors += 1
            error_files.add(identification)
        
        # make a GetMap query on this dataset
        gm_params = {
            "REQUEST": "GetMap",
            "SERVICE": "WMS",
            "VERSION": "1.1.1",
            "LAYERS": "{}/{}".format(identification, var_name),
            "TRANSPARENT": "true",
            "STYLES": style,
            "NUMCOLORBANDS": 254,
            "SRS": srs,
            "LOGSCALE": "false",
            "FORMAT": "image/png",
            "BBOX": bbox,
            "WIDTH": 100,
            "HEIGHT": 100,
            "COLORSCALERANGE": "{},{}".format(range_min, range_max),
            "TIME": default_timestamp
            }

        response = requests.get('{}'.format(args.ncwms), params=gm_params)
        if response.status_code == 200:
            print("  GetMap call OK")
        else:
            error = parse_ncWMS_exception(response.content)
            print("  ERROR: GetMap returned {} ({})".format(response.status_code, 
                                                        error if error else "unable to parse error"))
            errors += 1
            error_files.add(identification)
        
    files += 1



print("----------------------------------------------------")
print("FILE SUMMARY: checked {} files, {} errors found".format(files, errors))
if errors > 0:
    print("Files with errors:")
    for f in error_files:
        print("  {}".format(f))
        
# GetLegendGraphic, as used by the PDP, does not specify a dataset, so we need
# only test it once per server.   
glg_params = {
    "REQUEST": "GetLegendGraphic",
    "COLORBARONLY": "true",
    "WIDTH": 1,
    "HEIGHT": 300,
    "NUMCOLORBANDS": 254,
    "PALETTE": "default"
    }
    
response = requests.get('{}'.format(args.ncwms), params=glg_params)
if response.status_code == 200:
    print("\nGetLegendGraphic call OK")
else:
    print("ERROR: GetLegendGraphic returned {}".format(response.status_code))
