#!/bin/bash

localdir="/local_temp/lzeman/ncatted"

for var in BASEFLOW EVAP GLAC_AREA GLAC_MBAL GLAC_OUTFLOW PET_NATVEG PREC RAINF RUNOFF SNOW_MELT SOIL_MOIST_TOT SWE TRANSP_VEG
do
  echo "$(date) Now processing $var files"
  for file in /storage/data/projects/hydrology/dataportal/CMIP5/VICGL/*$var*.nc
  do
    echo "  Now processing $file"
    echo "    $(date) now copying $file to $localdir"
    base=$(basename $file)
    cp $file $localdir/$base
    echo "    $(date) now updating attributes in $file"
    ncatted -a _FillValue,$var,m,s,-32767 -a _FillValue,lat,d,, -a _FillValue,lon,d,, -a _FillValue,time,d,, $localdir/$base $localdir/$base.att
    echo "    $(date) now converting $file to netcdf4"
    nccopy -k 3 $localdir/$base.att $localdir/$base.4
    echo "    $(date) Now copying to /storage"
    cp $localdir/$base.4 $file
    echo "    $(date) now cleaning up"
    rm $localdir/$base
    rm $localdir/$base.att
    rm $localdir/$base.4
  done
done
