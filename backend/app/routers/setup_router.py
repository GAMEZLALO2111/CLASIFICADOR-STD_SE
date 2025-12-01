from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.utils.parser_setups import parse_setup

router = APIRouter(prefix="/setup", tags=["SETUP"])

@router.post("/procesar")
async def procesar_setup(file: UploadFile = File(...)):
    # Validar extensión
    if not file.filename.lower().endswith(".stp") and not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .stp o .txt")

    contenido = (await file.read()).decode("utf-8", errors="ignore")

    try:
        resultado = parse_setup(contenido)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el setup: {str(e)}")

    return {
        "archivo": file.filename,
        "resultado": resultado
    }
