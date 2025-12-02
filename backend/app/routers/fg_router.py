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

@router.post("/{fg_id}/agregar_pieza")
def agregar_pieza(fg_id: int, part_number: str, cantidad: int, db: Session = Depends(get_db)):
    pieza = agregar_pieza_fg(db, fg_id, part_number, cantidad)
    return {"message": "Pieza agregada", "data": {
        "id": pieza.id,
        "part_number": pieza.part_number,
        "cantidad": pieza.cantidad
    }}

@router.get("/{fg_id}/piezas")
def listar_piezas(fg_id: int, db: Session = Depends(get_db)):
    piezas = obtener_piezas_fg(db, fg_id)
    return {
        "fg_id": fg_id,
        "total_piezas": len(piezas),
        "data": [
            {"id": p.id, "part": p.part_number, "cantidad": p.cantidad}
            for p in piezas
        ]
    }
