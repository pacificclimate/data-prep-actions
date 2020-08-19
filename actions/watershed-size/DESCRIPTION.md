# Get Watershed Size

This extremely simple script counts the number of cells in an RVIC domain file that are marked as being part of the watershed (that is, they have values greater than 0 on the `mask` variable). 

## Usage
Run on an RVIC domain file. 
```bash
$ python watershed-counter.py /storage/data/projects/hydrology/vic_gen2/input/routing/peace/parameters/domain.rvic.peace.20161018.nc 
This domain contains 7485 grid cells inside the watershed

$ python watershed-counter.py /storage/data/projects/hydrology/vic_gen2/input/routing/columbia/parameters/domain.pnw.pcic.20170927.nc 
This domain contains 24113 grid cells inside the watershed

$ python watershed-counter.py /storage/data/projects/hydrology/vic_gen2/input/routing/fraser/parameters/rvic.domain_fraser_v2.nc 
This domain contains 17731 grid cells inside the watershed

```

## Requirements
`netcdf4`