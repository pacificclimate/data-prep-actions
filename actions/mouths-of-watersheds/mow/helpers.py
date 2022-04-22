# This module was copied unmodified from climate-explorer-backend
# and may contain some unused code
import math
import operator

def VIC_direction_matrix(lat_step, lon_step):
    """ Return a VIC direction matrix, which is a matrix indexed by the VIC
    streamflow direction codes 0...9, with the value at index `i` indicating
    the offsets from the data index in a streamflow file required to
    step in that streamflow direction.

    :param lat_step: Difference between two successive latitudes in streamflow
        file. (Only) sign matters.
    :param lon_step: Difference between two successive longitudes in streamflow
        file. (Only) sign matters.
    :return: tuple of offset pairs

    The offsets must account for the sign of the step in the lat and lon
    dimensions in the streamflow file.
    For example, in a streamflow file with lat and lon both increasing with
    increasing index, the offset to step northeast is [1, 1].

    Note that argument order is (lat, lon), not (lon, lat).
    """
    base = (
        (0, 0),  # filler - 0 is not used in the encoding
        (1, 0),  # 1 = north
        (1, 1),  # 2 = northeast
        (0, 1),  # 3 = east
        (-1, 1),  # 4 = southeast
        (-1, 0),  # 5 = south
        (-1, -1),  # 6 = southwest
        (0, -1),  # 7 = west
        (1, -1),  # 8 = northwest
        (0, 0),  # 9 = outlet
    )
    lat_dir = int(math.copysign(1, lat_step))
    lon_dir = int(math.copysign(1, lon_step))
    return tuple(
        (lat_dir * lat_base, lon_dir * lon_base) for lat_base, lon_base in base
    )

def vec_add(a, b):
    """numpy-style addition for builtin tuples: (1,1)+(2,3) = (3,4)"""
    return tuple(map(operator.add, a, b))

def neighbours(cell):
    """Return all neighbours of `cell`: all cells with an x or y offset
    of +/-1"""
    return (vec_add(cell, offset) for offset in neighbour_offsets)
