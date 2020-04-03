''' This script accepts one or more CSV files that contain timeseries, with
a column of timestamps and one or more columns of timed measurements.
It outputs a file that has a column of timestamps and multiple columns
of timed measurements.

It does some format tinkering, to get the input values into the expected
format: 
* all non-numeric values are quoted in the output
* dates are formatted Y/M/D'''

import argparse
import csv

date_att = "Date"

parser = argparse.ArgumentParser('Merge multiple timeseries CSVs')
parser.add_argument('files', nargs='+', help='files to process')
parser.add_argument('-o', '--output_file', help='file to output to')
args = parser.parse_args()

columns = [date_att]
rows = []

# collate eisting files
for file in args.files:
    print("Now parsing {}".format(file))
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        if not date_att in reader.fieldnames:
            raise Exception("  No date field found!")
        for column in reader.fieldnames:
            if column in columns:
                if not column == date_att:
                    raise Exception("  Repeating column: ".format(column))
            else:
                columns.append(column)
        
        for input_row in reader:
            if not input_row[date_att]:
                raise Exception("  Row missing timestamp")
            
            merged = False
            
            # convert all non-date attributes to floats.
            for att in input_row:
                if not att == date_att:
                    input_row[att] = float(input_row[att])
            
            for row in rows:
                if input_row[date_att] == row[date_att]:
                    row.update(input_row)
                    merged = True
            if not merged:
                rows.append(input_row)
                
# sort by date
rows.sort(key=lambda r: r[date_att])

# create a csv.Dialect object to describe the way we want the file
# formatted.
csv.register_dialect('pdp', quoting=csv.QUOTE_NONNUMERIC)


# output new file
with open(args.output_file, 'w') as outfile:
    print("Now writing to {}".format(args.output_file))
    writer = csv.DictWriter(outfile, dialect='pdp', fieldnames=columns)
    writer.writeheader()
    for outrow in rows:
        # fix formatting - dates need to be Y/M/D
        outrow[date_att] = outrow[date_att].replace("-", "/")
        writer.writerow(outrow)
                
            
            