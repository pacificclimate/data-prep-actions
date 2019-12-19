# Format Vic Gen2 Metadata

The scripts in this repository were used to format netCDF metadata for the vic gen2 dataset, to be displayed on the PDP. They're kludgey and not really intended for reuse.

## Fill Values

When the data was received, every variable had the same float-type fill value. This led to errors - lat, lon, and time are doubles, and the data variable is a short (compressed). Most netCDF tools refuse to interact with a variable with an invalid wrong-type fill value.

`fill-values.sh` removes fill values from lat, lon, and time, and sets the fill value of the main variable to type `short`. It will also convert each file to netCDF4 format, required by the PDP.

It has a hardcoded scratch directory and data input directory.

*CAUTION*: This script overwrites files in the data input directory, which is not ideal, but the files were so large there was nowhere to put them for review.

## Model and Run Metadata

These scripts format a metadata file Hydrology provided for use with CSG tools, and then apply the metadata to the files.

Hydrology provided the file `hydrology_experiments_atw.yaml`, which contains metadata describing all their model+experiment combinations.

The `split_yaml.py` script generates a seperate metadata update yaml for each model+experiment combination, suitable to be used in the `update_metadata` script. It also fixes a formatting error with the run (r1i1p1) metadata and applies the prefix `downscaling__GCM__` to each model-related metadata attribute in accordance with the PCIC metadata standards for Hydrological model data, forced by downscaled GCM data.

Finally, `update-run-metadata.sh` will, when run in the directory containing all the model yamls, apply the right model data to each file. It uses filenames to do this, as there is no model metadata actually in the files (if there were, we wouldn't need these scripts.) It uses the `update_metadata` tool, so must be run in an environment where that tool and its requirements are available.

## Single timestep

The `time-subset.sh` script was used to extract a single timestamp from each file; the goal was to see if ncWMS would function correctly if it had only access to one single timestamp from the file. The answer was "no;" I don't think we'll reuse this script.