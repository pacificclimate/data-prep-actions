#!/bin/bash

indir=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
for subdir in $indir/*_10/
do
	cd $subdir
	chown eyvorchuk *.nc
	chmod g+w *.nc
done
