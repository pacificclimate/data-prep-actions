# Update PCIC Standard Metadata

## Purpose and Procedure
This .yaml file can be used with the modelmeta `update_metadata` script to update netCDF metadata in a GCM downscaled dataset that is compliant with version 55 of the PCIC Metadata Standard (September 2017) to version 65 of the PCIC Metadata Standard (Octover 2017 to present) for dowwnscaled GCM output.

It renames required global attributes, but does not change any values.
* required attributes named `driving_x` are renamed `GCM__x`
* required attributes named `downscaling_x` are renamed `x`
* required attributes named `target_x` are renamed `target__x`

To use this file, copy it into the modelmeta directory, then

```
python scripts/update_metadata -u pcic_downscaled_metadata_55to65.yaml file_to_upgrade.nc
```

## Datasets updated with this file:
* Annual degree-day data for Climate Explorer
* 20 year return period data for Climate Explorer
* BCCAQ v2 data for the PDP