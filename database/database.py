from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# create an engine to connect with DB
engine = create_engine(
    "sqlite:///db\\factwise_board.db",
    connect_args={"check_same_thread": False},
    echo=True
)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
