from db.database import engine
from db.models import Base

def initialise_db():
    Base.metadata.create_all(bind=engine)
    print("Database Created Successfully")



if __name__ == "__main__":
    initialise_db()
    print(Base.metadata.tables.keys())