#!/bin/bash

localdir="/local_temp/lzeman/first"

for var in BASEFLOW EVAP GLAC_AREA GLAC_MBAL GLAC_OUTFLOW PET_NATVEG PREC RAINF RUNOFF SNOW_MELT SOIL_MOIST_TOT SWE TRANSP_VEG
do
  echo "$(date) Now processing $var files"
  for file in /storage/data/projects/hydrology/dataportal/CMIP5/VICGL/*$var*.nc
  do
    echo "  Now processing $file"
    echo "    $(date) now copying $file to $localdir"
    base=$(basename $file)
    cp $file $localdir/$base
    echo "    $(date) now subsetting $base"
    cdo seltimestep,1/1 $localdir/$base $localdir/$base.1
    echo "    $(date) cleaning up original and renaming subset"
    rm $localdir/$base
    mv $localdir/$base.1 $localdir/$base
  done
done
