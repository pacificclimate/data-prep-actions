# Metadata for watershed data files

These files are inputs to the `update_metadata` script and provide metadata needed to format RVIC input files for use with the PCEX system, used with the watershed API endpoint to provide data about the watershed that drains to a specific point.

Area data, which provides the area in meters of each grid square, is extracted from a domain file:

```
cdo selvar,area,lon,lat domain.rvic.peace.20161018.nc area.nc
update_metadata -u area.yaml area.nc
```

Elevation is extracted from a soils file:
```
cdo selvar,elev,lon,lat soils_gen2_20170606.nc elevation.nc
update_metadata -u elevation.yaml elevation.nc
```

Flow direction is extracted from a routing file (and then converted to lowercase):
```
cdo selvar,Flow_Direction,lat,lon bc.rvic.peace.20171019.nc flow-direction_peace.nc.tmp
cdo chname,Flow_Direction,flow_direction flow-direction_peace.nc.tmp flow-direction_peace.nc
update_metadata -y flow_direction.yaml flow-direction_peace.nc 
```

At which point the files should be ready for indexing.
