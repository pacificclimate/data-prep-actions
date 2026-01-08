# Split Aggregated PRISM Climologies

## Purpose

The [PRISM data portal](https://data.pacificclimate.org/portal/bc_prism/map/) currently features climatologies that contain both monthly and yearly data. Each file contains data for the twelve monthly means, followed by the yearly mean. The yearly mean is assigned to a Mid-Year (July) date, so the timestamps in the file are not in order.

We want to upgrade to a snazzy new version of ncWMS, but the new version requires monotonic timestamps. So each file has to be split into separate monthly and yearly datasets, which can be viewed or downloaded separately by users.

## Splitting the files

The files were split with CDO rather than `split_merged_climos`, as `split_merged_climos` isn't set up to handle monthly+yearly aggregations and there was some urgency. Commands are in `cdo.txt`. 

## Updating metadata

The original files predated PCIC's metadata standards and contained none of the global metadata required. 

* `prism.yaml` - metadata needed by all these files
* `1971.yaml` and `1981.yaml` - `climo_start_time` and `climo_end_time` attributes for the two climatologies 
* `monthly.yaml` and `yearly.yaml` - `frequency` attributes for the two resolutions

## Dimensionizing CRS

CDO automatically corrects the CRS variable from a variable with a
time dimension to a variable with no dimensions.
CDO's corrections are 100% correct - the CF Standards specify that
CRSs should be dimensionless variables - but the PDP cannot at this
time support downloading a dimensionless variable, so after the CDO
operators, we have the run the `dimensionize_crs.py` script to restore
the dimensional variable.

## Files Processed
* pr_monClim_PRISM_historical_run1_197101-200012.nc
* pr_monClim_PRISM_historical_run1_198101-201012.nc
* tmax_monClim_PRISM_historical_run1_197101-200012.nc
* tmax_monClim_PRISM_historical_run1_198101-201012.nc
* tmin_monClim_PRISM_historical_run1_197101-200012.nc
* tmin_monClim_PRISM_historical_run1_198101-201012.nc

## Next Steps

These files are still missing some required metadata; we're waiting to hear back from scientists, but this process filled in enough metadata to make it possible to add them to the database and map servers.