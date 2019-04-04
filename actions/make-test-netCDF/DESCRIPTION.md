# Make a Test NetCDF file

This script copies an existing netCDF file to a new location of your choice, with the following two changes:
* Replace selected variable's actual data with a repeated constant (masking is preserved)
* Update global history attribute to reflect use of this script

It is useful for debugging mathematical transformations done to netCDF files. Metadata is copied in full so that any process that accepts the source file should accept the test file as well.

Typical usage:
```bash
python make-test-file.py input.nc test-file.nc tasmax 1
```