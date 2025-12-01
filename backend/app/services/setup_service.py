from sqlalchemy.orm import Session
from backend.app.models.setup_model import Setup

def obtener_setup_por_part_number(db: Session, number: str):
    setup = db.query(Setup).filter(Setup.number == number).first()
    return setup


def listar_setups(db: Session):
    """
    Devuelve todos los setups guardados en la BD.
    """
    return db.query(Setup).all()
