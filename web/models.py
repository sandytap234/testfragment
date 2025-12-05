from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    auth_token = Column(String, unique=True)

def init_db(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)