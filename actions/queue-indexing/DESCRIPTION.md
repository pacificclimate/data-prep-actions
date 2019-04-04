# Queue File Indexing Jobs

## Purpose

The script in this archive can be used to processing modelmeta indexing jobs with the
pbs queue. This may be helpful if indexing very large files, since the queue can run
several jobs in parallel.

This archive contains a pbs job file template and a queueing script. The queueing script use the template to make a job file for each file in a directory, submits the job files to the queue, and deletes the job file.

Each job, when run by the queue, will copy its file to the job's working directory. It will then index the local copy of the file, since data access is faster when working from local storage. Then the script deletes the local copy of the file and indexes the file again in its canonical location. This second indexing of the file will update the location in the database to the true location, but since the indexing script checks to see if a file has changed since the last time it was indexed, it won't read the entire file or redo the time-consuming calculations.

### A Warning About Database Connections
Each indexing job requires its own database connection. Running jobs in parallel can use up all available database connections and block anything else from using the database. Talk to your friendly local sysadmin about limiting how many of your jobs can be run at once if running out of database connections is a possibility.

## Procedure

### 1. Create modelmeta virtual environment
Build the correct version of modelmeta for the database in question in a virtual environment somewhere acessible to the queue, such as in your home directory on storage. Name the virtual environment directory "venv" and create it in the top level of the modelmeta directory.

### 2. Configure the template
`template.pbs` is a template for the job files that will be submitted to the queue. You will need to edit the following variables:
* `database` - put in the DSN address of your database, for example the PDP database is `postgresql://pcic_meta:PASSWORD@monsoon.pcic.uvic.ca/pcic_meta` and climate explorer is `postgresql://ce_meta_rw:PASSWORD@monsoon.pcic.uvic.ca/ce_meta`
* `venv` is the location of the modelmeta instance containing the virtual environment from the previous step.

You should also edit the following PBS options (they look like comments, but anything that starts `#PBS` is a directive to the queuing system):
* `#PBS -o` - a directory output logs will be written to
* `#PBS -e` - a directory error logs will be written to
These can be the same directory.

Optionally, you may wish to edit `#PBS -m abe`, which is the most verbose setting - it emails you when a job is **A**borted, **B**egun, or **E**nded. If you'd like fewer emails, delete one or more of those letters. Emails will be sent to the user you're logged in as @uvic.ca.

Don't change the all-uppercase FILENAME or NUMBER variables; those will be filled in by the queueing script.

### 3. Configure the queueing script
The only thing that needs configured in queue-multi-index.sh is the location of the files to be indexed. Replace `/path/to/files/to/be/indexed/*.nc` with the actual file location.

### 4. Run the queueing script
The script has no arguments; it is just run by typing `./queue-multi-index.sh`.

## Datafiles Processed
BCCAQv2 dataset