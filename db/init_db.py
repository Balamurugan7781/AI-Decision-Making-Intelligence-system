from db.database import engine
from db.models import Base


def initialise_db():

    print("Dropping Existing database...")
    Base.metadata.drop_all(bind=engine)

    print("Creating new database...")
    Base.metadata.create_all(bind=engine)
    print("Database Created Successfully")



if __name__ == "__main__":
    initialise_db()
    print(Base.metadata.tables.keys())