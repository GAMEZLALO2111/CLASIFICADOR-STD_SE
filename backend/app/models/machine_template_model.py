from sqlalchemy import Column, Integer, String, JSON
from app.database.db import Base

class MachineTemplate(Base):
    __tablename__ = "machine_templates"

    id = Column(Integer, primary_key=True, index=True)
    tipo_maquina = Column(String, unique=True, nullable=False, index=True)  # "4I", "2I", "45STA"
    estaciones_totales = Column(Integer, nullable=False)
    autoindex_count = Column(Integer, nullable=False)
    estaciones_config = Column(JSON, nullable=False)
    # Formato de estaciones_config:
    # {
    #   "201": {"tipo": "B", "es_autoindex": true, "tiene_guia": false},
    #   "103": {"tipo": "A", "es_autoindex": false, "tiene_guia": true},
    #   ...
    # }