import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from config import DB_HOST, DB_PASS, DB_USER, DATABASE

# connect to the DB
engine = create_engine('mysql+pymysql://' + DB_USER + ':' + DB_PASS + '@' + DB_HOST + '/' + DATABASE,
                       convert_unicode=True, pool_recycle=3600, pool_size=10, echo=False)

print(engine)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = Session()
Base = declarative_base()


# Define the table


class FilesDropped(Base):
    __tablename__ = 'files_dropped'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    mob_id = Column(String(255), primary_key=True)
    file_path = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=False)  # duration is stored in seconds
    date_created = Column(DateTime, nullable=False)
    date_modified = Column(DateTime)
    date_found = Column(DateTime)
    date_scheduled = Column(DateTime)
    date_archived = Column(DateTime)
    date_removed = Column(DateTime)
    display_name = Column(String(255))
    job_uri = Column(String(255))

    def __init__(self, mob_id, file_path, duration, date_created, date_modified, display_name):
        self.mob_id = mob_id
        self.file_path = file_path
        self.duration = duration
        self.date_created = date_created
        self.date_modified = date_modified
        self.display_name = display_name
        self.date_found = datetime.datetime.utcnow()

Base.metadata.create_all(engine)
