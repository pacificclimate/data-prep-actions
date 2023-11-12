# This script reads a shapefile and outputs a version where all multipolygon
# features have been replaced by a single polygon representing the concave hull
# of the original shape. All feature attributes are unchanged.

# This is intended for use with the BC Freshwater Atlas's very detailed maps,
# where some watersheds have hundreds of little islands.


import argparse
from osgeo import ogr
import logging, traceback
from shapely import from_wkt, to_wkt, union, concave_hull

parser = argparse.ArgumentParser(
    "Merge watershed from a shapefile to make larger basins"
)
parser.add_argument("input", help="an input shapefile")
parser.add_argument("output", help="an output shapefile")
parser.add_argument("ratio", help="number between 0 and 1, higher = less points")
parser.add_argument(
    "name", help="name of the attribute to use in troubleshooting reports"
)

args = parser.parse_args()

# set up logging
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

try:
    # load input shapefile
    logger.info("Loading input files")

    driver = ogr.GetDriverByName("ESRI Shapefile")
    input = driver.Open(args.input)

    if input is None:
        raise Exception("Could not open shapefile {}".format(args.input))

    in_layer = input.GetLayer(0)  # shapefiles have only one layer
    in_layer_definition = in_layer.GetLayerDefn()

    # create output files
    logger.info("Creating output files")
    output = driver.CreateDataSource(args.output)
    out_layer = output.CreateLayer(in_layer.GetName())

    # copy all the fields present in the old file to the new one.
    for i in range(0, in_layer_definition.GetFieldCount()):
        out_layer.CreateField(in_layer_definition.GetFieldDefn(i))

    hulled = 0
    # copy each feature to the new file.
    for in_feature in in_layer:
        out_feature = ogr.Feature(out_layer.GetLayerDefn())

        for i in range(0, out_layer.GetLayerDefn().GetFieldCount()):
            out_field = out_layer.GetLayerDefn().GetFieldDefn(i)
            field_name = out_field.GetName()
            if field_name == args.name:
                logger.info("Copying {}".format(in_feature.GetField(i)))

            out_feature.SetField(
                out_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef(),
                in_feature.GetField(i),
            )

        in_geom = in_feature.GetGeometryRef()
        geom = in_geom.ExportToWkt()
        if "MULTIPOLYGON" in geom:
            # convert geometry to shapely, calculate concave hull, and convert it back
            logger.info("Calculating concave hull")
            con_hull = to_wkt(concave_hull(from_wkt(geom), args.ratio))
            out_feature.SetGeometry(ogr.CreateGeometryFromWkt(con_hull))
            hulled = hulled + 1
        else:
            logger.info("Feature is not a multipolygon, left unchanged")
            out_feature.SetGeometry(in_geom.Clone())

        out_layer.CreateFeature(out_feature)
        out_feature = None


except Exception as e:
    logger.error(traceback.format_exc())

finally:
    logger.info("Finished - calculated concave hulls of {} features".format(hulled))
