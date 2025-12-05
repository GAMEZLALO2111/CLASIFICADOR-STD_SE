from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services import machine_service, machine_template_service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/machine", tags=["MACHINES"])

class MachineCreate(BaseModel):
    template_id: int
    modelo: str  # "EMK6120", etc.
    nombre: str  # "T-101", etc.
    mesa_x: int
    mesa_y: int
    thickness_min: float
    thickness_max: float
    estaciones_dañadas: List[int] = []

class MachineUpdate(BaseModel):
    modelo: Optional[str] = None
    nombre: Optional[str] = None
    mesa_x: Optional[int] = None
    mesa_y: Optional[int] = None
    thickness_min: Optional[float] = None
    thickness_max: Optional[float] = None
    estaciones_dañadas: Optional[List[int]] = None
    activa: Optional[int] = None

@router.post("/admin/init_templates")
def inicializar_templates(db: Session = Depends(get_db)):
    """Inicializa los templates de máquinas (4I, 2I, 45STA)"""
    count = machine_template_service.inicializar_templates(db)
    return {
        "message": f"{count} templates inicializados",
        "nota": "Si devuelve 0, los templates ya existían"
    }

@router.get("/templates")
def listar_templates(db: Session = Depends(get_db)):
    """Lista todos los templates disponibles"""
    templates = machine_template_service.obtener_templates(db)
    return {
        "total": len(templates),
        "data": [
            {
                "id": t.id,
                "tipo_maquina": t.tipo_maquina,
                "estaciones_totales": t.estaciones_totales,
                "autoindex_count": t.autoindex_count
            }
            for t in templates
        ]
    }

@router.get("/templates/{template_id}")
def obtener_template_detalle(template_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle completo de un template incluyendo configuración de estaciones"""
    template = machine_template_service.obtener_template_por_id(db, template_id)
    if not template:
        raise HTTPException(404, "Template no encontrado")
    return template

@router.post("/crear")
def crear_machine_endpoint(data: MachineCreate, db: Session = Depends(get_db)):
    # Validar que el template existe
    template = machine_template_service.obtener_template_por_id(db, data.template_id)
    if not template:
        raise HTTPException(404, "Template no encontrado")
    
    machine = machine_service.crear_machine(
        db=db,
        template_id=data.template_id,
        modelo=data.modelo,
        nombre=data.nombre,
        mesa_x=data.mesa_x,
        mesa_y=data.mesa_y,
        thickness_min=data.thickness_min,
        thickness_max=data.thickness_max,
        estaciones_dañadas=data.estaciones_dañadas
    )
    return {
        "message": "Máquina creada exitosamente",
        "data": {
            "id": machine.id,
            "nombre": machine.nombre,
            "modelo": machine.modelo,
            "tipo_maquina": template.tipo_maquina
        }
    }

@router.get("/listar")
def listar_machines(solo_activas: bool = True, db: Session = Depends(get_db)):
    machines = machine_service.obtener_machines(db, solo_activas)
    return {
        "total": len(machines),
        "data": [
            {
                "id": m.id,
                "nombre": m.nombre,
                "modelo": m.modelo,
                "tipo_maquina": m.template.tipo_maquina,
                "mesa": f"{m.mesa_x}x{m.mesa_y}",
                "thickness": f"{m.thickness_min}-{m.thickness_max}",
                "estaciones_dañadas": m.estaciones_dañadas,
                "activa": m.activa == 1
            }
            for m in machines
        ]
    }

@router.get("/{machine_id}")
def obtener_machine_detalle(machine_id: int, db: Session = Depends(get_db)):
    machine = machine_service.obtener_machine_por_id(db, machine_id)
    if not machine:
        raise HTTPException(404, "Máquina no encontrada")
    
    return {
        "id": machine.id,
        "nombre": machine.nombre,
        "modelo": machine.modelo,
        "template": {
            "id": machine.template.id,
            "tipo_maquina": machine.template.tipo_maquina,
            "estaciones_totales": machine.template.estaciones_totales,
            "autoindex_count": machine.template.autoindex_count,
            "estaciones_config": machine.template.estaciones_config
        },
        "mesa_x": machine.mesa_x,
        "mesa_y": machine.mesa_y,
        "thickness_min": machine.thickness_min,
        "thickness_max": machine.thickness_max,
        "estaciones_dañadas": machine.estaciones_dañadas,
        "activa": machine.activa == 1
    }

@router.put("/{machine_id}")
def actualizar_machine(machine_id: int, data: MachineUpdate, db: Session = Depends(get_db)):
    datos = data.dict(exclude_unset=True)
    machine = machine_service.actualizar_machine(db, machine_id, datos)
    if not machine:
        raise HTTPException(404, "Máquina no encontrada")
    return {
        "message": "Máquina actualizada",
        "data": {
            "id": machine.id,
            "nombre": machine.nombre
        }
    }

@router.delete("/{machine_id}")
def eliminar_machine(machine_id: int, db: Session = Depends(get_db)):
    success = machine_service.eliminar_machine(db, machine_id)
    if not success:
        raise HTTPException(404, "Máquina no encontrada")
    return {"message": "Máquina eliminada"}