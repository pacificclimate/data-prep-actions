# Make Watershed Basins

## Purpose
Watersheds in British Columbia can be organized into "basins" - a basin being either an entire river, or "Coast" as sort of a catchall for small rivers that flow to the coast without joining a larger water system. These scripts generate shapefiles that describe basins, given a shapefile of all the watersheds and a list of which watershed is in which basin.

## virtual environment

You will need to set up a virtual environment with python GDAL and shapely installed.

## concave_hull.py

Run this script first. It converts all multipolygon watersheds (coastal areas with lots of islands) into single-polygon watersheds, leaving polygonal watersheds and all watershed attributes unchanged. If you don't do this, the next step will get bogged down in errors about invalid geometries, which are caused by the features with literally thousands of islands.

### Selecting a ratio
The `ratio` argument is passed directly to shapely's `concave_hull` function. Ratio must be between 0 and 1; higher ratios result in fewer points in the generated shape.

You might think that more points -  a higher resolution geometry -  is ideal, but given the way the concave hull algorithm works, this is not always the case. You might imagine concave hull as attempting to shrinkwrap all the individual points with one sheet of shrinkwrap with the smallest possible amount of air inside the shrink wrap. Lower ratios corresponding to giving the algorithm longer sheets of shrinkwrap. 

Imagine you have three points, and concave hull is attempting to shrinkwrap them. You give the algorithm a short piece of shrinkwrap, and it wraps around the outside of the three points, making a triangle. If, instead, you give the algorithm a longer piece of shrink wrap, it might wrap around the outside from point one to point two and from point two to point three, then turn and wrap arond the inside from point three back to point two, and along the inside back to point one. In this case, rather than a triangle, you get the hollow outline of one, a narrow wrapped strip just big enough to contain the three points.

A ratio of .8 was good for the shapefiles included in this directory, but different ratios might be good for different files. You'll have to open your shapefile in QGIS or something to make sure the generated polygons make sense, and rerun with a different ratio if they don't.

This repository includes an example of a poorly selected ratio. ratio-original.png shows the original shapefile (brown) for Haida Gwai. ratio-08.png shows the resulting geometry (yellow) run with a ratio of .8, which came out well. Ratio-01.png shows the resulting geometry (green) run with a ratio of .1. You can see that the large island at the top has become a thin strip around the outside of the region, instead of enclosing the entire region.

### Selecting a name

This argument is only used in logging. When the script reports issues with a region, this is the shapefile attribute it will refer to the region as so a human can investigate. Pick an attribute that is different for each region, like its name.

## merge-basins.py

This script accepts a shapefile full of watersheds and a CSV list of which watershed belongs to which river basin, and outputs a shapefile full of river basins. In order to build a correspondance between the CSV and the shapefile, one column of the CSV should be named to match an attribute of the shapefile, and the name of this attribute supplied as the "key" argument.

This script removes all holes from the basins, even if individual watersheds contain holes.

## Files Processed

watershed-degrees.shp was processed to concave.shp by concave_hull.py. basins.shp was generated from concave.shp with MjrDrain_Formatted.csv as a list of which watershed is in which basin.