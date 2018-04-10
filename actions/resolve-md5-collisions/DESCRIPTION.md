# Resolve md5 Collisions

## Purpose

An md5 sum describing the first MB of a data file is stored in the metadata database 
and used to detect updates to the file. In some cases where a netCDF file is generated
with extra header space to support faster updating of the headers, the first MB may
actually be identical across two different data files that share a model, variable, and
period; differing only by emissions scenario.

A file whose first MB is identical to a file already in the database, but which has
a different unique ID (model, period, emissions scenario, run, and variable),
cannot be indexed and yields the following error message:

```
2018-03-05 15:19:36 INFO: Processing file: /storage/data/projects/comp_support/climate_explorer_data_prep/climatological_means/climdex/dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19610101-19901231.nc
2018-03-05 15:19:37 ERROR: Encountered an unanticipated case:
2018-03-05 15:19:37 ERROR: id_match.id = None
2018-03-05 15:19:37 ERROR: hash_match.id = 13
2018-03-05 15:19:37 ERROR: filename_match.id = None
2018-03-05 15:19:37 ERROR: old_filename_exists = True; normalized_filenames_match = False; index_up_to_date = True
2018-03-05 15:19:37 ERROR: Traceback (most recent call last):
  File "/home/lzeman/Code/modelmeta-generic/modelmeta/venv/lib/python3.5/site-packages/mm_cataloguer/index_netcdf.py", line 1060, in index_netcdf_file
    data_file = find_update_or_insert_cf_file(session, cf)
  File "/home/lzeman/Code/modelmeta-generic/modelmeta/venv/lib/python3.5/site-packages/mm_cataloguer/index_netcdf.py", line 1045, in find_update_or_insert_cf_file
    raise ValueError('Unanticipated case. See log for details.')
ValueError: Unanticipated case. See log for details.
```

Long term, the correct solution is to update the database and reindex all files to take
the md5 sum of a longer section of the file, perhap 10MB. Short term, this script
was used to remove the empty space from the headers of a file for file-by-file
resolution of the md5 collision for high-priority files we needed indexed right away
(precipitation climdexes).

The script simply copies every dimension, variable, and attribute from one netCDF
file to another. You'd expect there to be a pre-existing netCDF tool that does
this, but `nccopy` faithfully copies header padding, while `cdo copy` removes 
header padding but makes other unwanted changes.

## Procedure

1. Run the indexing script on the directory containing the md5 hash collision files, redirecting output to a logfile.
`python scripts/index_netcdf -d postgresql://whateverdatabase /path/to/files/dtrETCCDI_*.nc &> dtr.log`

2. Grep the logfile for the error message to get a list of the affected files.
`grep -B1 "unanticipated" dtr.log`

3. Move the affected files to their own directory.
`mv /path/to/files/dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_*.nc /path/to/files/md5_collisions/`

4. Run the de-padding script on the files, placing results in a sub-directory.
`python strip_metadata_padding.py /path/to/files/dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_*.nc  /path/to/files/md5_collisions/compressed`

5. Re-index the files, and add to ensembles as needed.
`python scripts/index_netcdf -d postgresql://whateverdatabase /path/to/files/md5_collisions/compressed/*.nc`

## Datafiles Processed
dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19610101-19901231.nc
dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19710101-20001231.nc
dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19810101-20101231.nc
dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20100101-20391231.nc
dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20400101-20691231.nc
dtrETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20700101-20991231.nc
dtrETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19610101-19901231.nc
dtrETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19710101-20001231.nc
dtrETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19810101-20101231.nc
dtrETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20100101-20391231.nc
dtrETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20400101-20691231.nc
dtrETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20700101-20991231.nc
dtrETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19610101-19901231.nc
dtrETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19710101-20001231.nc
dtrETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19810101-20101231.nc
dtrETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20100101-20391231.nc
dtrETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20400101-20691231.nc
dtrETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20700101-20991231.nc
dtrETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19610101-19901231.nc
dtrETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19710101-20001231.nc
dtrETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19810101-20101231.nc
dtrETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20100101-20391231.nc
dtrETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20400101-20691231.nc
dtrETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20700101-20991231.nc
rx1dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19610101-19901231.nc
rx1dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19710101-20001231.nc
rx1dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19810101-20101231.nc
rx1dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20100101-20391231.nc
rx1dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20400101-20691231.nc
rx1dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20700101-20991231.nc
rx1dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19610101-19901231.nc
rx1dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19710101-20001231.nc
rx1dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19810101-20101231.nc
rx1dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20100101-20391231.nc
rx1dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20400101-20691231.nc
rx1dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20700101-20991231.nc
rx1dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19610101-19901231.nc
rx1dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19710101-20001231.nc
rx1dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19810101-20101231.nc
rx1dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20100101-20391231.nc
rx1dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20400101-20691231.nc
rx1dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20700101-20991231.nc
rx1dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19610101-19901231.nc
rx1dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19710101-20001231.nc
rx1dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19810101-20101231.nc
rx1dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20100101-20391231.nc
rx1dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20400101-20691231.nc
rx1dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20700101-20991231.nc
rx5dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19610101-19901231.nc
rx5dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19710101-20001231.nc
rx5dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_19810101-20101231.nc
rx5dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20100101-20391231.nc
rx5dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20400101-20691231.nc
rx5dayETCCDI_aClim_BCCAQ_CanESM2_historical+rcp85_r1i1p1_20700101-20991231.nc
rx5dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19610101-19901231.nc
rx5dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19710101-20001231.nc
rx5dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_19810101-20101231.nc
rx5dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20100101-20391231.nc
rx5dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20400101-20691231.nc
rx5dayETCCDI_aClim_BCCAQ_CCSM4_historical+rcp85_r2i1p1_20700101-20991231.nc
rx5dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19610101-19901231.nc
rx5dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19710101-20001231.nc
rx5dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_19810101-20101231.nc
rx5dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20100101-20391231.nc
rx5dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20400101-20691231.nc
rx5dayETCCDI_aClim_BCCAQ_CNRM-CM5_historical+rcp85_r1i1p1_20700101-20991231.nc
rx5dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19610101-19901231.nc
rx5dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19710101-20001231.nc
rx5dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_19810101-20101231.nc
rx5dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20100101-20391231.nc
rx5dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20400101-20691231.nc
rx5dayETCCDI_aClim_BCCAQ_MRI-CGCM3_historical+rcp45_r1i1p1_20700101-20991231.nc

## Datafiles Not Processed
Other climdex files with different variables are also affected by this issue. 
Since those files were not needed urgently for a project, they have not yet been 
processed in this way. Estimated number of files that are not currently indexed and
cannot be indexed due to md5 collision, as of April 10, 2018:

* tn10pETCCDI - 72 datafiles
* tn90pETCCDI - 72 datafiles
* tnnETCCDI - 24 datafiles
* tnxETCCDI - 24 datafiles
* tx10pETCCDI - 48 datafiles
* tx90pETCCDI - 48 datafiles
* txnETCCDI - 48 datafiles
* txxETCCDI - 48 datafiles