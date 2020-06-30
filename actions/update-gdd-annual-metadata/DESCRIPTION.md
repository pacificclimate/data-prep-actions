# Update gdd_annual Metadata

## Purpose and Procedure
This .yaml file can be used with the ce-dp `update_metadata` script to update netCDF metadata in the `gdd_annual_CanESM2_rcp85_r1i1p1_1951-2100.nc` dataset so that it can be used as input in the `generate_climos` script.

It sets the following global attributes:
* project_id: CMIP5
* initialization_method: 1
* physics_version: 1
* model_id: CanESM2
* experiment_id: rcp85

To use this .yaml file, copy the aforementioned netcdf file from the storage on the compute nodes to a different location, install the packages detailed in the [ce-dp README.md](https://github.com/pacificclimate/climate-explorer-data-prep#installation), then execute

```
update-metadata -u updates.yaml path/to/gdd_annual_file.nc
```