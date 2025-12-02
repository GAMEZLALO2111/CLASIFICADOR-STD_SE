from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database.db import Base

class FinishGood(Base):
    __tablename__ = "fg"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    partes = relationship("FGPart", back_populates="fg", cascade="all, delete")
