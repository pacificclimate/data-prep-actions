# Processing Fraser + Peace merged files

Script and config files used to prepare the streamflow datasets for the Fraser + Peace merged watershed.

## Formatting climatology bounds

The PCIC metadata standards require three types of information to completely define a climatology:

* the `climo_start_time` and `climo_end_time` global attribute, which mark the beginning and end of the entire climatology
* the `frequency` global attribute, which indicates whether it is an annual, daily, monthly, etc climatology
* the `time_bnds` variable, which has two data points for each data point of the `time` variable, indicating the beginning and end of the time span covered by that variable (for an annual climatology, these will be the same as `climo_start_time` and `climo_end_time` but if the climtaology has multiple data points per year, each one will have an entry in this variable)

This data set is lacking all this information.

### Filling in the frequency global attribute

There are three yaml config files, one for means, one for 2.5th percentiles, and one for 97.5th percentiles. Apply each .yaml to the relevant datasets like so:

```
$ for file in *Mean* ; do update_metadata -u ../../yamls/ops/mean.yaml $file ; done
$ for file in *025P* ; do update_metadata -u ../../yamls/ops/25p.yaml $file ; done
$ for file in *975P* ; do update_metadata -u ../../yamls/ops/975p.yaml $file ; done
```

### Formatting climo start and end times

These must match the climatology, which is present in the file name, but set incorrectly in the files.

```
$ for file in *2071*.nc ; do update_metadata -u ../../yamls/climos/2071.yaml $file ; done
$ for file in *2061*.nc ; do update_metadata -u ../../yamls/climos/2061.yaml $file ; done
$ for file in *2051*.nc ; do update_metadata -u ../../yamls/climos/2051.yaml $file ; done
$ for file in *2041*.nc ; do update_metadata -u ../../yamls/climos/2041.yaml $file ; done
$ for file in *2031*.nc ; do update_metadata -u ../../yamls/climos/2031.yaml $file ; done
$ for file in *2021*.nc ; do update_metadata -u ../../yamls/climos/2021.yaml $file ; done
$ for file in *2011*.nc ; do update_metadata -u ../../yamls/climos/2011.yaml $file ; done
$ for file in *2001*.nc ; do update_metadata -u ../../yamls/climos/2001.yaml $file ; done
```

### Creating the time_bnds variable

Once all this information about the climatologies is present in the files, the add_time_bounds.py script will have the input it needs to create the `time_bnds` variable. It can be run like this:

```
for file in *.nc ; do echo $file ; python ../../add-time-bounds.py $file $file.tmp ; mv $file.tmp $file ; done
```

But be careful if you run it with this command - if the script can't complete for any reason, it will output a blank netcdf file that the following `mv` bash command will copy overtop your input file.

## Formatting cell methods

Because each variable must be named explicitly to set a variable attribute on it, and because the cell methods vary based on whether the datafile is an ensemble mean or ensemble percentile, it takes 42 separate configuration files to set all the cell methods for this dataset, one for each combination of variable (14 variables) and aggregating operation (mean, 2.5 percentile, 97.5 percentile).

```
# change factor means
$ for file in cfrp10streamflow_aClimMean* ; do update_metadata -u ../../yamls/cfrpmeans/cfrp10mean.yaml $file ; done
$ for file in cfrp100streamflow_aClimMean* ; do update_metadata -u ../../yamls/cfrpmeans/cfrp100mean.yaml $file ; done
$ for file in cfrp2streamflow_aClimMean* ; do update_metadata -u ../../yamls/cfrpmeans/cfrp2mean.yaml $file ; done
$ for file in cfrp20streamflow_aClimMean* ; do update_metadata -u ../../yamls/cfrpmeans/cfrp20mean.yaml $file ; done
$ for file in cfrp200streamflow_aClimMean* ; do update_metadata -u ../../yamls/cfrpmeans/cfrp200mean.yaml $file ; done
$ for file in cfrp5streamflow_aClimMean* ; do update_metadata -u ../../yamls/cfrpmeans/cfrp5mean.yaml $file ; done
$ for file in cfrp50streamflow_aClimMean* ; do update_metadata -u ../../yamls/cfrpmeans/cfrp50mean.yaml $file ; done

# change factor 2.5 percentiles
$ for file in cfrp5streamflow_aClim025P* ; do update_metadata -u ../../yamls/cfrp25/cfrp5_25p.yaml $file ; done
$ for file in cfrp50streamflow_aClim025P* ; do update_metadata -u ../../yamls/cfrp25/cfrp50_25p.yaml $file ; done
$ for file in cfrp2streamflow_aClim025P* ; do update_metadata -u ../../yamls/cfrp25/cfrp2_25p.yaml $file ; done
$ for file in cfrp20streamflow_aClim025P* ; do update_metadata -u ../../yamls/cfrp25/cfrp20_25p.yaml $file ; done
$ for file in cfrp200streamflow_aClim025P* ; do update_metadata -u ../../yamls/cfrp25/cfrp200_25p.yaml $file ; done
$ for file in cfrp10streamflow_aClim025P* ; do update_metadata -u ../../yamls/cfrp25/cfrp10_25p.yaml $file ; done
$ for file in cfrp100streamflow_aClim025P* ; do update_metadata -u ../../yamls/cfrp25/cfrp100_25p.yaml $file ; done

# change factor 97.5 percentiles
$ for file in cfrp10streamflow_aClim975P* ; do update_metadata -u ../../yamls/cfrp975/cfrp10_975p.yaml $file ; done
$ for file in cfrp100streamflow_aClim975P* ; do update_metadata -u ../../yamls/cfrp975/cfrp100_975p.yaml $file ; done
$ for file in cfrp2streamflow_aClim975P* ; do update_metadata -u ../../yamls/cfrp975/cfrp2_975p.yaml $file ; done
$ for file in cfrp20streamflow_aClim975P* ; do update_metadata -u ../../yamls/cfrp975/cfrp20_975p.yaml $file ; done
$ for file in cfrp200streamflow_aClim975P* ; do update_metadata -u ../../yamls/cfrp975/cfrp200_975p.yaml $file ; done
$ for file in cfrp5streamflow_aClim975P* ; do update_metadata -u ../../yamls/cfrp975/cfrp5_975p.yaml $file ; done
$ for file in cfrp50streamflow_aClim975P* ; do update_metadata -u ../../yamls/cfrp975/cfrp50_975p.yaml $file ; done

# return period means
$ for file in rp2streamflow*Mean* ; do update_metadata -u ../../yamls/rpmeans/rp2mean.yaml $file ; done
$ for file in rp20streamflow*Mean* ; do update_metadata -u ../../yamls/rpmeans/rp20mean.yaml $file ; done
$ for file in rp200streamflow*Mean* ; do update_metadata -u ../../yamls/rpmeans/rp200mean.yaml $file ; done
$ for file in rp5streamflow*Mean* ; do update_metadata -u ../../yamls/rpmeans/rp5mean.yaml $file ; done
$ for file in rp50streamflow*Mean* ; do update_metadata -u ../../yamls/rpmeans/rp50mean.yaml $file ; done
$ for file in rp10streamflow*Mean* ; do update_metadata -u ../../yamls/rpmeans/rp10mean.yaml $file ; done
$ for file in rp100streamflow*Mean* ; do update_metadata -u ../../yamls/rpmeans/rp100mean.yaml $file ; done

# return period 2.5 percentiles
$ for file in rp2streamflow*025P* ; do update_metadata -u ../../yamls/rp25/rp2_25p.yaml $file ; done
$ for file in rp20streamflow*025P* ; do update_metadata -u ../../yamls/rp25/rp20_25p.yaml $file ; done
$ for file in rp200streamflow*025P* ; do update_metadata -u ../../yamls/rp25/rp200_25p.yaml $file ; done
$ for file in rp5streamflow*025P* ; do update_metadata -u ../../yamls/rp25/rp5_25p.yaml $file ; done
$ for file in rp50streamflow*025P* ; do update_metadata -u ../../yamls/rp25/rp50_25p.yaml $file ; done
$ for file in rp10streamflow*025P* ; do update_metadata -u ../../yamls/rp25/rp10_25p.yaml $file ; done
$ for file in rp100streamflow*025P* ; do update_metadata -u ../../yamls/rp25/rp100_25p.yaml $file ; done

# return period 97.5 percentiles
$ for file in rp2streamflow*975P* ; do update_metadata -u ../../yamls/rp975/rp2_975p.yaml $file ; done
$ for file in rp20streamflow*975P* ; do update_metadata -u ../../yamls/rp975/rp20_975p.yaml $file ; done
$ for file in rp200streamflow*975P* ; do update_metadata -u ../../yamls/rp975/rp200_975p.yaml $file ; done
$ for file in rp5streamflow*975P* ; do update_metadata -u ../../yamls/rp975/rp5_975p.yaml $file ; done
$ for file in rp50streamflow*975P* ; do update_metadata -u ../../yamls/rp975/rp50_975p.yaml $file ; done
$ for file in rp10streamflow*975P* ; do update_metadata -u ../../yamls/rp975/rp10_975p.yaml $file ; done
$ for file in rp100streamflow*975P* ; do update_metadata -u ../../yamls/rp975/rp100_975p.yaml $file ; done

```


## Miscellaneous

The `global.yaml` file does some miscellaneous formattion cleanup.