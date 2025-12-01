from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.db import get_db
from backend.app.services.fg_service import crear_fg, obtener_fgs

router = APIRouter(prefix="/fg", tags=["FG"])

@router.post("/crear")
def crear_fg_endpoint(nombre: str, db: Session = Depends(get_db)):
    fg = crear_fg(db, nombre)
    return {"message": "FG creado", "fg": {"id": fg.id, "nombre": fg.nombre}}

@router.get("/")
def listar_fgs(db: Session = Depends(get_db)):
    lista = obtener_fgs(db)
    return lista

