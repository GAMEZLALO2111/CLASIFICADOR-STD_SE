from sqlalchemy import Column, Integer, String
from backend.app.database.db import Base

class FG(Base):
    __tablename__ = "fg"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
