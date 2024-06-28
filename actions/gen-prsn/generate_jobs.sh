root=/storage/data/climate/downscale/MBCn/CMIP6_MBCn
for model_dir in $root/*_10
do
    base=$(basename $model_dir)
    model=${base%_10}
    python generate_job_file.py $model_dir $PWD $model
done
