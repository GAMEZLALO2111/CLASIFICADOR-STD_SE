from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database.db import Base
from datetime import datetime, timedelta


class EstiloManual(Base):
    """
    Modelo para estilos creados manualmente (sin distribución automática).
    Permite al usuario crear configuraciones de herramientas personalizadas.
    """
    __tablename__ = "estilos_manuales"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)  # Nombre descriptivo del estilo
    machine_id = Column(Integer, nullable=False)  # ID de la máquina asignada
    machine_nombre = Column(String, nullable=False)
    tipo_maquina = Column(String, nullable=False)
    
    # Parts que el usuario quiere procesar en este estilo
    part_numbers = Column(JSON, nullable=False)  # Lista de números de parte
    
    # Configuración del estilo (estaciones y herramientas)
    estilo_json = Column(JSON, nullable=False)  # Array de estaciones con sus herramientas
    
    # Información adicional
    notas = Column(String, nullable=True)  # Notas del usuario
    
    # Control de fechas
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))  # 30 días
    activa = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<EstiloManual(id={self.id}, nombre='{self.nombre}', machine='{self.machine_nombre}')>"
