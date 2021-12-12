from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from config import DB_URI


engine = create_engine(DB_URI)
session = Session(engine, future=True)
