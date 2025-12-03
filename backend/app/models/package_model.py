from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from backend.app.database.db import Base

class Package(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, index=True)
    descripcion = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_expiracion = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    
    # Relación con parts
    parts = relationship("PackagePart", back_populates="package", cascade="all, delete-orphan")