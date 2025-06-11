from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modelmeta import DataFile
from nchelpers import CFDataset

dsn = "DSN_STRING"
engine = create_engine(dsn)
Session = sessionmaker(engine)
with Session() as sesh:
    try:
        q = sesh.query(DataFile).filter(DataFile.filename.contains("Ensemble_Averages"))
        for res in q.all():
            f = res.filename
            print(f"Changing md5sum for {f}")
            with CFDataset(f) as cf:
                sesh.query(DataFile).filter(DataFile.filename == f).update(
                    {"first_1mib_md5sum": cf.first_MiB_md5sum}
                )
        sesh.commit()
    except:
        sesh.rollback()
