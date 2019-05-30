# Normalize Time Variable for PDP Files

## Purpose

The PDP requires:

1. all files have a time variable
2. the time variable have a "units" attribute of the form "days since YYYY-MM-DD"
3. the reference date from the units attribute is the first timestamp

This script modifies a netCDF file such that if #1 and #2 are true, #3 will be made true as well.

For example, a netCDF file whose time variable looked like this:
```
netcdf pr_day_BCCAQv2+ANUSPLIN300_bcc-csm1-1-m_historical+rcp85_r1i1p1_19500101-21001231 {
dimensions:
    lon = 1068 ;
    lat = 510 ;
    time = 55115 ;
variables:
    double lon(lon) ;
    double lat(lat) ;
    double time(time) ;
        time:units = "days since 1850-01-01 00:00:00" ;
        time:calendar = "365_day" ;
        time:long_name = "Time" ;
        time:standard_name = "Time" ;
    short pr(time, lat, lon) ;
data:
 
 time = 36500.5, 36501.5, 36502.5, 36503.5, 36504.5, 36505.5, 36506.5,
...
}
```

Would have 100 years *added* to the reference date, and 100 years *subtracted* from each timestamp:

```
netcdf pr_day_BCCAQv2+ANUSPLIN300_bcc-csm1-1-m_historical+rcp85_r1i1p1_19500101-21001231 {
dimensions:
    lon = 1068 ;
    lat = 510 ;
    time = 55115 ;
variables:
    double lon(lon) ;
    double lat(lat) ;
    double time(time) ;
        time:units = "days since 1950-01-01 00:00:00" ;
        time:calendar = "365_day" ;
        time:long_name = "Time" ;
        time:standard_name = "Time" ;
    short pr(time, lat, lon) ;
 
data:
 
 time = 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5,
...
}
```

**WARNING 1**: this script has not been tested outside the dataset it was written for use with. Be very careful about applying it to new datasets.

For example, as checks on data consistency, it assumes that the dataset starts January first and that the dataset has a CMOR-style filename containing extractable dates. These assumptions are *not* reliable across all PCIC datasets or all netCDF files.

**WARNING 2**: This script does not check that all values in the time variable either monotonically increasing and equally spaced; a file that violated those constraints recently cause us some trouble.


## Procedure
Build modelmeta and use its virtual environment. Copy remove_time_offset.py into the scripts directory.

To do a dry run and see whether the script would be able to normalize the data, but not change anything, use the -d argument:

```
python scripts remove_time_offset.py -d file_to_adjust.nc
```

To normalize a file:
```
python scripts remove_time_offset.py -d file_to_adjust.nc
```
To normalize every file in a directory:
```
for file in /path/to/datasets ; 
do python scripts remove_time_offset.py $file ; 
done
```

## Files processed with this script
The BCCAQv2 data. Individual files are listed in files-processed.txt, though there were approximately two dozen already normalized files that were unchanged by the script.
