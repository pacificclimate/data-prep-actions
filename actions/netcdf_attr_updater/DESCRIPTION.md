# NetCDF Attribute Editor
This script is for updating attributes in NetCDF files. It supports searching for variables with specific attributes and applying string replacements or value corrections. It iterates through a csv of filepaths and modifies the files in place using NCO tools.

Originally designed to correct CF-style `cell_methods`, it can be adapted for any variable attribute update.
# Change md5sum
Originally developed by Eric.
Recalculates and updates the first_1mib_md5sum field in the database for files that have been edited in-place, recognizing  modifications without needing to re re-index/re-associate anything!
Ideal for minor edits (e.g., updating long_name, units, or other non-indexed attributes)