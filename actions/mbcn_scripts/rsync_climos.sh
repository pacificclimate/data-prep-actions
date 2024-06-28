#models="ACCESS-CM2 ACCESS-ESM1-5 BCC-CSM2-MR CanESM5 CMCC-ESM2 CNRM-CM6-1 CNRM-ESM2-1 EC-Earth3 EC-Earth3-Veg"
#models="CMCC-ESM2 CNRM-CM6-1 CNRM-ESM2-1 EC-Earth3 EC-Earth3-Veg"
#models="FGOALS-g3 GFDL-ESM4 HadGEM3-GC31-LL INM-CM4-8 INM-CM5-0 IPSL-CM6A-LR KACE-1-0-G KIOST-ESM MIROC6 MIROC-ES2L MPI-ESM1-2-HR MPI-ESM1-2-LR MRI-ESM2-0 NorESM2-LM NorESM2-MM TaiESM1 UKESM1-0-LL"
models="Ensemble_Averages"
for model in $models
do
    root_dir=/storage/data/climate/downscale/MBCn/CMIP6_MBCn/${model}
    scenarios="ssp126 ssp245 ssp585"
    subdirs="annual climdex degree_days monthly return_levels seasonal"
    periods="1971-2000 1981-2010 2011-2040 2041-2070 2071-2100"
    if [ $model = 'CanESM5' ]; then
        run=r1i1p2f1
    else
        ls_out=$(ls $root_dir)
        [[ $ls_out =~ (r[0-9][[:alnum:]]*) ]]
        run=${BASH_REMATCH[1]}
    fi

    for scenario in $scenarios
    do
        scenario_dir=Ensemble_${scenario}_Average
        for subdir in $subdirs
        do
            if [ "$subdir" = "return_levels" ]; then
                full_dir=$root_dir/$scenario_dir/$subdir
            else
                full_dir=$root_dir/$scenario_dir/$subdir
            fi
            for period in $periods
            do
                rsync -a --bwlimit=7680 --progress --stats -e "ssh -i ~/.ssh/pcicadmin" $full_dir/*${period}.nc pcicadmin@webapps.pacificclimate.org:$full_dir
            done
        done
    done
done
