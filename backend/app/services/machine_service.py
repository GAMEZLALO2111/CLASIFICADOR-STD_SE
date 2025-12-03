from sqlalchemy.orm import Session
from backend.app.models.machine_model import Machine
from backend.app.models.machine_template_model import MachineTemplate
from typing import List, Optional

def crear_machine(
    db: Session,
    template_id: int,
    modelo: str,
    nombre: str,
    mesa_x: int,
    mesa_y: int,
    thickness_min: float,
    thickness_max: float,
    estaciones_dañadas: List[int] = []
) -> Machine:
    nueva_machine = Machine(
        template_id=template_id,
        modelo=modelo,
        nombre=nombre,
        mesa_x=mesa_x,
        mesa_y=mesa_y,
        thickness_min=thickness_min,
        thickness_max=thickness_max,
        estaciones_dañadas=estaciones_dañadas
    )
    db.add(nueva_machine)
    db.commit()
    db.refresh(nueva_machine)
    return nueva_machine

def obtener_machines(db: Session, solo_activas: bool = True) -> List[Machine]:
    query = db.query(Machine)
    if solo_activas:
        query = query.filter(Machine.activa == 1)
    return query.all()

def obtener_machine_por_id(db: Session, machine_id: int) -> Optional[Machine]:
    return db.query(Machine).filter(Machine.id == machine_id).first()

def actualizar_machine(db: Session, machine_id: int, datos: dict) -> Optional[Machine]:
    machine = obtener_machine_por_id(db, machine_id)
    if not machine:
        return None
    
    for key, value in datos.items():
        if hasattr(machine, key):
            setattr(machine, key, value)
    
    db.commit()
    db.refresh(machine)
    return machine

def eliminar_machine(db: Session, machine_id: int) -> bool:
    machine = obtener_machine_por_id(db, machine_id)
    if not machine:
        return False
    
    db.delete(machine)
    db.commit()
    return True