from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class PackagePart(Base):
    __tablename__ = "package_parts"

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, ForeignKey("packages.id", ondelete="CASCADE"), nullable=False)
    
    # Info del archivo
    part_filename = Column(String, nullable=False)  # "TYEH-1171206_01-SW"
    cantidad = Column(Integer, nullable=False)
    
    # Snapshot completo del parser (JSON)
    parsed_data = Column(JSON, nullable=False)
    
    # Relación
    package = relationship("Package", back_populates="parts")