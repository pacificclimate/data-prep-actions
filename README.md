# Data Preparation Actions

## Purpose

This repository brings together the shell scripts, configuration files, log file outputs, and other ephemera of 
data preparation actions.
Keeping these in a repo has the following purposes and benefits:

1. Record-keeping
2. Easy re-use of scripts, etc., written for different but similar cases
3. Single source for deployment and execution of these scripts

## Security note

**IMPORTANT**

Dangerous combination:

* This is a **publicly visible** repository. 
* You will be placing scripts here that run against our secure networks and databases. 

Therefore:

* Do **NOT** include usernames or passwords in the scripts. 
* Instead use environment variables which you set only locally when executing the scripts.

## Organization

Repo contents are organized by _actions_. The term "action" is loosely defined, but it encompasses the processing of a 
specific group of files with a specific goal in mind. 

**Example action**: To form climatological means of CMIP5 output files and index them in the Climate Explorer 
modelmeta database (`ce_meta`). This description would form part (or all) of the `DESCRIPTION.md` file for that action.
This action would be composed of the following sub-actions:

* Convert metadata: Fix any missing or non-compliant metadata to make the files processable. (Unlikely
to be necessary for CMIP5 outputs, but often necessary with other datasets.)
* Form climatological means: Execution of the climatological mean-forming code is handled by the jobqueueing tool, but
adding files to be processed to the job queue usually involves a script to find and add the files. That script should
be placed here. 
* Index: Run the indexer on the output climatological means files.
* Fix up modelmeta database: Some indexing operations will create records with filenames that are not quite correct.
For example, if the file to be indexed is copied to local scratch disk before being processed by the indexer, then the
filepath recorded by the indexer will be the scratch location. That needs to be modified so that the database records 
point to the actual long-term location of the files.

Actions are organized under the `actions` subdirectory as follows. Only subdirectories for sub-actions actually done
need to be included.

```
    actions/
        <action-name>/
            DESCRIPTION.md
            convert-metadata/
                # updates.yaml file(s) for update_metadata script
                # shell script(s) for invoking updata_metadata
                # log files generated
            climo-means/
                # shell script(s) for adding files to jobqueue
                # log files generated
            index/
                # shell script(s) for invoking index_netcdf
                # log files generated
            modelmeta-fixup/
                # SQL query used to correct the filepath (or other fixup, heaven forbid)
                # log files generated
```

Further subdirectories can be added as needed (and ideally documented here) for additional sub-actions.

## Recommended process

1. _Branch per action_: When starting an action, create a new branch from master. Use the branch to manage the action. 
Merge the branch to master once the action is complete and all desired files have been added to the repo.
A PR may be a convenient way to accomplish this.
2. _Issue per action_: It may also be useful to use issues in this repo to manage the work to be done, i.e., 
the actions to be taken. This would couple neatly with PRs.

## Caution re. large files

Log files can be bulky, so be careful about adding large log files to this repo. 

GitHub [recommends](https://help.github.com/articles/what-is-my-disk-quota/) that repositories be kept under 1 GB, 
and enforces a strict limit of 100 MB per file. For large files, either store a pointer to our local storage, or use 
[GitHub Large File Storage](https://help.github.com/articles/versioning-large-files/).

Also note that if large files are stored in this repo, then they are replicated wherever this repo is cloned.
That may not be desirable.
