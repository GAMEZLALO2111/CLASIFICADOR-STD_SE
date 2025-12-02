from sqlalchemy.orm import Session
from backend.app.models.fg_model import FinishGood

def crear_fg(db: Session, nombre: str):
    nuevo_fg = FinishGood(nombre=nombre)
    db.add(nuevo_fg)
    db.commit()
    db.refresh(nuevo_fg)
    return nuevo_fg

def obtener_fgs(db: Session):
    return db.query(FinishGood).all()

def obtener_fg(db: Session, fg_id: int):
    return db.query(FinishGood).filter(FinishGood.id == fg_id).first()

from backend.app.models.fg_parts_model import FGPart

def agregar_pieza_fg(db: Session, fg_id: int, part_number: str, cantidad: int):
    nueva = FGPart(
        fg_id=fg_id,
        part_number=part_number,
        cantidad=cantidad
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_piezas_fg(db: Session, fg_id: int):
    return db.query(FGPart).filter(FGPart.fg_id == fg_id).all()
