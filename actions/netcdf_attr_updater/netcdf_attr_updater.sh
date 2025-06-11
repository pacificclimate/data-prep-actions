#!/bin/bash

csv_file="sd_files_to_update.csv"

while IFS= read -r nc_file; do

    # Extract all variable names with 'cell_methods' attribute
    variables=$(ncks -m "$nc_file" | grep 'cell_methods' | cut -d ' ' -f 1 | uniq)

    for var in $variables; do
        
        # Extract the current 'cell_methods' attribute for the variable
        cell_methods=$(ncdump -h "$nc_file" | grep "${var}:cell_methods" | cut -d '"' -f 2)
       
        # Check if 'standard deviation' is part of the 'cell_methods' string
        if [[ "$cell_methods" == *"standard deviation"* ]]; then
            new_cell_methods="${cell_methods/standard deviation/standard_deviation}"
            ncatted -a cell_methods,$var,m,c,"$new_cell_methods" "$nc_file"
           
        fi
    done
done < "$csv_file"