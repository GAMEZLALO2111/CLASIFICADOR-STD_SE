from sqlalchemy.orm import Session
from backend.app.models.fg import FG

def crear_fg(db: Session, nombre: str):
    nuevo_fg = FG(nombre=nombre)
    db.add(nuevo_fg)
    db.commit()
    db.refresh(nuevo_fg)
    return nuevo_fg

def obtener_fgs(db: Session):
    return db.query(FG).all()

def obtener_fg(db: Session, fg_id: int):
    return db.query(FG).filter(FG.id == fg_id).first()
