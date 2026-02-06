# SCIP data update

Scripts in this folder do two things:
* update metadata by changing the domain from `bccoast+fraser` (the domain used in the old dataset) to `bccoast+ungauged+fraser`
* remove a CRS scalar variable that our indexing scipt did not parse correctly

## update domain

First run the file-renaming bash script in the directory containing the files to rename all of them. While filenames are not load-bearing, leaving them with the wrong domain could be confusing.

```bash
#! /bin/sh

for n in *.nc; do
	x="`echo $n | sed s/bccoast\+fraser/bccoast-ungauged-fraser/`"
	mv "$n" "$x"
done
```

Secondly update domain attributes with `ncatted`:
```bash
for file in ./*.nc ; do echo $file ; ncatted -O -a domain,global,o,c,"bccoast+ungauged+fraser" $file ; ncatted -O -a hydromodel__domain,global,o,c,"bccoast+ungauged+fraser" $file ; ncatted -O -a hydromodel__forcing_domain,global,o,c,"bccoast+ungauged+fraser" $file ; done
```


# remove scalar variable

NetCDF supports "scalar variables" - variables with no data. The CF Standards indicate that a scalar variable is in fact the preferred way to indicate the grid mapping of a dataset - the various mapping parameter are stored in attributes of the variable.

However, in this case, our indexing script did not understand the grid mapping, and I elected to just remove it, since it was WGS 84, the default assumption of the SCIP portal. A python script was needed to remove it, because NCO does not recognize scalar variables as variables that can be edited or deleted.

After removing the CRS variable with the python script, references to it were removed from attributes with `ncatted`.

```bash
for file in ./*.nc ; do python3 remove_variable.py $file crs ; done

for file in ./*.nc ; do echo $file; ncatted -a grid_mapping,,d,, $file $file.tmp ; mv $file.tmp $file; done
```

These tweaks were all these files needed. Their metadata was otherwise perfect.