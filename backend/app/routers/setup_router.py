from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.database.db import get_db
from backend.app.models.setup_model import Setup
from backend.app.utils.parser_setups import parse_setup
from backend.app.services.setup_service import listar_setups, obtener_setup_por_part_number
import os
import shutil

router = APIRouter(prefix="/setup", tags=["SETUP"])


# ----------------------------------------------------------
#  POST /setup/upload  → Subir y guardar SETUP
# ----------------------------------------------------------
@router.post("/upload")
async def upload_setup(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Validar extensión
    if not file.filename.endswith(".stp"):
        raise HTTPException(400, "Solo se aceptan archivos .stp")

    # 2. Guardar temporalmente
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Parsear el archivo
    try:
        data = parse_setup(temp_path)
    except Exception as e:
        os.remove(temp_path)
        raise HTTPException(500, f"Error procesando setup: {str(e)}")

    # 4. Guardar en DB
    new_setup = Setup(
        part_full=data["part_number"]["full"],
        prefix=data["part_number"]["prefix"],
        number=data["part_number"]["number"],
        version=data["part_number"]["version"],
        nivel=data["part_number"]["nivel"],

        thickness=data["thickness"],
        sheet_x=data["sheet_size"][0] if data["sheet_size"] else None,
        sheet_y=data["sheet_size"][1] if data["sheet_size"] else None,

        stations=",".join(data["stations"]),
        tool_numbers=",".join(data["tool_numbers"]),

        sym=data["sym"],
        run_time_mins=data["run_time_mins"],
        uph=data["uph"]
    )

    db.add(new_setup)
    db.commit()
    db.refresh(new_setup)

    # 5. Borrar temporal
    os.remove(temp_path)

    return {
        "message": "SETUP guardado con éxito",
        "data": data
    }


# ----------------------------------------------------------
#  GET /setup/listar  → Listar todos los setups guardados
# ----------------------------------------------------------
@router.get("/listar")
def listar_setups_endpoint(db: Session = Depends(get_db)):
    setups = listar_setups(db)
    return {
        "message": "Setups encontrados",
        "total": len(setups),
        "data": setups
    }


# ----------------------------------------------------------
#  GET /setup/{number}  → Buscar setup por número de parte
# ----------------------------------------------------------
@router.get("/{number}")
def obtener_setup(number: str, db: Session = Depends(get_db)):
    setup = obtener_setup_por_part_number(db, number)

    if not setup:
        raise HTTPException(
            status_code=404,
            detail=f"No existe un setup con el número de parte {number}"
        )

    return {
        "message": "Setup encontrado",
        "data": {
            "id": setup.id,
            "part_full": setup.part_full,
            "prefix": setup.prefix,
            "number": setup.number,
            "version": setup.version,
            "nivel": setup.nivel,
            "thickness": setup.thickness,
            "sheet_x": setup.sheet_x,
            "sheet_y": setup.sheet_y,
            "stations": setup.stations.split(",") if setup.stations else [],
            "tool_numbers": setup.tool_numbers.split(",") if setup.tool_numbers else [],
            "sym": setup.sym,
            "run_time_mins": setup.run_time_mins,
            "uph": setup.uph
        }
    }
