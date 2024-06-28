from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modelmeta import DataFile
from nchelpers import CFDataset

dsn = 'postgresql://ce_meta_rw:PASSWORD@db.pcic.uvic.ca:5433/ce_meta'
engine = create_engine(dsn)
Session = sessionmaker(engine)
with Session() as sesh:
    try:
        q = sesh.query(DataFile).filter(DataFile.filename.contains("MBCn")).filter(DataFile.filename.contains("90p"))
        for res in q.all():
            f = res.filename
            print(f"Changing md5sum for {f}")
            with CFDataset(f) as cf:
                sesh.query(DataFile).filter(DataFile.filename == f).update({"first_1mib_md5sum": cf.first_MiB_md5sum})
        sesh.commit()
    except:
        sesh.rollback()
