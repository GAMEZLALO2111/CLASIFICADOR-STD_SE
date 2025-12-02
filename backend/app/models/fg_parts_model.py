from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.db import Base

class FGPart(Base):
    __tablename__ = "fg_parts"

    id = Column(Integer, primary_key=True, index=True)
    
    fg_id = Column(Integer, ForeignKey("fg.id"), nullable=False)
    part_number = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)

    # Relación opcional (si quieres jalar datos del FG)
    fg = relationship("FinishGood", back_populates="partes")
