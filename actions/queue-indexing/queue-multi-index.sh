#!/bin/bash
# this script makes one copy of the template for each file in the
# directory, substituting in the filename and a numerical ID,
# then submits each copy to the queue and deletes the file.
inc=0
for file in /path/to/files/to/be/indexed/*.nc
do
    echo "Queueing up $file, #$inc"
    cat template.pbs | sed 's#NUMBER#'$inc'#' | sed 's#FILENAME#'$file'#' > template$inc.pbs
    qsub template$inc.pbs
    rm template$inc.pbs
    ((inc++))
done

