# merge-basins.py
# accepts a shapefile of polygonal watershed regions and a CSV with one
# column for watershed code or name and one column for the name of the
# basin it is part of.
# Outputs a new shapefile containing basin "regions" each of which is constructed
# by merging all watersheds in that basin.

import argparse
from osgeo import ogr
import logging, traceback, csv
from shapely import from_wkt, to_wkt, union, is_valid, make_valid, Polygon, MultiPolygon

parser = argparse.ArgumentParser(
    "Merge watershed from a shapefile to make larger basins"
)
parser.add_argument("watersheds", help="an input shapefile")
parser.add_argument("basins", help="csv correlating watersheds to basins")
parser.add_argument(
    "key", help="identifying attribute in the input shapefile that matches CSV"
)
parser.add_argument("output", help="file to write basin shapefile to")

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
    # load csv and make dictionary of basin membership
    logger.info("Loading CSV")
    membership = {}
    with open(args.basins) as basinfile:
        reader = csv.DictReader(basinfile)
        for row in reader:
            membership[row[args.key]] = row["Basin"]

    # load shapefile
    logger.info("Loading shapefile")

    driver = ogr.GetDriverByName("ESRI Shapefile")
    watersheds = driver.Open(args.watersheds)

    if watersheds is None:
        raise Exception("Could not open shapefile {}".format(args.shapefile))

    # see if the attribute we are looking for is present
    logger.info("Checking shapefile attributes")
    layer = watersheds.GetLayer(0)  # shapefiles have only one layer
    layer_definition = layer.GetLayerDefn()
    fields = []

    for i in range(layer_definition.GetFieldCount()):
        fields.append(layer_definition.GetFieldDefn(i).GetName())

    if args.key not in fields:
        raise Exception("Attribute {} not present in shapefile".format(args.key))

    key_index = fields.index(args.key)

    # create output files
    logger.info("Creating output files")
    output = driver.CreateDataSource(args.output)
    out_layer = output.CreateLayer(layer.GetName())
    out_layer.CreateField(ogr.FieldDefn("NAME", ogr.OFTString))
    out_layer.CreateField(ogr.FieldDefn("WATERSH", ogr.OFTInteger))

    # step through the watersheds and create each basin
    basins = {}
    logger.info("Building basins")
    for feature in layer:
        watershed_key = feature.GetField(key_index)
        basin = membership[watershed_key]
        logger.info(
            "Now processing watershed {} for basin {}".format(watershed_key, basin)
        )

        geom = feature.GetGeometryRef()
        geom = geom.ExportToWkt()
        if not is_valid(from_wkt(geom)):
            logger.warning("Watershed {} is self-intersecting".format(watershed_key))
            logger.warning("Attempting to fix watershed with shapely buffer")
            logger.warning("Please manually check results.")
            detangled = from_wkt(geom)
            detangled = make_valid(detangled)
            assert is_valid(detangled)
            geom = to_wkt(detangled)
            logger.warn("Here are the buffered results: {}".format(geom))

        if basin in basins:
            logger.info("Adding watershed {} to basin {}".format(watershed_key, basin))
            old = from_wkt(basins[basin]["geometry"])
            if not is_valid(old):
                logger.warning("Current {} basin is not valid".format(basin))
                old = make_valid(old)
                assert is_valid(old)
            combined = union(old, from_wkt(geom))
            if not is_valid(combined):
                logging.warning("Using make_valid on combined geometry")
                combined = make_valid(combined)
                assert is_valid(combined)
            basins[basin]["geometry"] = to_wkt(combined)
            basins[basin]["watershed"] = basins[basin]["watersheds"] + 1

        else:
            logger.info(
                "Beginning basin {} with watershed {}".format(basin, watershed_key)
            )
            basins[basin] = {"watersheds": 1, "geometry": geom}

    logger.info("Outputting basins")
    num_basins = 0
    for basin in basins:
        logger.info("Writing basin {}".format(basin))
        output_feature = ogr.Feature(out_layer.GetLayerDefn())
        output_feature.SetField("NAME", basin)
        output_feature.SetField("WATERSH", basins[basin]["watersheds"])

        geom = basins[basin]["geometry"]

        # remove holes from basin
        if "MULTIPOLYGON" in geom:
            logger.info("Removing holes from {} multipolygon".format(basin))
            polygons = []
            for polygon in from_wkt(geom).geoms:
                polygons.append(Polygon(polygon.exterior.coords))
            no_holes = MultiPolygon(polygons)
            output_feature.SetGeometry(ogr.CreateGeometryFromWkt(to_wkt(no_holes)))

        elif "POLYGON" in geom:
            logger.info("Removing holes from {} polygon".format(basin))
            no_holes = Polygon(from_wkt(geom).exterior.coords)
            output_feature.SetGeometry(ogr.CreateGeometryFromWkt(to_wkt(no_holes)))

        out_layer.CreateFeature(output_feature)
        num_basins = num_basins + 1


except Exception as e:
    logger.error(traceback.format_exc())

finally:
    logger.info("Wrote {} basins".format(num_basins))
