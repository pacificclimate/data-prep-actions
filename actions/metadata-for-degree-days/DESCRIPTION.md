# Metadata for Degree Day Files

These files are inputs to the update_metadata script and provide metadata that is missing from degree day datasets. Both times I have worked on this data, it's been in pretty good shape.

First, the v55->v65 update yaml should be run on files if they're the old metadata version.

global.yaml can be run on all files to provide missing metadata, something like:

```
for file in /path/to/files/*.nc ; do python scripts/update_metadata -u global.yaml $file ; done
```
(Note that global.yaml provides a couple options that may vary across your data collection: method, method_id, and package_id. These are currently set for BCCAQv2; change or remove them if your dataset was generated some other way.)

The four variable files add human friendly variable descriptions taken from a variable metadata spreadsheet Trevor gave me. There's no harm in running these updates on the wrong variables; they just spit error messages. Something like:

```
for file in /path/to/files/cdd*.nc ; do update_metadata -u cdd.yaml $file ; done
for file in /path/to/files/fdd*.nc ; do update_metadata -u fdd.yaml $file ; done
for file in /path/to/files/gdd*.nc ; do	update_metadata -u gdd.yaml $file ; done
for file in /path/to/files/hdd*.nc ; do	update_metadata -u hdd.yaml $file ; done

```

The GFDL-ESM2G model's files were missing run (r1i1p1) and experiment (rcp85) information. The missing data can be added with r1i1p1.yaml and rcp85.yaml:
```
for file in /path/to/files/*r1i1p1*.nc ; do update_metadata -u r1i1p1.yaml $file ; done
for file in /path/to/files/*rcp85*.nc ; do update_metadata -u rcp85.yaml $file ; done
```