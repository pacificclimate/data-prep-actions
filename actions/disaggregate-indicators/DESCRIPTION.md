# Disaggregate BC-SRIF Indicators

## Purpose
The scripts and YAMLs in this directory are used to disaggregate the BC-SRIF indicator data, as output by Travis.

The raw indicator data differs from CF Standards format in the following ways:
1. instead of latitude and longitude, uses numbered cells
2. has a dimension for statistics (mean, min, max, sd, n)
3. time dimension consists of a number of climatologies, which are described in attributes, but not in data format
4. some metadata is missing, and some has different names
5. no climatology bounds indicated
6. no cell methods

Here is a sample of one of the aggregator files, pre-processing.
```
netcdf pot19freqyear {
dimensions:
	cell = 11794 ;
	time.int = 4 ;
	var_5 = 5 ;
variables:
	int cell(cell) ;
		cell:units = "-" ;
		cell:long_name = "Grid cell number" ;
	int time.int(time.int) ;
		time.int:units = "30 year intervals" ;
		time.int:long_name = "1:1971-2000 ; 2:2010-2039 ; 3:2040-2069 ; 4:2070-2099" ;
	int var_5(var_5) ;
		var_5:units = "parameter" ;
		var_5:long_name = "parameters: 1-mean, 2-sd, 3-n, 4-min, 5-max" ;
	float POT19freq_year(var_5, time.int, cell) ;
		POT19freq_year:units = "days" ;
		POT19freq_year:_FillValue = 1.e+32f ;
		POT19freq_year:long_name = "annual mean frequency (days) with peak-over-threshold temperatures > 19C" ;

// global attributes:
		:Title = "Salmon Risk Assessment Hydrological Indicators" ;
		:Major\ drainage = "fraser" ;
		:Model = "CanESM2" ;
		:Model\ run = "r1i1p1" ;
		:RCP\ scenario = "rcp45" ;
		:Time\ period = "1971-2099" ;
		:Temporal\ resolution = "30 year means" ;
		:Institution = "Pacific Climate Impacts Consortium" ;
		:Authors = "Travis Tai" ;
		:Date = "2022-07-15" ;
}
```

## Procedure

### 1. disaggregate-netcdfs.py
This script accepts an indicator file as input, and outputs 20 netCDF files, one for each combination of operation (min, max, mean, std, n) and climatology (1971-2000, 2:2010-2039, 2040-2069, 2070-2099). Currently, it only works if the metadata indicates exactly those operations and exactly those climatologies, and only on annual-resolution datasets.

It requires a CSV file giving the latitude and longitude for each numbered cell. A sample version is included (cell_index.csv) but you should get an up to date one with each data set.

It translates all metadata in the file to the PCIC metadata standard for data derived from a routed streamflow model with GCM input, but it doesn't fill in any metadata that is not in the file.

It creates a climatology_bnds variable.

### 2. globals.yaml

This YAML file can be used with `update_metadata` to fill in the rest of the missing metadata for the PCIC metadata standard for data derived from a routed streamflow model with GCM input, assuming the "usual" setup. You can get `update_metadata` by cloning and building the `climate-explorer-data-prep` repository.

### 3. indicator-specific yamls

These YAML files can be used with `update_metadata` to fill in variable attributes: cell_methods, and formatting units to match PCIC standards ("degC" instead of "degrees celsius"). Use each file on the matching indicator outputs, like:
```
for file in apd_flow*.nc ; do update_metadata -u apd_flow.yaml $file ; done
```

and so on for each indicator.