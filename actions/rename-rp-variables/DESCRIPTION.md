# Format Return Period Data

The respository contains scripts to process return period data for use in Climate Explorer.

## rename_rp_variables.py

This python script renames variables of the form `rp.[PERIOD]` to `rp[PERIOD][MODEL_OUTPUT]` where `[PERIOD]` is the length of the return period in years, typically 5 or 20, and `[MODEL OUTPUT]` is a variable like tasmin, tasmax, or precipitation.

For example, rp.20 might be renamed rp20tasmax; rp.5 might be renamed rp5pr.

Additionally, the process that generates the return period datasets sometimes generates float-type rp variables with integer fill value attributes. This minor issue doesn't seem to impact any tools we use, but a warning message is generated, so it's fixed by this script as well, just in case.

The script must be run from a directory that can be written to, as it creates temporary netCDF files during in the working directory during processing. It can be run on every file in a directory with the following command:

```
for file in /path/to/netcdfs/*.nc ; do python rename_rp_variables $file ; done
```

## standard_aClim_time.py

This script normalizes time metadata for return period climatologies. As we received the data, time metadata looked like this:

```
netcdf pr_RP20_BCCAQ2_PRISM_ACCESS1-0_rcp85_r1i1p1_1971-2000 {
dimensions:
	time = UNLIMITED ; // (1 currently)
variables:
	double time(time) ;
		time:units = "days since 1-01-01 00:00:00" ;
		time:long_name = "Years" ;
		time:calendar = "proleptic_gregorian" ;
		time:standard_name = "Years" ;
data:

 time = 1 ;
}
```
This script, regrettably, has to extract climatology periods from the filenames, since these files contain no usable time data. It adds a time_bnds variable to represent the climatology, calculates timestamps, and standardizes the metadata to match CE standards:

```
netcdf pr_RP20_BCCAQ2_PRISM_ACCESS1-0_rcp85_r1i1p1_1971-2000 {
dimensions:
	time = UNLIMITED ; // (1 currently)
	bnds = 2 ;
variables:
	double time(time) ;
		time:calendar = "proleptic_gregorian" ;
		time:units = "days since 1950-01-01 00:00:00" ;
		time:long_name = "time" ;
		time:standard_name = "time" ;
		time:bounds = "time_bnds" ;
	double time_bnds(time, bnds) ;

data:

 time = 18262 ;
 
 time_bnds =
  7670, 18627 ;
 
}

```

## files_processed.txt
A list of all return period files processed by these scripts.

## Global metadata processing
[Update_metadata](https://github.com/pacificclimate/climate-explorer-data-prep/blob/master/scripts/update_metadata) was used to add the following missing global attributes:
* method_id: BCCAQv2
* method: Quantile Delta Mapping
* GCM__experiment_id: historical,rcp85
* project_id: CMIP5
* product: downscaled output
* GCM__initialization_method: [as appropriate]
* GCM__realization: [as appropriate]
* GCM__physics_version: [as appropriate]

Update_metadata was also used to update the global metadata from PCIC Metadata Standard v55 to v65. That file can be found [here](https://github.com/pacificclimate/data-prep-actions/pull/5). 