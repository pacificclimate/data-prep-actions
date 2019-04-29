# Generate Precipitation as Snow climatologies

## Purpose
This script will produce a series of `.pbs` files that can be run by the queue to produce climatological mean files for precipitation as snow (`prsn`).  The files created by `generate_prsn` would collectively be too large to store, thus the script will throw them away afterwards.  The prsn datasets get passed into `generate_climos` where the climatological files are created.  In order to use the script the `/path/to/'s` will have to be updated.

## Commands

### 1. Generate the `.pbs` job files

`(venv)$ python generate_job_file.py /path/to/datasets /path/to/output/directory`

### 2. Run queue
`$ for job in /path/to/output/directory ; do qsub $job ; done`
