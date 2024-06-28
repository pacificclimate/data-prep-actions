model=HadGEM3-GC31-LL
corrected_dir=/storage/data/climate/downscale/BCCAQ2/nobackup/Corrected_Outliers/$model
bccaq2_dir=/storage/data/climate/downscale/BCCAQ2/CMIP6_BCCAQv2/$model
for file in $corrected_dir/*
do
        base=$(basename $file)
        echo "$(date) Copying $base to $bccaq2_dir for replacement"
        #cp $file $bccaq2_dir
done
