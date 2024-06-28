#!/bin/bash
inc=0
#root=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
#models="ACCESS-CM2"
#models="ACCESS-ESM1-5 BCC-CSM2-MR CanESM5 CMCC-ESM2 CNRM-CM6-1 CNRM-ESM2-1 EC-Earth3 EC-Earth3-Veg"
#models="FGOALS-g3 GFDL-ESM4 HadGEM3-GC31-LL INM-CM4-8 INM-CM5-0 IPSL-CM6A-LR KACE-1-0-G KIOST-ESM MIROC6"
models="MIROC-ES2L MPI-ESM1-2-HR MPI-ESM1-2-LR MRI-ESM2-0 NorESM2-LM NorESM2-MM TaiESM1 UKESM1-0-LL"
for model in $models
do
    #base=$(basename $model_dir)
    #model=${base%_10}
    cat convert_classic.pbs | sed 's#MODEL#'$model'#' > convert_classic${inc}.pbs
    qsub convert_classic${inc}.pbs
    rm convert_classic${inc}.pbs
    ((inc++))
done
