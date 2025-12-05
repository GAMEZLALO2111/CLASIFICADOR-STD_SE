from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services import distribucion_service
from app.services.excel_service import generar_excel_distribucion, generar_excel_estilo_maquina
from app.models.distribucion_model import DistribucionRequest, DistribucionResponse
from app.models.distribucion_storage_model import DistribucionStorage
from datetime import datetime
from typing import List
import io

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


@router.post("/exportar-excel")
def exportar_distribucion_a_excel(
    distribucion: DistribucionResponse
):
    """
    Recibe el JSON de una distribución ya calculada y lo convierte a Excel.
    
    Uso:
    1. Llamar POST /crear para obtener el JSON de la distribución
    2. Llamar POST /exportar-excel enviando ese JSON completo
    3. Descargar el archivo Excel generado
    
    El archivo incluye:
    - Resumen general
    - Detalle por máquina
    - Estilos de herramientas
    - Alertas y errores
    """
    try:
        # Generar Excel directamente del JSON recibido
        excel_bytes = generar_excel_distribucion(distribucion)
        
        # Nombre del archivo
        filename = f"Distribucion_{distribucion.package_nombre}_D{distribucion.demanda}.xlsx"
        
        # Retornar archivo para descarga
        return StreamingResponse(
            io.BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(500, f"Error generando Excel: {str(e)}")


@router.get("/listar")
def listar_distribuciones(db: Session = Depends(get_db)):
    """
    Lista todas las distribuciones activas (no expiradas).
    
    Retorna resumen de cada distribución:
    - ID
    - Package nombre
    - Demanda
    - Horas objetivo
    - Es factible
    - Fecha creación
    - Fecha expiración
    """
    now = datetime.utcnow()
    
    # Obtener solo distribuciones activas y no expiradas
    distribuciones = db.query(DistribucionStorage).filter(
        DistribucionStorage.activa == True,
        DistribucionStorage.expires_at > now
    ).order_by(DistribucionStorage.created_at.desc()).all()
    
    return [
        {
            "id": d.id,
            "package_id": d.package_id,
            "package_nombre": d.package_nombre,
            "demanda": d.demanda,
            "horas_objetivo": d.horas_objetivo,
            "es_factible": d.es_factible,
            "created_at": d.created_at.isoformat(),
            "expires_at": d.expires_at.isoformat(),
            "machine_ids": d.machine_ids
        }
        for d in distribuciones
    ]


@router.get("/{distribucion_id}", response_model=DistribucionResponse)
def obtener_distribucion(distribucion_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el JSON completo de una distribución guardada por su ID.
    """
    now = datetime.utcnow()
    
    dist = db.query(DistribucionStorage).filter(
        DistribucionStorage.id == distribucion_id,
        DistribucionStorage.activa == True,
        DistribucionStorage.expires_at > now
    ).first()
    
    if not dist:
        raise HTTPException(404, "Distribución no encontrada o expirada")
    
    # Retornar el JSON completo guardado
    return DistribucionResponse(**dist.resultado_json)


@router.delete("/{distribucion_id}")
def eliminar_distribucion(distribucion_id: int, db: Session = Depends(get_db)):
    """
    Elimina (marca como inactiva) una distribución.
    """
    dist = db.query(DistribucionStorage).filter(
        DistribucionStorage.id == distribucion_id
    ).first()
    
    if not dist:
        raise HTTPException(404, "Distribución no encontrada")
    
    dist.activa = False
    db.commit()
    
    return {"message": "Distribución eliminada"}


@router.post("/admin/cleanup")
def limpiar_distribuciones_expiradas(db: Session = Depends(get_db)):
    """
    Elimina distribuciones expiradas (más de 1 día).
    """
    now = datetime.utcnow()
    
    count = db.query(DistribucionStorage).filter(
        DistribucionStorage.expires_at <= now
    ).update({"activa": False})
    
    db.commit()
    
    return {"message": f"{count} distribuciones expiradas eliminadas"}


@router.get("/{distribucion_id}/maquina/{machine_id}/estilo-excel")
def descargar_estilo_maquina(
    distribucion_id: int,
    machine_id: int,
    db: Session = Depends(get_db)
):
    """
    Descarga el estilo de UNA máquina específica en formato Excel.
    Optimizado para que el técnico programe la máquina con las herramientas correctas.
    """
    # Buscar distribución
    dist = db.query(DistribucionStorage).filter(
        DistribucionStorage.id == distribucion_id,
        DistribucionStorage.activa == True
    ).first()
    
    if not dist:
        raise HTTPException(404, "Distribución no encontrada")
    
    # Buscar la asignación de la máquina específica
    resultado = dist.resultado_json
    asignacion_encontrada = None
    
    for asig in resultado.get("asignaciones", []):
        if asig.get("machine_id") == machine_id:
            asignacion_encontrada = asig
            break
    
    if not asignacion_encontrada:
        raise HTTPException(404, f"Máquina {machine_id} no encontrada en esta distribución")
    
    # Convertir a objeto AsignacionMaquina
    from app.models.distribucion_model import AsignacionMaquina
    asignacion = AsignacionMaquina(**asignacion_encontrada)
    
    # Generar Excel del estilo
    excel_bytes = generar_excel_estilo_maquina(
        asignacion=asignacion,
        package_nombre=dist.package_nombre,
        demanda=dist.demanda
    )
    
    # Nombre del archivo
    filename = f"estilo_{asignacion.machine_nombre}_{dist.package_nombre}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
