# Prepare BC Coast Indicators for SCIP

## Purpose
Format the new BC Coast + Fraser indicator files for the SCIP website, that is, prepare them for addition to a modelmeta database. These files have pretty good formatting already, and no data changes were needed, just a small amount of metadata adjusting done with the`update_metadata` tool

## Update project info

globals.yaml contains attributes pertaining to the file format and type. Run it on all files with: 

```
for file in input/*.nc ; do echo $file; update_metadata -u yamls/global.yaml $file ; done
```

## Adjust Runstring

The three components of the run string are represented in the file as three different attributes, which are automatically combined with their single-letter prefixes to make the run string. For example:

```
hydromodel__downscaling__GCM__realization = "3"
hydromodel__downscaling__GCM__initialization_method = "1"
hydromodel__downscaling__GCM__physics_version = "1"
```

would be combined by the indexing software into the string "r3i1p1". In these files, the scientists quite reasonably included the prefix in the attribute value, like this:

```
hydromodel__downscaling__GCM__realization = "r3"
hydromodel__downscaling__GCM__initialization_method = "i1"
hydromodel__downscaling__GCM__physics_version = "p1"
```

which would result in the incorrect run string rr3ii1pp1. Metadata were corrected as follows:

```
for file in input/*r1*.nc ; do echo $file; update_metadata -u yamls/r1.yaml $file ; done
for file in input/*r2*.nc ; do echo $file; update_metadata -u yamls/r2.yaml $file ; done
for file in input/*r3*.nc ; do echo $file; update_metadata -u yamls/r3.yaml $file ; done
for file in input/*r4*.nc ; do echo $file; update_metadata -u yamls/r4.yaml $file ; done
for file in input/*r5*.nc ; do echo $file; update_metadata -u yamls/r5.yaml $file ; done
for file in input/*i1*,nc ; do echo $file; update_metadata -u yamls/i1.yaml $file ; done
for file in input/*p1*.nc ; do echo $file; update_metadata -u yamls/p1.yaml $file ; done
```

## Fix Units

DAP does not allow unicode characters in netCDF attributes. So units using the degree symbol are not allowed. These YAML files update the units string of temperature indicators to say "degC" instead of "&deg;C"

```
for file in input/twMonth*.nc ; do echo $file ; update_metadata -u yamls/tw_month.yaml $file ; done
for file in input/twDay*.nc ; do echo $file ; update_metadata -u yamls/tw_day.yaml $file ; done
```

## Adjust scenario

Datasets typically use historical data for the reference period and modelled data for the future periods. For ease in connecting all the temporal segments of a dataset, their scenario for both reference and projected data is given a unified string like "historical, rcp85". Future data was understandably labeled just "rcp85". Update the scenario string. 

```
for file in input/*rcp45*.nc ; fo echo $file ; update_metadata -u yamls/rcp45.yaml $file ; done
for file in input/*rcp85*.nc ; do echo $file ; update_metadata -u yamls/rcp85.yaml $file ; done
```