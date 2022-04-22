import argparse
import csv
from netCDF4 import Dataset
from shapely.geometry import shape, Point
import geojson
from mow.helpers import *
from mow.geo_data_grid_2d.vic import VicDataGrid
import warnings

parser = argparse.ArgumentParser(
    "Output a CSV file with the lon lat of the mouth of each watershed"
)
parser.add_argument("rvic_flow_direction", help="an RVIC-netCDF file")
parser.add_argument(
    "geoserver",
    help="a geoserver output file describing the watersheds, a file",
)
parser.add_argument("output", help="the csv file to output the results to")
args = parser.parse_args()
with Dataset(args.rvic_flow_direction, "r") as nc, open(
    args.geoserver
) as f, open(args.output, "w", encoding="UTF8") as x:
    flow_direction = VicDataGrid.from_nc_dataset(nc, "flow_direction")
    grid = VIC_direction_matrix(
        flow_direction.lat_step, flow_direction.lon_step
    )
    distance = max(flow_direction.lon_step, flow_direction.lat_step) * -1.2
    writer = csv.writer(x)
    header = ["lon", "lat", "WTRSHDGRPC"]
    writer.writerow(header)
    gj = geojson.load(f)
    for i in gj["features"]:
        flag = False
        visited = set()
        polygon = shape(i.geometry)
        center = polygon.buffer(distance).representative_point()
        try:
            xy = flow_direction.lonlat_to_xy(center.coords[0])
        except:
            warnings.warn("watershed center not in netCDF file")
            continue
        visited.add(xy)
        while True:
            cell_routing = flow_direction.values[xy]
            if cell_routing.mask:
                warnings.warn("watershed center not in netCDF file")
                break
            neighbour = vec_add(xy, grid[int(cell_routing)])
            # if xy = neighbour, then we must be at an outlet
            # when we add an outlet to xy, we will get xy again,
            # therefore, neighbour == xy. If the neighbour is in
            # visited, we have encountered a cycle, and want to
            # stop. There is no mouth, and we mark the flag true
            # to assert that this point of a cycle is not added
            # to the csv file.
            if xy == neighbour:
                break
            if neighbour in visited:
                flag = True
                break
            if flow_direction.is_valid_index(neighbour) and polygon.contains(
                Point(flow_direction.xy_to_lonlat(neighbour))
            ):
                xy = neighbour
            else:
                break
        if not cell_routing.mask and not flag:
            mouth = flow_direction.xy_to_lonlat(xy)
            line = [
                mouth[0].compressed()[0],
                mouth[1].compressed()[0],
                i.properties["WTRSHDGRPD"],
            ]
            writer.writerow(line)
