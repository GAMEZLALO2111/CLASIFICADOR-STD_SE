from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.estilo_manual_model import EstiloManual
from app.models.estilo_manual_request import CrearEstiloManualRequest, EstiloManualResponse
from app.models.machine_model import Machine
from app.services.excel_service import generar_excel_estilo_maquina
from app.models.distribucion_model import AsignacionMaquina, AsignacionPart, EstiloEstacion
from app.models.setup_model import Setup
from app.utils.parser_setups import parse_setup
from datetime import datetime
from typing import List, Optional
import io
import tempfile
import os

router = APIRouter(prefix="/estilo", tags=["ESTILOS MANUALES"])


@router.post("/crear-desde-archivos", response_model=EstiloManualResponse)
async def crear_estilo_desde_archivos(
    nombre: str = Form(...),
    machine_id: int = Form(...),
    notas: str = Form(None),
    archivos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Crea un estilo manual desde archivos .stp
    
    El usuario sube archivos .stp, selecciona una máquina,
    y el sistema parsea los setups automáticamente y calcula el estilo.
    
    Parámetros:
    - nombre: Nombre descriptivo del estilo
    - machine_id: ID de la máquina donde se aplicará
    - archivos: Lista de archivos .stp a procesar
    - notas: Notas opcionales
    """
    # Validar que la máquina existe
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(404, f"Máquina {machine_id} no encontrada")
    
    # Validar que hay archivos
    if not archivos or len(archivos) == 0:
        raise HTTPException(400, "Debe proporcionar al menos un archivo .stp")
    
    # Parsear cada archivo .stp
    setups_parseados = []
    part_numbers = []
    
    for archivo in archivos:
        # Validar extensión
        if not archivo.filename.lower().endswith('.stp'):
            raise HTTPException(400, f"El archivo {archivo.filename} no es un .stp válido")
        
        # Leer contenido del archivo
        contenido = await archivo.read()
        
        # Guardar temporalmente para parsear
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.stp', delete=False) as temp_file:
            temp_file.write(contenido)
            temp_path = temp_file.name
        
        try:
            # Parsear el setup
            setup = parse_setup(temp_path)
            setups_parseados.append(setup)
            part_numbers.append(setup.part_number)
        except Exception as e:
            raise HTTPException(400, f"Error parseando {archivo.filename}: {str(e)}")
        finally:
            # Eliminar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    # Calcular estilo unificado usando la máquina seleccionada
    from app.services.machine_template_service import calcular_estilo_unificado
    
    estilo_calculado = calcular_estilo_unificado(
        setups=setups_parseados,
        machine_template=machine.template_data
    )
    
    # Convertir estilo a formato JSON
    estilo_json = []
    for est in estilo_calculado:
        estilo_json.append({
            "estacion": est.estacion,
            "tipo": est.tipo,
            "tool_number": est.tool_number,
            "angulo": est.angulo,
            "tiene_guia": est.tiene_guia,
            "es_autoindex": est.es_autoindex,
            "parts_que_usan": est.parts_que_usan
        })
    
    # Crear estilo manual
    estilo = EstiloManual(
        nombre=nombre,
        machine_id=machine_id,
        machine_nombre=machine.nombre,
        tipo_maquina=machine.tipo,
        part_numbers=part_numbers,
        estilo_json=estilo_json,
        notas=notas
    )
    
    db.add(estilo)
    db.commit()
    db.refresh(estilo)
    
    return EstiloManualResponse(
        id=estilo.id,
        nombre=estilo.nombre,
        machine_id=estilo.machine_id,
        machine_nombre=estilo.machine_nombre,
        tipo_maquina=estilo.tipo_maquina,
        part_numbers=estilo.part_numbers,
        estilo_json=estilo.estilo_json,
        notas=estilo.notas,
        created_at=estilo.created_at.isoformat(),
        expires_at=estilo.expires_at.isoformat(),
        activa=estilo.activa
    )


@router.post("/crear", response_model=EstiloManualResponse)
def crear_estilo_manual(
    request: CrearEstiloManualRequest,
    db: Session = Depends(get_db)
):
    """
    [DEPRECADO] Usa /crear-desde-archivos en su lugar.
    
    Crea un estilo manual personalizado sin necesidad de distribución automática.
    El usuario define:
    - Máquina a usar
    - Parts que procesará
    - Configuración de estaciones y herramientas
    """
    # Validar que la máquina existe
    machine = db.query(Machine).filter(Machine.id == request.machine_id).first()
    if not machine:
        raise HTTPException(404, f"Máquina {request.machine_id} no encontrada")
    
    # Convertir estaciones a dict
    estilo_json = [est.model_dump() for est in request.estaciones]
    
    # Crear estilo manual
    estilo = EstiloManual(
        nombre=request.nombre,
        machine_id=request.machine_id,
        machine_nombre=machine.nombre,
        tipo_maquina=machine.tipo,
        part_numbers=request.part_numbers,
        estilo_json=estilo_json,
        notas=request.notas
    )
    
    db.add(estilo)
    db.commit()
    db.refresh(estilo)
    
    return EstiloManualResponse(
        id=estilo.id,
        nombre=estilo.nombre,
        machine_id=estilo.machine_id,
        machine_nombre=estilo.machine_nombre,
        tipo_maquina=estilo.tipo_maquina,
        part_numbers=estilo.part_numbers,
        estilo_json=estilo.estilo_json,
        notas=estilo.notas,
        created_at=estilo.created_at.isoformat(),
        expires_at=estilo.expires_at.isoformat(),
        activa=estilo.activa
    )


@router.get("/listar", response_model=List[EstiloManualResponse])
def listar_estilos_manuales(db: Session = Depends(get_db)):
    """
    Lista todos los estilos manuales activos (no expirados).
    """
    now = datetime.utcnow()
    
    estilos = db.query(EstiloManual).filter(
        EstiloManual.activa == True,
        EstiloManual.expires_at > now
    ).order_by(EstiloManual.created_at.desc()).all()
    
    return [
        EstiloManualResponse(
            id=e.id,
            nombre=e.nombre,
            machine_id=e.machine_id,
            machine_nombre=e.machine_nombre,
            tipo_maquina=e.tipo_maquina,
            part_numbers=e.part_numbers,
            estilo_json=e.estilo_json,
            notas=e.notas,
            created_at=e.created_at.isoformat(),
            expires_at=e.expires_at.isoformat(),
            activa=e.activa
        )
        for e in estilos
    ]


@router.get("/{estilo_id}", response_model=EstiloManualResponse)
def obtener_estilo_manual(estilo_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un estilo manual por su ID.
    """
    estilo = db.query(EstiloManual).filter(
        EstiloManual.id == estilo_id,
        EstiloManual.activa == True
    ).first()
    
    if not estilo:
        raise HTTPException(404, "Estilo no encontrado")
    
    return EstiloManualResponse(
        id=estilo.id,
        nombre=estilo.nombre,
        machine_id=estilo.machine_id,
        machine_nombre=estilo.machine_nombre,
        tipo_maquina=estilo.tipo_maquina,
        part_numbers=estilo.part_numbers,
        estilo_json=estilo.estilo_json,
        notas=estilo.notas,
        created_at=estilo.created_at.isoformat(),
        expires_at=estilo.expires_at.isoformat(),
        activa=estilo.activa
    )


@router.get("/{estilo_id}/excel")
def descargar_estilo_manual_excel(estilo_id: int, db: Session = Depends(get_db)):
    """
    Descarga un estilo manual en formato Excel.
    """
    estilo = db.query(EstiloManual).filter(
        EstiloManual.id == estilo_id,
        EstiloManual.activa == True
    ).first()
    
    if not estilo:
        raise HTTPException(404, "Estilo no encontrado")
    
    # Convertir a AsignacionMaquina para usar la función de Excel existente
    # Crear parts ficticios (ya que es manual, no tiene asignaciones reales)
    parts_asignados = [
        AsignacionPart(
            part_filename=pn,
            part_number=pn,
            cantidad_requerida=0,
            cantidad_asignada=0,
            horas_corrida=0,
            estaciones_usadas=0,
            estaciones_unificadas=0
        )
        for pn in estilo.part_numbers
    ]
    
    # Convertir estaciones
    estaciones_estilo = [
        EstiloEstacion(**est_dict)
        for est_dict in estilo.estilo_json
    ]
    
    # Crear objeto AsignacionMaquina
    asignacion = AsignacionMaquina(
        machine_id=estilo.machine_id,
        machine_nombre=estilo.machine_nombre,
        tipo_maquina=estilo.tipo_maquina,
        parts_asignados=parts_asignados,
        tiempo_total_usado=0,
        tiempo_disponible=0,
        tiempo_sobrante=0,
        estilo=estaciones_estilo,
        estaciones_fuera_estilo=[],
        alertas=[],
        errores=[]
    )
    
    # Generar Excel
    excel_bytes = generar_excel_estilo_maquina(
        asignacion=asignacion,
        package_nombre=estilo.nombre,
        demanda=0
    )
    
    filename = f"estilo_manual_{estilo.nombre}_{estilo.machine_nombre}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.delete("/{estilo_id}")
def eliminar_estilo_manual(estilo_id: int, db: Session = Depends(get_db)):
    """
    Elimina (desactiva) un estilo manual.
    """
    estilo = db.query(EstiloManual).filter(EstiloManual.id == estilo_id).first()
    
    if not estilo:
        raise HTTPException(404, "Estilo no encontrado")
    
    estilo.activa = False
    db.commit()
    
    return {"message": f"Estilo '{estilo.nombre}' eliminado"}
