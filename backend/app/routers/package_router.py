from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.app.database.db import get_db
from backend.app.services import package_service
from backend.app.utils.parser_setups import parse_setup
from typing import List
import os
import shutil

router = APIRouter(prefix="/package", tags=["PACKAGES"])

@router.post("/crear")
async def crear_package_endpoint(
    nombre: str = Form(...),
    descripcion: str = Form(""),
    files: List[UploadFile] = File(...),
    cantidades: str = Form(...),  # JSON string: "[10, 20, 30]"
    db: Session = Depends(get_db)
):
    import json
    
    # Parsear cantidades
    try:
        cantidades_list = json.loads(cantidades)
        # Asegurar que es lista
        if not isinstance(cantidades_list, list):
            raise HTTPException(400, "cantidades debe ser una lista JSON: [10, 20, 30]")
    except json.JSONDecodeError:
        raise HTTPException(400, "cantidades debe ser JSON válido: [10, 20, 30]")
    
    if len(files) != len(cantidades_list):
        raise HTTPException(400, f"Número de archivos ({len(files)}) y cantidades ({len(cantidades_list)}) no coincide")
    
    parts_data = []
    
    for file, cantidad in zip(files, cantidades_list):
        # Validar extensión
        if not file.filename.endswith(".stp"):
            raise HTTPException(400, f"Solo se aceptan archivos .stp: {file.filename}")
        
        # Guardar temporalmente
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parsear
        try:
            parsed_data = parse_setup(temp_path)
        except Exception as e:
            os.remove(temp_path)
            raise HTTPException(500, f"Error parseando {file.filename}: {str(e)}")
        
        # Limpiar temporal
        os.remove(temp_path)
        
        # Agregar a lista
        parts_data.append({
            "filename": file.filename.replace("temp_", "").replace(".stp", ""),
            "cantidad": cantidad,
            "parsed_data": parsed_data
        })
    
    # Crear package
    package = package_service.crear_package(db, nombre, descripcion, parts_data)
    
    return {
        "message": "Package creado exitosamente",
        "data": {
            "id": package.id,
            "nombre": package.nombre,
            "total_parts": len(package.parts),
            "expira_en": "24 horas"
        }
    }

@router.get("/listar")
def listar_packages(db: Session = Depends(get_db)):
    packages = package_service.obtener_packages_activos(db)
    return {
        "total": len(packages),
        "data": [
            {
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "total_parts": len(p.parts),
                "fecha_creacion": p.fecha_creacion,
                "fecha_expiracion": p.fecha_expiracion
            }
            for p in packages
        ]
    }

@router.get("/{package_id}")
def obtener_package_detalle(package_id: int, db: Session = Depends(get_db)):
    package = package_service.obtener_package_por_id(db, package_id)
    if not package:
        raise HTTPException(404, "Package no encontrado o expirado")
    
    return {
        "id": package.id,
        "nombre": package.nombre,
        "descripcion": package.descripcion,
        "fecha_creacion": package.fecha_creacion,
        "fecha_expiracion": package.fecha_expiracion,
        "parts": [
            {
                "filename": part.part_filename,
                "cantidad": part.cantidad,
                "info": part.parsed_data
            }
            for part in package.parts
        ]
    }

@router.post("/admin/cleanup")
def limpiar_packages_expirados(db: Session = Depends(get_db)):
    """Endpoint para job de limpieza manual"""
    count = package_service.eliminar_packages_expirados(db)
    return {
        "message": f"{count} packages expirados eliminados"
    }

@router.post("/agregar_part")
async def agregar_part_a_package(
    package_id: int = Form(...),
    file: UploadFile = File(...),
    cantidad: int = Form(...),
    db: Session = Depends(get_db)
):
    """Agrega un part a un package existente"""
    from backend.app.models.package_part_model import PackagePart
    
    # Verificar que el package existe
    package = package_service.obtener_package_por_id(db, package_id)
    if not package:
        raise HTTPException(404, "Package no encontrado o expirado")
    
    # Validar extensión
    if not file.filename.endswith(".stp"):
        raise HTTPException(400, "Solo se aceptan archivos .stp")
    
    # Guardar temporalmente
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parsear
    try:
        parsed_data = parse_setup(temp_path)
    except Exception as e:
        os.remove(temp_path)
        raise HTTPException(500, f"Error parseando: {str(e)}")
    
    # Limpiar temporal
    os.remove(temp_path)
    
    # Agregar part al package
    new_part = PackagePart(
        package_id=package_id,
        part_filename=file.filename.replace("temp_", "").replace(".stp", ""),
        cantidad=cantidad,
        parsed_data=parsed_data
    )
    db.add(new_part)
    db.commit()
    db.refresh(new_part)
    
    return {
        "message": "Part agregado al package",
        "package_id": package_id,
        "part": {
            "filename": new_part.part_filename,
            "cantidad": new_part.cantidad
        }
    }

@router.post("/crear_vacio")
def crear_package_vacio(
    nombre: str = Form(...),
    descripcion: str = Form(""),
    db: Session = Depends(get_db)
):
    """Crea un package vacío, luego usa /agregar_part para agregar archivos"""
    from backend.app.models.package_model import Package
    
    nuevo_package = Package(
        nombre=nombre,
        descripcion=descripcion
    )
    db.add(nuevo_package)
    db.commit()
    db.refresh(nuevo_package)
    
    return {
        "message": "Package vacío creado",
        "data": {
            "id": nuevo_package.id,
            "nombre": nuevo_package.nombre
        },
        "siguiente_paso": f"Usa POST /package/agregar_part con package_id={nuevo_package.id}"
    }