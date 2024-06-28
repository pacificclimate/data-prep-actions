#!/bin/bash
# this script makes one copy of the template for each file in the
# directory, substituting in the filename and a numerical ID,
# then submits each copy to the queue and deletes the file.
inc=0
input_dir=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
module load python/3.8.6 netcdf-bin
for subdir in $input_dir/*_10/
do
    model=$(basename $subdir)
    if [ "$model" = "nobackup" ]
    then
        continue
    fi
    cat remove_time_offset.pbs | sed 's#MODEL#'$model'#' | sed 's#DIRNAME#'$subdir'#' > remove_time_offset$inc.pbs
    qsub remove_time_offset$inc.pbs
    rm remove_time_offset$inc.pbs
    ((inc++))
done

