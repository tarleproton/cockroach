import databases
import sqlalchemy


DATABASE_URL = "postgresql://postgres:88832167@localhost:5432/cockroach"

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL)