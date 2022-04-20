# Find Mouth of Watershed

This script locates the mouth of a watershed from a geojson file by matching
it up with a netCDF file. The resulting mouth of the watershed along with
the watershed code are outputted as a CSV file.

## Usage
Run with an RVIC file as well as a netCDF file.
```bash
$ python mouths-of-watersheds.py {netcdf} {json} {csv output}

## Requirements
`argparse`
`csv`
`netcdf4`
`shapely`
`geojson`
To build virtual environment:
`python3 -m venv venv`
`source venv/bin/activate`
`pip install {requirement}`
After this point, use source to re-enter environment
