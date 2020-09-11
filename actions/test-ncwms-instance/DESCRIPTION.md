# Test an ncWMS instance

## Purpose
This script tests a running, configured ncWMS instance. It connects to a database (provided
as an argument) and gets a list of files and variables corresponding to the ensemble
specified by the user. It then makes one of each of the following requests for each
variable in each file:
* `GetCapabilities`
* `GetFeatureInfo`
* `GetMap`

It prints out a summary of how many requests failed, and which files had failures. It doesn't
check the content of requests; if `GetMap` returns a blank map, this script will not notice. It
doesn't worry about data correctness, just whether ncWMS can access the data and respond without
HTTP errors.

Finally it makes a `GetLegendGraphic` request against the server as a whole. `GetLegendGraphic`
requests *can* be made against individual datasets, but the PDP doesn't do this, so it isn't tested.

## NCWMS version
The `--version` argument can be used to specify ncWMS1 or ncWMS 2 formatted requests, which 
affects the default pallette names. 

For non-dynamic ncWMS installations, the script will attempt to access each dataset using it
`unique_id` in the database.

For dynamic ncWMS installation, specify a prefix with the `--prefix` argument, and the script
will attempt to access the dataset as `prefix/full-filepath`.


## Stress Testing
This script typically takes a couple hours to chew through all the requests;
it's intended as a shakedown for new ncWMS instances. For routine testing of an existant
instance, you might want to hit only 10% of the files, or something.

By default, it requsts a 100x100 pixel map. To use as a stress-test, you can change 
the size of the request image to 1024 x 1024 (the ncWMS maximum). If running multiple
copies of the script at once, randomize the file order to prevent ncWMS from just
caching the data and getting off easy.

## Usage

```
python ncWMS-check.py -d postgresql://user:password@server.org:port/database -s http://ncwms_instance.org:port/base ensemble_name
```

where: 
* `-d` argument is the postgres DSN of the modelmeta-formatted database containing the list of files to check
* `-s` argument is the URL of the ncWMS server up to but not including the question mark immediately before the parameters
* `ensemble` is the name of the database ensemble containing the files of interest

Note that the number of errors reported by the script can exceeed the number of files for which errors
were encountered, if files have more than one error.