from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.db import get_db
from backend.app.services import distribucion_service
from backend.app.models.distribucion_model import DistribucionRequest, DistribucionResponse

router = APIRouter(prefix="/distribucion", tags=["DISTRIBUCION"])

@router.post("/crear", response_model=DistribucionResponse)
def crear_distribucion_endpoint(
    request: DistribucionRequest,
    db: Session = Depends(get_db)
):
    """
    Crea una distribución de parts a máquinas basada en:
    - Package seleccionado
    - Demanda (productos finales)
    - Tiempo objetivo (horas disponibles)
    - Máquinas disponibles
    
    Retorna asignaciones optimizadas con estilos de herramientas.
    """
    try:
        distribucion = distribucion_service.crear_distribucion(
            db=db,
            package_id=request.package_id,
            demanda=request.demanda,
            horas_objetivo=request.horas_objetivo,
            machine_ids=request.machine_ids
        )
        return distribucion
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error creando distribución: {str(e)}")
