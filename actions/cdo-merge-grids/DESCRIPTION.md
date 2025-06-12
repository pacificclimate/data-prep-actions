# Helper script to CDO's mergegrid

cdo has a command called `mergegrid`. This command combines data from files with different spatial coverage. But, somewhat oddly, it keeps the existing boundaries of one of the files (the first argument). For example, if you did:

`cdo mergegrid a.nc b.nc out.nc`

`out.nc` would have the same spatial extent as `a.nc`, and data from `a.nc` and `b.nc` that was within that extent. Any data from `b.nc` that was outside the boundaries of `a.nc` would not be present in the combined file.

This script outputs a file whose spatial extent is the smallest rectangle that covers the union of its inputs, containing a specified variable with latitude and longitude dimensions but no data. This blank file can then be used as an input file to `cdo mergegrid` in order to make sure all data from the two constituent files ends up in the output. In order to use the spatial extent of the file output by this script, it needs to be the first input to `cdo mergegrid`.

Usage would be something like this:

`python mergegrid_extent.py a.nc b.nc blank.nc`
`cdo mergegrid blank.nc a.nc blank_with_a.nc`
`cdo mergegrid blank_with_a.nc b.nc out.nc`

This was used to add data for the upper fraser to the area and flow direction rasters for the PCEX backend, which previously contained only data for the Peace watershed.