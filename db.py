import databases
import sqlalchemy

metadata = sqlalchemy.MetaData()
database = databases.Database("sqlite:///cockroach.db")
engine = sqlalchemy.create_engine("sqlite:///cockroach.db")