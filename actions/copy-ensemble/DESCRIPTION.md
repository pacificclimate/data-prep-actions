# Copy files from one metadata ensemble to another

## Purpose
This script copies files associated with one ensemble to another ensemble in the same database.

## Usage
Modelmeta version 0.1.2 should be checked out, and this script placed in the "scripts directory".

```
copy_ensemble_files dsn source_ensemble_name destination_ensemble_name
```

It was used to create a `ce_files` ensemble that contained all files from the `all_CLIMDEX_files` and `all_downscale_files` ensembles:

```
 python scripts/copy_ensemble_files.py postgresql://user@server/database all_CLIMDEX_files ce_files
  python scripts/copy_ensemble_files.py postgresql://user@server/database all_downscale_files ce_files
```

It was also used to add some files that had been accidentally left out of the `all_files` ensemble:

```
python scripts/copy_ensemble_files.py postgresql://user@server/database all_CLIMDEX_files all_files
```


