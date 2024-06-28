#!/bin/bash

indir=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
for subdir in $indir/*_10/Derived/*/
do
    if [[ "$subdir" == *"ssp370"* ]]; then
        continue
    fi
    cd $subdir
    chmod g+w return_levels
    path=${subdir}return_levels/
    if [ -d "$path" ]; then
        echo "$path exists."
    else
        echo "$path does not exist."
    fi
done
