#!/bin/bash

indir=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
for subdir in $indir/*_10/
do
	for file in $subdir*.nc
	do
		echo $file
		ncdump -k $file
	done
done
