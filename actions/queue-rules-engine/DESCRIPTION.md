# Queue Plan2Adapt Rules Engine

This simple script generates one `pbs` file for each of the plan2adapt regions. Each `pbs` file tells the queue to run the plan2adapt rules engine for its region for the 2020s, 2050s, and 2080s, and saves the result as files named `region_2020`. `region_2050` and `region_2080`.

To use the script, just fill in the variables at the top:

* *connection*: a database DSN string
* *log_dir*: where job logs should be written to. Directory on storage ending in a /
* *venv*: a directory on storage where the p2a-rules-engine is installed and a virtual environment named `venv` is set up.
* *data*: a directory on storage to copy data to when it is finished, ending in a /
* *ensemble*: database ensemble containing necessary datasets

Then just run the script. You can submit the resulting jobfiles in a batch:
```
for file in *.pbs ; do qsub $file ; done
```