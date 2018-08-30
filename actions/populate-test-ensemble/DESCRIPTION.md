# Populate a Test Ensemble

## Purpose
The text file in this directory contains a reasonably-short list of files that can be used to exercise all climate explorer frontend functionality (as of August 29, 2018). It is intended to make setting up a complete-enough test database easier. This file list contains:

Multiyear Mean files:
* Two models (CanESM2 and CNRM-CM5) for the Model Context Graph
* Three emissions scenarios to test switching between scenarios
* Two variables (tasmax, tasmin) for the variable response and comparison graphs
* Three resolutions for the Annual Cycle graph
* Six climatologies for each model/scenario/variable set to test the Future Anomaly graph, the long term average graph, and the stats table

Non-MYM files:
* Two models, CanESM2 and CNRM-CM5
* Two variables, rx1day and rx5day, for the Variable Response Graph and Timeseries graph
* Three emissions scenarios

228 files total. It does not contain any known bad data, overlapping MYM and non-MYM data for the same dataset, files that should be ignored, or geographical subset files, so it isn't a good test of known problems or issues.


## How to Create the Test Ensemble
The text file can be used to provide arguments to any script that normally operates on a list of files. 

Add the test files to the database (assuming you have put the text file in the top level modelmeta directory):

```
python scripts/index_netcdf -d [YOUR DATABASE] $(cat testensemble.txt)
```

Create a new ensemble to put the files in, then add them with:

```
python scripts/associate_ensemble -d [YOUR DATABASE] -n [YOUR ENSEMBLE] -v 1 $(cat testensemble.txt)
```