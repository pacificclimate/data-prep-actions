# Update Climate Explorer Data Prep Test File Metadata

## Purpose
The metadata for `tiny_hydromodel_gcm_climos.nc`, `tiny_hydromodel_gcm.nc`, `tiny_downscaled_tasmax.nc`, `tiny_downscaled_tasmax_climos.nc`, `tiny_downscaled_pr.nc` and `tiny_downscaled_pr_packed.nc` in the [climate-explorer-data-prep](https://github.com/pacificclimate/climate-explorer-data-prep) test files were out of date.  This was causing a series of failures during testing and needed to be updated.

## Commands

Using the [`update_metadata`](https://github.com/pacificclimate/climate-explorer-data-prep/blob/master/dp/update_metadata.py) script.

### 1. Update the hydromodel test files
```
(venv)$ for file in path/to/climate-explorer-data-prep/tests/data/tiny_hydromodel*.nc ; do python scripts/update_metadata -u ../update_hydromodel.yaml $file; done
```

### 2. Update downscaled test files

```
(venv)$ for file in path/to/climate-explorer-data-prep/tests/data/tiny_downscaled*.nc ; do python scripts/update_metadata -u ../update_downscaled.yaml $file; done
```

### 3. Add missing variable to pr test files
```
(venv)$ for file in path/to/climate-explorer-data-prep/tests/data/tiny_downscaled_pr*.nc ; do python scripts/update_metadata -u ../update_pr.yaml $file; done
```
