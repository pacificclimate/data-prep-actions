# Ensemble Mean calculator

This script accepts a directory and a CSV file. The CSV file should be a list of model-run pairs to include in the ensemble mean. So far there are two ensemble lists - PCIC12, and the Hydrology ensemble.

The script scans every file in the directory and reads its metadata attributes. If the model and run match one included in the CSV file, the script assigns the file to a group based on its experiment, variable, frequency, method, and timespan.

After all files in the directory have been scanned, the script checks each resulting group. For any group that ended up with the same number of files as there are specified model/run pairs, the cdo ensmean command will be run to generate a file containing the ensemble mean of the input files.

It does not adjust the metadata of the resulting dataset. Yaml file intended as input to `update_metadata` to sets the "model" metadata attributes of the PCIC12 and Hydrology ensembles are included.

To calculate the mean of some other ensemble, you can just make a new CSV file listing the models and runs that should be included.

## A note on metadata attributes and updates

The PCIC metadata standard, as documented in Confluence, is process-oriented. A datafile is originally output from a GCM with a certain set of metadata attributes describing the GCM process. When another process, such as downscaling, is applied to the data, those original set of metadata attributes are preserved with the GCM__ prefix, and an additional set of metadata attributes describing the downscaling process are added to the file. 

This is because some information is the same for all processes, such as contact information for the person who worked on it - we want to preserve information from every step of data processing, and adding the prefixes means that new attributes never overwrite old ones.

However, this means that if you want to know the name of the GCM that output the file, the attribute storing this data will depend on what other processes the file has been through. If the file was freshly output from a GCM, the name will be in the attribute `model_id`. If the data has been output from a GCM, then downscaled, the name of the GCM will be stored in `GCM__model_id`; if the data has been output from a GCM, then downscaled and then used for hydrological modeling, it will be called `downscaling__GCM__model_id`; if the data has been output from a GCM, downscaled, then used for hydrological modeling, then that hydrological output has been routed, it will be called `hydromodel__downscaling__GCM__model_id`. Each additional process adds a new prefix.

Using this script averages several GCMs together, so after using it, you will want to update the name of the GCM (as well as the realization, institution, and institute_id) to the whatever the name of the ensemble is, but you will need to understand PCIC's metadata model and which processes your file has been through to know the name of the attribute you need to update.

This means the sample update yaml files provided may not be correct for your use case, even if you are creating the same ensemble, if the yaml samples were written for the wrong "level". The PCIC12 update file is for downscaled data; the hydrology ensemble update file is for routed streamflow. You may need to write another.

## Virtual Environment

You will need a python 3 virtual environment with `netcdf4` and `cdo` installed.