# disaggregates a particular file into individual files based on 
# climatology and statistical measure

import argparse
from netCDF4 import Dataset
import numpy
import csv
from datetime import date
import math
import re

parser = argparse.ArgumentParser(description='disaggregate a netCDF indicator file')
parser.add_argument('netcdf', help='a netCDF file to split')
parser.add_argument('grid', help='a CSV that maps between numbered grid cells and latlon')

args=parser.parse_args()

with Dataset(args.netcdf, "r") as input:
    
    #check dataset format - general number and presence of variables
    expected_variables = ["time.int", "cell", "var_5"]
    for ev in expected_variables:
        if ev not in input.variables:
            raise Exception("Did not find expected variable {}".format(ev))
    
    resolution_variables = ["month", "day"]

    indicators = []
    resolution = "year"
    for v in input.variables:
        if v in resolution_variables:
            if resolution == "year":
                resolution = v
            else:
                raise Exception("Multiple time resolution variables: {}, {}".format(v, resolution))
        elif not v in expected_variables:
            indicators.append(v)
    
    if len(indicators) == 0:
        raise Exception("No possible indicator variables found")
    elif len(indicators) == 1:
        indicator = indicators[0]
        print("Indicator is {}".format(indicator))
    else:
        raise Exception("Multiple possible indicators found: {}".format(indicators))
    
    print("Time resolution is {}".format(resolution))

    def check_variable_expectations(var_name, length, long_name):
        #checks that a particular variable has the format we expect.
        var = input.variables[var_name]
        if len(var[:]) != length:
            raise Exception("Unexpected length of {} variable. Expected {}, found {}".format(var_name, length, len(var[:])))
        if var.long_name != long_name:
            raise Exception("Unexpected long_name for variable {}. Expected {}, found {}".format(var_name, long_name, var.long_name))
    
    check_variable_expectations("var_5", 5, "parameters: 1-mean, 2-sd, 3-n, 4-min, 5-max")
    check_variable_expectations("time.int", 4, "1:1971-2000 ; 2:2010-2039 ; 3:2040-2069 ; 4:2070-2099")
    check_variable_expectations("cell", 11794, "Grid cell number")
    if resolution == "month":
        check_variable_expectations("month", 12, "calendar month")
    elif resolution == "day":
        check_variable_expectations("day", 366, "calendary day: 366 days")
    
    
    #TODO: check that the variable has the axes in the right order!
    def get_dimension_name(dim):
        return dim.name
    indicator_dimensions = list(map(get_dimension_name, input.variables[indicator].get_dims()))
    expected_indicator_dimensions = ["var_5"]
    if resolution != "year":
        expected_indicator_dimensions.append(resolution)
    expected_indicator_dimensions.append("time.int")
    expected_indicator_dimensions.append("cell")

    if indicator_dimensions != expected_indicator_dimensions:
        raise Exception("Variable {} dimensions in unexpected order. Expected {} got {}".format(indicator, expected_indicator_dimensions, indicator_dimensions))
    
    input_atts = input.__dict__
    
    #get lat and lon info and cell index out of the csv file
    with open(args.grid) as grid:
        csv = csv.DictReader(grid)
        latitudes = set()
        longitudes = set()
        rows = set()
        cols = set()
        index_tuples = []
    
        for row in csv:
            latitudes.add(float(row["lat"]))
            longitudes.add(float(row["lon"]))
            rows.add(int(row["row"]))
            cols.add(int(row["col"]))
            index_tuples.append((int(row["cell_ind"]),( int(row["row"]), int(row["col"]))))
    
        print("rows: {} cols: {} lats: {} lons: {}".format(len(rows), len(cols), len(latitudes), len(longitudes)))
        rows = list(rows)
        rows.sort()
        row_offset = rows[0]
        cols = list(cols)
        cols.sort()
        col_offset = cols[0]
        print("rows runs from {} to {}, cols runs from {} to {}".format(rows[0], rows[-1], cols[0], cols[-1]))
        
        def check_spatial_intervals(axis_set, axis_name):
            axis = list(axis_set)
            axis.sort()
            interval = axis[1] - axis[0]
            for i in range(1, len(axis)):
                if axis[i] - axis[i-1] != interval:
                    raise Exception("Unexpected interval in {} axis between {] and {}".format(axis_name, axis[i], axis[i-1]))
            return numpy.array(axis)
            
        latitudes = check_spatial_intervals(latitudes, "latitude")
        longitudes = check_spatial_intervals(longitudes, "longitudes")
        
        def second_element(l):
            return l[1]
        
        index_tuples.append((0,(0,0))) #dummy entry - data indexing begins at 1
        index_tuples.sort()
        for i in range(len(index_tuples)):
            if index_tuples[i][0] != i:
                raise Exception("cell index is missing an entry for {}".format(i-1))
        index_tuples = list(map(second_element, index_tuples))
    

    # the input files look good, now to split the netCDF
    # we want indicator[parameter, time, *] to each end up in a separate file.
    # loop over parameter and time. 
    var_5 = input.variables["var_5"]
    stats = ['mean', 'sd', 'n', 'min', 'max']
    
    time_int = input.variables["time.int"]
    climo_starts = [1971, 2010, 2040, 2070]
    climo_ends = [2000, 2039, 2069, 2099]

    for stat in range(len(var_5[:])):
        print("  Now processing {} {}".format(stat, stats[stat]))
        
        for climo in range(len(time_int[:])):
            print ("    Now processing {} {}-{}".format(climo, climo_starts[climo], climo_ends[climo]))
            
            freq_abbreviation = {"year": "a", "month": "m"}[resolution]
            filename = "{}_{}Clim{}_BCCAQv2_{}_historical-{}_{}_{}0101-{}1231_{}.nc".format(indicator, 
                                              freq_abbreviation,
                                              stats[stat].capitalize(),
                                              input_atts["Model"],
                                              input_atts["RCP scenario"],
                                              input_atts["Model run"],
                                              climo_starts[climo],
                                              climo_ends[climo],
                                              input_atts["Major drainage"]
                                              )
            print("      {}".format(filename))
            
            with Dataset(filename, "w", format="NETCDF4") as output:
                timelen = {"year": 1, "month": 12, "day": 366}[resolution]
                
                lat = output.createDimension("lat", len(latitudes))
                lon = output.createDimension("lon", len(longitudes))
                time = output.createDimension("time", timelen)
                bnds = output.createDimension("bnds", 2)
                
                lats = output.createVariable("lat", "f8", ("lat"))
                lats.standard_name = "latitude"
                lats.long_name = "latitude"
                lats.units = "degrees_north"
                lats.axis = "Y"
                
                lons = output.createVariable("lon", "f8", ("lon"))
                lons.standard_name = "longitude"
                lons.long_name = "longitude"
                lons.units = "degrees_east"
                lons.axis = "X"
                
                time = output.createVariable("time", "f8", ("time"))
                time.standard_name = "time"
                time.long_name = "time"
                time.units = "days since 1950-01-01"
                time.axis = "T"
                time.calendar = "standard"
                time.climatology = "climatology_bnds"
                
                climatology_bnds = output.createVariable("climatology_bnds", "f8", ("time", "bnds"))
                climatology_bnds.calendar = "standard"
                climatology_bnds.units = "days since 1950-01-01"
                
                indicator_var = output.createVariable(indicator, "f8", ("time", "lat", "lon"), fill_value=32767)
                indicator_var.standard_name = indicator
                indicator_var.long_name = input.variables[indicator].long_name
                indicator_var.units = input.variables[indicator].units
                
                lats[:] = latitudes
                lons[:] = longitudes
                
                def days_since_1950(year, month, day):
                    days = date(int(year), int(month), int(day)) - date(1950, 1, 1)
                    days = days.days
                    return days
                
                start_year = climo_starts[climo]
                end_year = climo_ends[climo]
                mid_year = (start_year + end_year)/2
                if resolution == "year":
                    time[:] = numpy.array([days_since_1950(mid_year, 7, 2)])
                    climatology_bnds[:] = numpy.array([
                        days_since_1950(start_year, 1, 1),
                        days_since_1950(end_year, 12, 31)])
                
                elif resolution == "month":
                    times = []
                    bounds = []
                    month_lengths = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    for month in range(1, 13):
                        times.append(days_since_1950(mid_year, month, 15))
                        bounds.append(days_since_1950(start_year, month, 1))
                        bounds.append(days_since_1950(end_year, month, month_lengths[month]))
                    time[:] = numpy.array(times)
                    climatology_bnds[:] = numpy.array(bounds).reshape(timelen, 2)
                
                elif resolution == "year":
                    raise Exception("yearly data translation is not implemented yet")
                
                data = numpy.full((timelen, len(latitudes), len(longitudes)), 32767)
                
                #translate data from numbered cells to latitude and longitude
                if resolution == "year":
                    slice = input.variables[indicator][:]
                    slice = slice[stat]
                    slice = slice[climo]
                    for i in range(len(index_tuples)):
                        #skip the fake one
                        if i > 0:
                            tup = index_tuples[i]
                            row = tup[0]
                            col = tup[1]
                            datum = slice[i - 1]
                            data[0, row - row_offset, col - col_offset] = datum
                else:
                    for t in range(timelen):
                        slice = input.variables[indicator][:]
                        slice = slice[stat]
                        slice = slice[t]
                        slice = slice[climo]
                        for i in range(len(index_tuples)):
                            if i > 0:
                                tup = index_tuples[i]
                                row = tup[0]
                                col = tup[1]
                                datum = slice[i - 1]
                                data[t, row - row_offset, col - col_offset] = datum
                
                indicator_var[:] = data

                # translate global metadata on input file into PCIC standards
                # we's just doing the things that will vary by input file here - 
                # it's expected a lot of the metadata will be filled in later
                
                #global data
                output.climo_start_time = "{}-01-01T00:00:00Z".format(start_year)
                output.climo_end_time = "{}-12-31T00:00:00Z".format(end_year)
                output.frequency = "{}Clim{}".format(freq_abbreviation, stats[stat].capitalize())
                output.domain = input_atts["Major drainage"]
                output.creation_date = "{}T-00*00:00Z".format(input_atts["Date"])
                output.title = input_atts["Title"]
                output.history = "{}: disaggregate-netcdfs.py {} {}".format(date.today(), args.netcdf, args.grid)
                
                # GCM model data
                gcm_prefix = "hydromodel__downscaling__GCM__"
                run_strings = re.split("[rip]", input_atts["Model run"])
                output.setncattr("{}realization".format(gcm_prefix), run_strings[1])
                output.setncattr("{}initialization_method".format(gcm_prefix), run_strings[2])
                output.setncattr("{}physics_version".format(gcm_prefix), run_strings[3])
                
                gcm = input_atts["Model"]
                output.setncattr("{}model_id".format(gcm_prefix), gcm)
                gcm_institutions = {
                    "ACCESS1-0": "CSIRO (Commonwealth Scientific and Industrial Research Organisation, Australia), and BOM (Bureau of Meteorology, Australia)",
                    "CanESM2": "CCCma (Canadian Centre for Climate Modelling and Analysis, Victoria, BC, Canada)",
                    "CCSM4": "NCAR (National Center for Atmospheric Research) Boulder, CO, USA",
                    "CNRM-CM5": "CNRM (Centre National de Recherches Meteorologiques, Meteo-France, Toulouse,France) and CERFACS (Centre Europeen de Recherches et de Formation Avancee en Calcul Scientifique, Toulouse, France)",
                    "HadGEM2-ES": "Met Office Hadley Centre, Fitzroy Road, Exeter, Devon, EX1 3PB, UK, (http://www.metoffice.gov.uk)",
                    "MPI-ESM-LR": "Max Planck Institute for Meteorology",
                }
                gcm_institute_ids = {
                    "ACCESS1-0": "CSIRO-BOM",
                    "CanESM2": "CCCma",
                    "CCSM4": "NCAR",
                    "CNRM-CM5": "CNRM-CERFACS",
                    "HadGEM2-ES": "MOHC",
                    "MPI-ESM-LR": "MPI-M",
                }
                output.setncattr("{}institution".format(gcm_prefix), gcm_institutions[gcm])
                output.setncattr("{}institute_id".format(gcm_prefix), gcm_institute_ids[gcm])
                
                experiment = "historical, {}".format(input_atts["RCP scenario"])
                output.setncattr("{}experiment".format(gcm_prefix), experiment)
                output.setncattr("{}experiment_id".format(gcm_prefix), experiment)
    
    
print("done!")
