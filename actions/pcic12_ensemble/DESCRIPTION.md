# PCIC12 Ensemble

This primitive script scans every file in a directory and reads the metadata attributes. If a file's model metadata attribute is recognized as belonging to one of the PCIC12 models, it uses other metadata attributes to assign the file to a group based on its experiment, variable, frequency, method, and timespan.

After all files in the directory have been scanned, the script checks each resulting group. For any group that ended up with 12 files corresponding to the 12 models in the PCIC ensemble, the cdo ensmean command will be run to generate a file containing the ensemble mean of the input files.

CAUTION: There are some things it doesn't verify. It is intended that the files in the input folder will be pre-selected in a process that handles some of the missing verification, such as by populating the input folder with the results of a query run on the metadata database. You may want to edit it to fix the following gaps if your collection of input data isn't pre-vetted.

* It doesn't check to make sure that the twelve models in a set are actually all different - you could, for example, have two CanESM2 datasets and no HadGEM2-ES datasets, and as long as they had the same variable, experiment, frequency, method, and timespan, the set would be erroneously considered complete.

* It doesn't check to make sure files share a spatial extent. I think cdo would complain if they didn't, but I'm not sure.

* It assumes it is working with downscaled GCM data, and the metadata formatting that implies

It does not adjust the metadata of the resulting dataset. A yaml file intended as input to `update_metadata` to sets the "model" metadata attributes of the generated PCIC12 file is included.