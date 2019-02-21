# Add ANUSPLIN Observational Data

## Purpose
The ANUSPLIN dataset was added for the [p2a](https://github.com/pacificclimate/p2a-rule-engine) rule engine.  It will replace `CRU_TS_21` as the new historical baseline.  The following commands were run to produce the climatologies.

## Commands

### 1. General update of missing global metadata

Using the `update_metadata` script from [climate-explorer-data-prep](https://github.com/pacificclimate/climate-explorer-data-prep) update the three anusplin\_[variable_name]\_final.nc files found at `/storage/data/climate/downscale/BCCAQ2/ANUSPLIN/`.

NOTE: These files were copied to `/local_temp/[user]/` as to not change the original data files

```
(venv)$ python scripts/update_metadata -u ../updates.yaml ../anusplin_tasmin_final.nc
(venv)$ python scripts/update_metadata -u ../updates.yaml ../anusplin_tasmax_final.nc
(venv)$ python scripts/update_metadata -u ../updates.yaml ../anusplin_pr_final.nc
```

### 2. Generate the climatologies

Run `generate_climos` on the updated files.

```
python scripts/generate_climos ../anusplin_tasmin_final.nc -o ../climatologies/
python scripts/generate_climos ../anusplin_tasmax_final.nc -o ../climatologies/
python scripts/generate_climos ../anusplin_pr_final.nc -o ../climatologies/
```

### 3. Update missing variable metadata for each climos file

Each file was missing metadata specific to the files variable that was making `index_netcdf` from [modelmeta](https://github.com/pacificclimate/modelmeta) unhappy.

```
(venv)$ for file in ../climatologies/tasmin*.nc ; do python scripts/update_metadata -u ../update_tasmin.yaml $file; done
(venv)$ for file in ../climatologies/tasmax*.nc ; do python scripts/update_metadata -u ../update_tasmax.yaml $file; done
(venv)$ for file in ../climatologies/pr*.nc ; do python scripts/update_metadata -u ../update_pr.yaml $file; done
```

### 4. Index!

```
(venv)$ python scripts/index_netcdf -d postgresql://ce_meta_rw@monsoon.pcic.uvic.ca/ce_meta ../climatologies/*.nc
```
