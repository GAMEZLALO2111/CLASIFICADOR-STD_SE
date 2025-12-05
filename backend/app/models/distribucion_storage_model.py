from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from datetime import datetime, timedelta
from app.database.db import Base

class DistribucionStorage(Base):
    __tablename__ = "distribuciones"
    
    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(Integer, nullable=False)
    package_nombre = Column(String, nullable=False)
    demanda = Column(Integer, nullable=False)
    horas_objetivo = Column(Integer, nullable=False)
    machine_ids = Column(JSON, nullable=False)  # [1, 2, 3]
    
    # Resultado completo
    resultado_json = Column(JSON, nullable=False)
    es_factible = Column(Boolean, default=False)
    
    # Fechas
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=1))
    activa = Column(Boolean, default=True)
