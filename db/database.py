# This is for creating connections with the database using SQLAlchemy.


from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, declarative_base
import os


# Project paths


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)
Database_path = os.path.join(DATA_DIR, "business.db")
database_url = f"sqlite:///{Database_path}"

# Creating SQLAlchemy engine and session
engine = create_engine(database_url, connect_args={"check_same_thread": False})

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind = engine)

# Declarative Base....

Base = declarative_base()


# FastAPI DB dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

