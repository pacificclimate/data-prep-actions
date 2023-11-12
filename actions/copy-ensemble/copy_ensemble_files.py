#! python
'''
copy_ensemble_files - copy all files from one
ensemble to another. The first ensemble is unchanged.

This script assumes:
  * It is used with version 1 of both ensembles
  * Every indexed variable in each file should be added to the ensemble.
  
That is, it is like calling associate_ensembles with no -V argument and
-n always equal to 1.

So it may fail if one of the ensembles is ever present in multiple versions
or if some file variables do not belong in an ensemble (like a crs variable)
'''
from argparse import ArgumentParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import traceback

from mm_cataloguer.associate_ensemble import main, find_ensemble
from modelmeta.v2 import DataFileVariable, EnsembleDataFileVariables, Ensemble, DataFile

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

parser = ArgumentParser(description="Copy files from one ensemble to another in the same database")
parser.add_argument("dsn", help="DSN for database")
parser.add_argument("source", help="ensemble to copy files from")
parser.add_argument("destination", help = "ensemble to copy files to")

args = parser.parse_args() #is there any non-database-connection verification to do here?

engine = create_engine(args.dsn)
Session = sessionmaker(bind=engine)

#get a list of all files in the "source" ensemble
try:
    logger.info("Generating list of files associated with ensemble {}".format(args.source))
    session = Session()
    source_ensemble = find_ensemble(session, args.source, 1)

    files = session.query(DataFile).join(DataFileVariable, EnsembleDataFileVariables, Ensemble)\
        .filter(Ensemble.name == args.source)

    filenames = []
    for f in files:
        filenames.append(f.filename)
except:
    logger.error(traceback.format_exc())
    session.rollback()
    exit()
finally:
    session.close()

#call associate_ensemble on the filename list. 
#we don't need to worry about duplicates - associate_ensemble checks for them.
logger.info("Associating {} files with ensemble {}".format(len(filenames), args.destination))
main(args.dsn, args.destination, 1, False, filenames, None)