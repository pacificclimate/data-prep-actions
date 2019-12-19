#!/bin/bash

for file in *.yaml
do
    echo "Looking for datasets to apply $file to:"
    run="${file%.*}"
    for target in $(ls /storage/data/projects/hydrology/dataportal/CMIP5/VICGL/*.nc | grep -i $run)
    do
	echo "  Applying $run to $target"
	update_metadata -u $file $target
    done
done
