# Rename Return Period Variables

This python script renames variables of the form `rp.[PERIOD]` to `rp[PERIOD][MODEL_OUTPUT]` where `[PERIOD]` is the length of the return period in years, typically 5 or 20, and `[MODEL OUTPUT]` is a variable like tasmin, tasmax, or precipitation.

Additionally, the process that generates the return period datasets sometimes generates float-type rp variables with integer fill value attributes. This minor issue doesn't seem to impact any tools we use, but a warning message is generated, so it's fixed by this script as well, just in case.

The script must be run from a directory that can be written to, as it creates temporary netCDF files during in the working directory during processing. It can be run on every file in a directory with the following command:

```
for file in /path/to/netcdfs/*.nc ; do python rename_rp_variables $file ; done
```