from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.config import CONFIG
from models.db import Base


engine = create_engine(
    CONFIG.DB_CONNECTION_STRING,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,  # reconect after 1 hour
)
session_maker = sessionmaker(bind=engine, expire_on_commit=False)


def create_tables() -> None:
    """
    Creates the database tables by calling `Base.metadata.create_all(engine)`.
    """
    Base.metadata.create_all(engine)
