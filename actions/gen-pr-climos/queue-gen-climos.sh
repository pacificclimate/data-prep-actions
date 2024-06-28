#!/bin/bash
# this script makes one copy of the template for each file in the
# directory, substituting in the filename and a numerical ID,
# then submits each copy to the queue and deletes the file.
inc=0
root=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
#models="ACCESS-CM2"
#models="ACCESS-ESM1-5 BCC-CSM2-MR CanESM5 CMCC-ESM2 CNRM-CM6-1 CNRM-ESM2-1 EC-Earth3 EC-Earth3-Veg"
#models="FGOALS-g3 GFDL-ESM4 HadGEM3-GC31-LL INM-CM4-8 INM-CM5-0 IPSL-CM6A-LR KACE-1-0-G KIOST-ESM MIROC6"
#models="MIROC-ES2L MPI-ESM1-2-HR MPI-ESM1-2-LR MRI-ESM2-0 NorESM2-LM NorESM2-MM TaiESM1 UKESM1-0-LL"
models="BCC-CSM2-MR NorESM2-LM MIROC-ES2L MPI-ESM1-2-HR MRI-ESM2-0 UKESM1-0-LL EC-Earth3-Veg CMCC-ESM2 INM-CM5-0 FGOALS-g3 TaiESM1 IPSL-CM6A-LR"
for model in $models
do
    cat generate_climos.pbs | sed 's#MODEL#'$model'#' > generate_climos${inc}.pbs
    qsub generate_climos${inc}.pbs
    rm generate_climos${inc}.pbs
    ((inc++))
done

