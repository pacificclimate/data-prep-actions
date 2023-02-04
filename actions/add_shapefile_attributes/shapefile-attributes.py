from osgeo import ogr
import argparse
import csv

parser = argparse.ArgumentParser('Add data from a CSV to a shapefile')
parser.add_argument('shapefile', help='a shapefile')
parser.add_argument('csv', help='a csv file with one row for each feature in the shapefile')
parser.add_argument('shapefile_key', help='the attribute in the shapefile used to identify each feature')
parser.add_argument('csv_key', help='the attribute in the csv to match with the shapefile attribute')
parser.add_argument('csv_data', help='the attribute in the CSV containing the new data')
parser.add_argument('output', help='filename for output shapefile')

args = parser.parse_args()

# get the new values from the CSV - construct a dict where keys
# are the feature identifiers and values are the new value.
# todo - end script if something amiss with CSV
new_values = dict()
with open(args.csv) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        new_values[row[args.csv_key]] = row[args.csv_data]

driver = ogr.GetDriverByName("ESRI Shapefile")

sf_source = driver.Open(args.shapefile, 0)

if sf_source is None:
    print("Error: could not open shapefile")
else:
    #get the layer - index is always 0 for shapefiles
    layer = sf_source.GetLayer(0)
    print(layer)
    
    layer_definition = layer.GetLayerDefn()

    fields = []
    shape_key_match = False


    #build a list of all user-defined fields
    print("Loading fields in source shapefile")
    for i in range(layer_definition.GetFieldCount()):
        field = dict()
        field["name"] = layer_definition.GetFieldDefn(i).GetName()
        field["type_code"] = layer_definition.GetFieldDefn(i).GetType()
        field["type"] = layer_definition.GetFieldDefn(i).GetFieldTypeName(field["type_code"])
        field["width"] = layer_definition.GetFieldDefn(i).GetWidth()
        field["precision"] = layer_definition.GetFieldDefn(i).GetPrecision()
        
        if field["name"] == args.shapefile_key:
            shape_key_match = True
            print("  Loading field {} - shapefile key".format(field["name"]))
        else:
            print("  Loading field {}".format(field["name"]))

        fields.append(field)
        
    if shape_key_match:
        print("Creating output files.")
        output = driver.CreateDataSource(args.output)
        out_layer = output.CreateLayer(layer.GetName()) #do I need a layer type here?
        
        #copy all the fields present in the old file to the new one.
        for i in range(0, layer_definition.GetFieldCount()):
            out_layer.CreateField(layer_definition.GetFieldDefn(i))
        
        #add the new field. we're assuming they're text.
        out_layer.CreateField(ogr.FieldDefn(args.csv_data, ogr.OFTString))
        
        #write each feature to the file.
        for in_feature in layer:
            output_feature = ogr.Feature(out_layer.GetLayerDefn())
            
            feature_key = ""
            
            #copy the field values from the input layer
            for i in range(0, out_layer.GetLayerDefn().GetFieldCount()):
                out_field = out_layer.GetLayerDefn().GetFieldDefn(i)
                field_name = out_field.GetName()
                if field_name == args.shapefile_key:
                    feature_key = in_feature.GetField(i)
                    
                    #unfortunately, this bit of kludge is required because the CSV file
                    #understands numbers as strings, but the shapefile uses floats
                    #affects the WTRSHDGRPD key
                    if isinstance(feature_key, float):
                        feature_key = '{:.0f}'.format(feature_key)
                    print("  Now writing feature {}".format(feature_key))
                if field_name == args.csv_data and feature_key in new_values:
                    output_feature.SetField(out_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef(),
                                            new_values[feature_key])
                    print("    Set {} to {}".format(field_name, new_values[feature_key]))
                elif field_name == args.csv_data:
                    print("    No new data provided for {}, leaving blank".format(field_name))
                    output_feature.SetField(out_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef(),
                                            "")
                else:
                    output_feature.SetField(out_layer.GetLayerDefn().GetFieldDefn(i).GetNameRef(),
                                            in_feature.GetField(i))
            geom = in_feature.GetGeometryRef()
            output_feature.SetGeometry(geom.Clone())
            # Add new feature to output Layer
            out_layer.CreateFeature(output_feature)
            output_feature = None
        
    else:
        print("Attribute {} not found in input shapefile.".format(args.shapefile_key))


print("done!")



            
        