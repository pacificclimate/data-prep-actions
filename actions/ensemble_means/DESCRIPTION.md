# Ensemble Mean calculator

This script accepts a directory and a CSV file. The CSV file should be a list of model-run pairs to include in the ensemble mean. So far there are two ensemble lists - PCIC12, and the Hydrology ensemble.

The script scans every file in the directory and reads its metadata attributes. If the model and run match one included in the CSV file, the script assigns the file to a group based on its experiment, variable, frequency, method, and timespan.

After all files in the directory have been scanned, the script checks each resulting group. For any group that ended up with the same number of files as there are specified model/run pairs, the cdo ensmean command will be run to generate a file containing the ensemble mean of the input files.

It does not adjust the metadata of the resulting dataset. A yaml file intended as input to `update_metadata` to sets the "model" metadata attributes of the generated PCIC12 file is included.

## Virtual Environment

You will need a python 3 virtual environment with `netcdf4` and `cdo` installed.