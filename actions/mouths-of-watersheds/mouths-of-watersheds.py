import argparse
import csv
from netCDF4 import Dataset
from shapely.geometry import shape
import geojson
from mow.helpers import *
from mow.geo_data_grid_2d.vic import VicDataGrid

parser = argparse.ArgumentParser('Output a CSV file with the lon lat of the mouth of each watershed')
parser.add_argument('nc', help='an RVIC-netCDF file')
parser.add_argument('geojson', help='a geoserver output file describing the watersheds')
parser.add_argument('csv', help='the csv file to output the results to')
args = parser.parse_args()
nc = Dataset(args.nc, "r")
flow_direction = VicDataGrid.from_nc_dataset(nc, "flow_direction")
grid = VIC_direction_matrix(flow_direction.lat_step, flow_direction.lon_step) 

with open(args.geojson) as f:
    with open(args.csv, 'w', encoding='UTF8') as x:
        writer = csv.writer(x)
        header = ['lon', 'lat', 'WTRSHDGRPC']
        writer.writerow(header)
        gj = geojson.load(f)
        for i in gj['features']:
            visited = set()
            center = shape(i.geometry).centroid
            try:
                xy = flow_direction.lonlat_to_xy(center.coords[0])
            except:
                continue
            visited.add(xy)
            while True:
                cell_routing = flow_direction.values[xy]
                if cell_routing.mask:
                    break
                neighbour = vec_add(xy, grid[int(cell_routing)])
                #if xy = neighbour, then we must be at an outlet
                if xy == neighbour:
                    break
                if neighbour in visited:
                    cell_routing.mask = True
                    break
                if flow_direction.is_valid_index(neighbour):
                    xy = neighbour
                else:
                    break
            if not cell_routing.mask:
                mouth = flow_direction.xy_to_lonlat(xy)
                line = [mouth[0].compressed()[0], mouth[1].compressed()[0], i.properties['WTRSHDGRPD']]
                writer.writerow(line)

nc.close()
