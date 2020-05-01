# Merge streamflow timeseries

## merge-timeseries-csv.py
This is a pretty single-purpose script. It is intended to merge multiple CSVs containing timeseries streamflow data into a single file and format it for use with the PDP's Routed Streamflow portal. It takes the names of the files to be merged as an argument.

CSV files should have a date column and one or more timeseries columns, like this:

| Date       | ACCESS1-0_rcp45_r1i1p1 |
|------------|------------------------|
| 1945-01-01 | 487.179870605469       |
| 1945-01-02 | 975.182678222656       |
| 1945-01-03 | 1008.06353759766       |



| Date       | CanESM2_rcp45_r1i1p1 |
|------------|----------------------|
| 1945-01-01 | 487.182159423828     |
| 1945-01-02 | 977.417358398438     |
| 1945-01-03 | 1019.74468994141     |

The output is a file like this:

| Date       | ACCESS1-0_rcp45_r1i1p1 | CanESM2_rcp45_r1i1p1 |
|------------|------------------------|----------------------|
| 1945-01-01 | 487.179870605469       | 487.182159423828     |
| 1945-01-02 | 975.182678222656       | 977.417358398438     |
| 1945-01-03 | 1008.06353759766       | 1019.74468994141     |

If the timestamp column has a different name, it can be set by changing the `date_att` variable at the beginning of the script. If any timeseries is missing some of the data, it will be empty in those locations.

## queue-file-merge.py
This script outputs pbs files that run `merge-timeseries-csv.py` for groups of files on the queue. It reads a directory on storage containing a bunch of csvs, and outputs a pbs jobfile that merges each set of csvs that share a prefix. Hydrology produced files named `[station].[model].csv` - this script outputs a job to merge all data for each station together.

You may need to edit various file location in the template file, `template.pbs`, to update where the script outputs logs and data, and where it looks for `merge-timeseries-csv.py`, etc. I didn't parametrize them because it seems unlikely we'll need to run this script again.