# Copy files for the PCIC12 ensemble to its own directory before computing ensemble means
root_dir=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
models="BCC-CSM2-MR NorESM2-LM UKESM1-0-LL MRI-ESM2-0 MPI-ESM1-2-HR EC-Earth3-Veg MIROC-ES2L INM-CM5-0 CMCC-ESM2 FGOALS-g3 TaiESM1 IPSL-CM6A-LR"
scenarios="ssp126 ssp245 ssp585"
periods="1971-2000 1981-2010 2011-2040 2041-2070 2071-2100"
for model in $models
do
    for scenario in $scenarios
    do
        scenario_dir=${model}_${scenario}_*
        for period in $periods
        do
            cp $root_dir/${model}_10/Derived/$scenario_dir/return_levels/tas*RL50*${period}.nc pcic12_models
        done
    done
done
