# Update PRSN fill values
The PRSN data was generated from BCCAQv2 temperature and precipitation files. The data in the BCCAQv2 files is compressed into a short, and the fill values are 32767 (maximum short value):
```
netcdf tasmax_day_BCCAQv2+ANUSPLIN300_CanESM2_historical+rcp45_r1i1p1_19500101-21001231 {
dimensions:
	lon = 1068 ;
	lat = 510 ;
	time = 55115 ;
variables:
	double lon(lon) ;
	double lat(lat) ;
	double time(time) ;
	short tasmax(time, lat, lon) ;
		tasmax:units = "degC" ;
		tasmax:_FillValue = 32767s ;
		tasmax:add_offset = 0.001525902 ;
		tasmax:scale_factor = 0.003051804 ;
		tasmax:standard_name = "air_temperature" ;
		tasmax:long_name = "Daily Maximum Near-Surface Air Temperature" ;
		tasmax:missing_value = 32767. ;
		tasmax:cell_methods = "time: maximum" ;
}
```

When the PRSN files were generated, they inherited the fill value metadata attribute from their parents:
```
netcdf prsn_sClimMean_BCCAQv2_CanESM2_historical+rcp85_r1i1p1_19610101-19901231_Canada {
dimensions:
	time = UNLIMITED ; // (4 currently)
	lon = 1068 ;
	lat = 510 ;
	bnds = 2 ;
variables:
	double time(time) ;
	double lon(lon) ;
	double lat(lat) ;
	short prsn(time, lat, lon) ;
		prsn:standard_name = "snowfall_flux" ;
		prsn:long_name = "Precipitation as Snow" ;
		prsn:units = "kg m-2 d-1" ;
		prsn:add_offset = 400.00610361 ;
		prsn:scale_factor = 0.01220722 ;
		prsn:_FillValue = 32767s ;
		prsn:missing_value = 32767s ;
		prsn:cell_methods = "time: mean time: mean over days" ;
	float climatology_bnds(time, bnds) ;
}
```
But their actual fill value was -32768 (minimum short value):
```
netcdf prsn_sClimMean_BCCAQv2_CanESM2_historical+rcp45_r1i1p1_19610101-19901231_Canada {
dimensions:
variables:
// global attributes:
data:

 prsn =
  -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, 
    -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, 
    -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, 
    -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, 
    -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, 
    -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, 
    -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, 
    -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768,
    ...
}
```

This has not yet been investigated; perhaps a rounding error when uncompressing and compressing the data is responsible? The scale factors do change.

This script sets the netCDF metadata attributes `_FillValue` and `missing_value` on the prsn variable to short -32768 using `ncatted`. One an interactive compute node:

```
module load nco-bin
chmod u+x update_fill_md.sh
./update_fill_md.sh
```