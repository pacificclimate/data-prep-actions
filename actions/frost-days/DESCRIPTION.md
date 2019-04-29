# Add metadata to fdETCCDI datafiles

## Purpose
The [p2a](https://github.com/pacificclimate/p2a-rule-engine) rule engine required monthy fdETCCDI data in order to produce `number of frost free days`.  The following commands were run in order to add metadata to the files.

## Commands

### 1. Add metadata common to all files

Using the `update_metadata` script from [climate-explorer-data-prep](https://github.com/pacificclimate/climate-explorer-data-prep).

```
(venv)$ for file in fd/*.nc ; do python scripts/update_metadata -u all_shared.yaml $file ; done
```

### 2. Add metadata common to all files with the same emission scenario

```
(venv)$ for file in fd/*rcp45*.nc ; do python scripts/update_metadata -u fd_rcp45.yaml $file ; done
(venv)$ for file in fd/*rcp85*.nc ; do python scripts/update_metadata -u fd_rcp85.yaml $file ; done
```

### 3. Add metadata common to files with the same ensemble members

```
(venv)$ for file in fd/*r1i1p1*.nc ; do python scripts/update_metadata -u fd_r1i1p1.yaml $file ; done
(venv)$ for file in fd/*r2i1p1*.nc ; do python scripts/update_metadata -u fd_r2i1p1.yaml $file ; done
(venv)$ for file in fd/*r3i1p1*.nc ; do python scripts/update_metadata -u fd_r3i1p1.yaml $file ; done
```

### 4. Add metadata common to files with model

```
(venv)$ for file in fd/*ACCESS1-0*.nc ; do python scripts/update_metadata -u fd_ACCESS1-0.yaml $file ; done
(venv)$ for file in fd/*CanESM2*.nc ; do python scripts/update_metadata -u fd_CanESM2.yaml $file ; done
(venv)$ for file in fd/*CCSM4*.nc ; do python scripts/update_metadata -u fd_CCSM4.yaml $file ; done
(venv)$ for file in fd/*CNRM-CM5*.nc ; do python scripts/update_metadata -u fd_CNRM-CM5.yaml $file ; done
(venv)$ for file in fd/*CSIRO-Mk3-6-0*.nc ; do python scripts/update_metadata -u fd_CSIRO-Mk3-6-0.yaml $file ; done
(venv)$ for file in fd/*GFDL-ESM2G*.nc ; do python scripts/update_metadata -u fd_GFDL-ESM2G.yaml $file ; done
(venv)$ for file in fd/*HadGEM2-CC*.nc ; do python scripts/update_metadata -u fd_HadGEM2-CC.yaml $file ; done
(venv)$ for file in fd/*HadGEM2-ES*.nc ; do python scripts/update_metadata -u fd_HadGEM2-ES.yaml $file ; done
(venv)$ for file in fd/*inmcm4*.nc ; do python scripts/update_metadata -u fd_inmcm4*.yaml $file ; done
(venv)$ for file in fd/*MIROC5*.nc ; do python scripts/update_metadata -u fd_MIROC5.yaml $file ; done
(venv)$ for file in fd/*MPI-ESM-LR*.nc ; do python scripts/update_metadata -u fd_MPI-ESM-LR.yaml $file ; done
(venv)$ for file in fd/*MRI-CGCM3*.nc ; do python scripts/update_metadata -u fd_MRI-CGCM3.yaml $file ; done
```

### 5. Add metadata specific to each file

```
(venv)$ python scripts/update_metadata -u fd_ACCESS1-0_rcp45.yaml fdETCCDI_mon_ACCESS1-0_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_ACCESS1-0_rcp85.yaml fdETCCDI_mon_ACCESS1-0_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CanESM2_rcp45.yaml fdETCCDI_mon_CanESM2_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CanESM2_rcp8.yaml fdETCCDI_mon_CanESM2_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CCSM4_rcp45.yaml fdETCCDI_mon_CCSM4_rcp45_r2i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CCSM4_rcp85.yaml fdETCCDI_mon_CCSM4_rcp85_r2i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CNRM-CM5_rcp45.yaml fdETCCDI_mon_CNRM-CM5_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CNRM-CM5_rcp85.yaml fdETCCDI_mon_CNRM-CM5_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CSIRO-Mk3-6-0.yaml fdETCCDI_mon_CSIRO-Mk3-6-0_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_CSIRO-Mk3-6-0_rcp85.yaml fdETCCDI_mon_CSIRO-Mk3-6-0_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_GFDL-ESM2G_rcp45.yaml fdETCCDI_mon_GFDL-ESM2G_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_GFDL-ESM2G_rcp85.yaml fdETCCDI_mon_GFDL-ESM2G_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_HadGEM2-CC_rcp45.yaml fdETCCDI_mon_HadGEM2-CC_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_HadGEM2-CC_rcp85.yaml fdETCCDI_mon_HadGEM2-CC_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_HadGEM2-ES_rcp45.yaml fdETCCDI_mon_HadGEM2-ES_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_HadGEM2-ES_rcp85.yaml fdETCCDI_mon_HadGEM2-ES_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_inmcm4_rcp45.yaml fdETCCDI_mon_inmcm4_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_inmcm4_rcp85.yaml fdETCCDI_mon_inmcm4_rcp85_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_MIROC5_rcp45.yaml fdETCCDI_mon_MIROC5_rcp45_r3i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_MIROC5_rcp85.yaml fdETCCDI_mon_MIROC5_rcp85_r3i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_MPI-ESM-LR_rcp45.yaml fdETCCDI_mon_MPI-ESM-LR_rcp45_r3i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_MPI-ESM-LR_rcp85.yaml fdETCCDI_mon_MPI-ESM-LR_rcp85_r3i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_MRI-CGCM3_rcp45.yaml fdETCCDI_mon_MRI-CGCM3_rcp45_r1i1p1_1951-2100.nc
(venv)$ python scripts/update_metadata -u fd_MRI-CGCM3_rcp85.yaml fdETCCDI_mon_MRI-CGCM3_rcp85_r1i1p1_1951-2100.nc
```
