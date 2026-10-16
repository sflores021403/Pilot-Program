from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from sqlalchemy.engine import URL



DATABASE_URL = URL.create(
    "postgresql+psycopg",
    username="postgres",
    password=os.environ["PILOT_DB_PASSWORD"],
    host="localhost",
    database="pilot_program",
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()