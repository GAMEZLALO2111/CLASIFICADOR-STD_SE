# backend/app/models/partnumber.py

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class PartNumber(Base):
    __tablename__ = "partnumbers"

    id = Column(Integer, primary_key=True, index=True)

    fg_id = Column(Integer, ForeignKey("fg.id", ondelete="CASCADE"))

    numero_parte = Column(String, nullable=False)
    espesor = Column(Float)
    sheet_x = Column(Float)
    sheet_y = Column(Float)

    estaciones = Column(String)   # guardaremos JSON string
    tools = Column(String)        # JSON string

    sym = Column(Integer)
    runtime_min = Column(Float)
    uph = Column(Float)
