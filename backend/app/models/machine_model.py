from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.db import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con template
    template_id = Column(Integer, ForeignKey("machine_templates.id"), nullable=False)
    template = relationship("MachineTemplate")
    
    # Especificaciones variables
    modelo = Column(String, nullable=False)  # "EMK6120", "EMK3510", etc.
    nombre = Column(String, unique=True, nullable=False, index=True)  # "T-101", "T-103", etc.
    
    # Mesa de trabajo
    mesa_x = Column(Integer)  # mm
    mesa_y = Column(Integer)  # mm
    
    # Rango de espesores
    thickness_min = Column(Float)  # mm
    thickness_max = Column(Float)  # mm
    
    # Estaciones dañadas (específicas de esta máquina)
    estaciones_dañadas = Column(JSON, default=[])  # [12, 34, 45]
    
    # Estado
    activa = Column(Integer, default=1)  # 1=activa, 0=inactiva