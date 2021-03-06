# Generate RVIC Grid File

The two scripts in this file can be used together to generate raster
streamflow data using PCIC's compute queue. `rvic-queuer` creates PBS
job scripts that run RVIC on every individual cell in the watershed.
`rvic-reassembler` combines the resulting single-cell streamflow files
back into a grid.

## You will need
Warning: the author of the scripts and README is not a hydrologist and uses 
inaccurate names for these hydrology data files. If you need to
ask Hydrology for some files, functional descriptions might be
needed.

### A baseflow netCDF file
This file provides the data from which streamflow is calculated.
It is a raster file containing a timeseries of hydrological
data about how water flows over and under the ground, based on modeled
rainfall output by a GCM. It is created by the VIC-GL model. It needs to have
the variables `RUNOFF` and `BASEFLOW`.

### A domain netCDF file 
This file describes the extent of the watershed. It needs to
have the following variables:
* `mask` (1 if this grid square is in the watershed, 0 if not)
* `frac` (I think this may be optional, but not sure)
* `area` (area of each grid square - the higher the latitude, the smaller the area)

### A domain routing netCDF file
This file also contains information about the watershed; it
describes which grid squares feed water to eachother.
It needs to have the following variables:
* `Flow_distance`
* `Flow_direction`
* `Basin_ID`
* `velocity`
* `diffusion`

### A unit hydrograph CSV file
This is a CSV file that describes how water seeps through a single
grid square. All PCIC RVIC runs use the same one; there's a copy in
this repository.

### An RVIC python environment
Currently, the script is hard-coded to use the environment at 
`/storage/data/projects/comp_support/climate_explorer_data_prep/hydro/peace_watershed/venv`
If you need to change that, you can just change the constant at the beginning of
`rvic-queuer.py`.

To make a new RVIC environment:
```
module load python
python3 -m venv venv
source venv/bin/activate
git clone http://github.com/UW-Hydro/RVIC
cd RVIC
```
Now open `core/share.py` in the editor of your choice and change 
every instance of `valid_range` from lines 277 to 298 to `range`.
```
pip install .
```

### An output directory on storage
It should contain a directory named `logs`.

## Procedures

### Note: The Peace Watershed And Its Assumptions
The Peace is a fairly small watershed. Some of the assumptions this
script makes about filesize and runtime may not hold true if you are
simulating a much larger watershed. The script assumes:

* The baseflow file is less than 60GB in size
* An individual point takes 25 minutes or less to calculate

You may need to allocate more time and space if you're doing the Columbia
or something.

### Choosing the n argument
This script begins by copying all the input files to local storage on the
compute node, before using them to calculate as many grid cells as you
requested. If you are doing a very small number of cells this is probably
pretty inefficient. 20 cells per job has worked well.

However, the generated job file is pretty messy and repetitive, as it
contains commands to write out separate, near-identical configuration
files for each grid square. If you are testing, n=1 is probably best
for your sanity.

## Procedure

Put the input files somewhere accessible on `/storage`.

Run `rvic-queuer.py` to generate jobfiles. They'll be named `rvic##.pbs,` 
with the numbers starting at 0.

Submit the jobs to the queue.

Once all the jobs have been submitted and run, you can run `rvic-assembler.py` 
on the resulting streamflow files to get a grid again.

There is an oversight in `rvic-assembler.py`: it does not assign an explicit
`_FillValue` attribute to streamflow, and streamflow ends up with the default
fill value for float variables of `9.96921e+36`, and no explicit `_FillValue`
attribute. Most netCDF tools seem to make allowances for a default
unspecified fill value, but the modelmeta indexer does not, and it's
certainly better to explicitly assign it anyway. So you can either update
`rvic-assembler.py` before it is next used or use `ncatted` to manually
assign the fill value attribute, like this:
```
ncatted -a _FillValue,streamflow,c,f,9.96921e+36 streamflow_aClimMean_CanESM2_rcp85_r1i1p1_19610101-19901231_peace.nc streamflow.nc
mv streamflow.nc streamflow_aClimMean_CanESM2_rcp85_r1i1p1_19610101-19901231_peace.nc
```

## Helpful commands
To submit jobs in batches:
 ```
for i in {0..49} ; do qsub rvic$i.pbs ; done
 ```
 
 To check whether all points for a job sucessfully completed:
 ```
 ls CanESM2_rcp85_r1i1p1_process9_point*.nc | wc -l
 ```

## Metadata
`rvic-assembler.py` copies metadata attributes from the baseflow file
to the final gridded streamflow file, prepending `hydromodel__`
to each. Further metadata formatting is probably needed, however.
`streamflow.yaml` is a sample input file for the `update_metadata`
tool.

## Date-filename problem
We cannot choose the name of the file RVIC outputs from the first step,
which contains the Impulse Response Functions used to calculate
streamflow and is needed as input to the second step.
RVIC generates a name for this file that includes the
date the file was created.

This script uses shell commands to assemble the filename, including the
date, but is, on rare occaisions, incorrect if the impulse response
function calculations began before midnight but finished after midnight.
Anecdotally, this seems to happen about 0.02% of the time.

The missing-points.py script is intended to check for this particular
failure. Given that the peace watershed is about 7500 grid cells, it
does actually come up sometimes.