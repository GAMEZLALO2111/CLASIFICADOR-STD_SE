from sqlalchemy.orm import Session
from backend.app.models.machine_template_model import MachineTemplate
from backend.app.database.templates_data import TEMPLATES
from typing import List, Optional

def inicializar_templates(db: Session) -> int:
    """
    Carga los templates predefinidos en la BD si no existen
    Retorna cantidad de templates creados
    """
    count = 0
    for template_data in TEMPLATES:
        # Verificar si ya existe
        existe = db.query(MachineTemplate).filter(
            MachineTemplate.tipo_maquina == template_data["tipo_maquina"]
        ).first()
        
        if not existe:
            nuevo_template = MachineTemplate(**template_data)
            db.add(nuevo_template)
            count += 1
    
    db.commit()
    return count

def obtener_templates(db: Session) -> List[MachineTemplate]:
    """Obtiene todos los templates disponibles"""
    return db.query(MachineTemplate).all()

def obtener_template_por_id(db: Session, template_id: int) -> Optional[MachineTemplate]:
    """Obtiene un template por ID"""
    return db.query(MachineTemplate).filter(MachineTemplate.id == template_id).first()

def obtener_template_por_tipo(db: Session, tipo_maquina: str) -> Optional[MachineTemplate]:
    """Obtiene un template por tipo (4I, 2I, 45STA)"""
    return db.query(MachineTemplate).filter(MachineTemplate.tipo_maquina == tipo_maquina).first()