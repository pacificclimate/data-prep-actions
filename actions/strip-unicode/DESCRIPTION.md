# Strip Unicode from netCDF metadata

## Purpose

A user downloading data from the PDP received a file with a lot of missing metadata, like this:

```
$ ncdump -h allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.RUNOFF.nc
netcdf allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.RUNOFF {
dimensions:
        time = UNLIMITED ; // (56613 currently)
        lat = 367 ;
        lon = 496 ;
variables:
        double lat(lat) ;
                lat:_Netcdf4Dimid = 1 ;
                lat:CLASS = "DIMENSION_SCALE" ;
                lat:NAME = "lat" ;
        double lon(lon) ;
                lon:_Netcdf4Dimid = 2 ;
                lon:CLASS = "DIMENSION_SCALE" ;
                lon:NAME = "lon" ;
        double time(time) ;
                time:_Netcdf4Dimid = 0 ;
                time:CLASS = "DIMENSION_SCALE" ;
                time:NAME = "time" ;
        short RUNOFF(time, lat, lon) ;
                RUNOFF:_Netcdf4Dimid = 0 ;
                RUNOFF:missing_value = -32767.f ;
                RUNOFF:scale_factor = -0.003785882f ;
                RUNOFF:add_offset = 124.0482f ;
                RUNOFF:_FillValue = -32767s ;

// global attributes:
                :model_end_month = 12. ;
                :model_start_month = 1. ;
                :nco_openmp_thread_number = 1 ;
                :model_start_year = 1945. ;
                :model_end_day = 31. ;
                :model_start_day = 1. ;
                :model_start_hour = 0. ;
                :model_end_year = 2099. ;
}
```

This file was unusable because it was missing the units for the time attribute - netCDF processing software had no idea what any of the timestamps meant.

Upon investigation, this file on the server was found to contain a metadata attribute that was a netCDF unicode `string` instead of the usual `text` attribute. 

```
netcdf allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.BASEFLOW.nc {
dimensions:
    ...
variables:
    short BASEFLOW(time, lat, lon) ;
    double lat(lat) ;
    double lon(lon) ;
    double time(time) ;
 
// global attributes:
        ...
        :downscaling__GCM__experiment_id = "rcp45" ;
        :downscaling__GCM__initialization_method = "1" ;
        :downscaling__GCM__institute_id = "CNRM-CERFACS" ;
        :downscaling__GCM__institution = "Centre National de Recherches Meteorologiques and Centre Europeen de Recherche et Formation Avancee en Calcul Scientifique" ;
        :downscaling__GCM__model_id = "CNRM-CM5" ;
        :downscaling__GCM__physics_version = "1" ;
        :downscaling__GCM__realization = "1" ;
        string :downscaling__GCM__model_name = "Centre National de Recherches Météorologiques Climate Model" ;
}

```
PyDAP does not allow string metadata, so this needed to be removed.

## Process

The included yaml file was used with the metadata update script to convered the unicode `string` into a text attribute.

After this update, the files still downloaded with missing metadata attributes (though the new attribute did download). NetCDF `string` attributes explicitly allovcate space in the file; it seemed like perhaps there was some remnant of that process remaining. So the files were converted to netCDF3 (which does not support `string` attributes) and back to netCDF4 to purge whatever traces remained, whcih fixed the issue.

```
[lzeman@lynx ~]$ for file in *.nc ; do echo $file ; mv $file $file.old ; nccopy -k classic $file.old $file.nc3 ; nccopy -k netCDF4 $file.nc3 $file ; rm $file.old ; rm $file.nc3 ; done
```

## Files processed with this method
All CNRM-CM5 files on the hydrology model output portal, specifically:

* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.BASEFLOW.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.EVAP.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.GLAC_AREA.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.GLAC_MBAL.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.GLAC_OUTFLOW.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.PET_NATVEG.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.PREC.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.RAINF.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.RUNOFF.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.SNOW_MELT.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.SOIL_MOIST_TOT.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.SWE.nc
* allwsbc.CNRM-CM5_rcp45_r1i1p1.1945to2099.TRANSP_VEG.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.BASEFLOW.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.EVAP.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.GLAC_AREA.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.GLAC_MBAL.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.GLAC_OUTFLOW.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.PET_NATVEG.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.PREC.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.RAINF.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.RUNOFF.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.SNOW_MELT.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.SOIL_MOIST_TOT.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.SWE.nc
* allwsbc.CNRM-CM5_rcp85_r1i1p1.1945to2099.TRANSP_VEG.nc
