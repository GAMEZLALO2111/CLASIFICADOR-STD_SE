from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services import package_service
from app.utils.parser_setups import parse_setup
from typing import List
import os
import shutil

router = APIRouter(prefix="/package", tags=["PACKAGES"])

# Endpoint POST /crear ELIMINADO - Usar preview + confirmar

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
                "id": part.id,
                "filename": part.part_filename,
                "cantidad": part.cantidad,
                "info": part.parsed_data
            }
            for part in package.parts
        ]
    }

@router.put("/{package_id}/actualizar_cantidades")
def actualizar_cantidades_package(
    package_id: int,
    cantidades: str = Form(...),  # JSON: {"part_id": nueva_cantidad}
    db: Session = Depends(get_db)
):
    """
    Actualiza las cantidades de los parts de un package.
    cantidades debe ser JSON: {"1": 10, "2": 20} donde las keys son part_id
    """
    import json
    from app.models.package_part_model import PackagePart
    
    # Verificar package existe
    package = package_service.obtener_package_por_id(db, package_id)
    if not package:
        raise HTTPException(404, "Package no encontrado o expirado")
    
    # Parsear cantidades
    try:
        cantidades_dict = json.loads(cantidades)
        if not isinstance(cantidades_dict, dict):
            raise ValueError("Debe ser un objeto JSON")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(400, 'cantidades debe ser JSON válido: {"1": 10, "2": 20}')
    
    # Actualizar cada part
    actualizados = []
    for part_id_str, nueva_cantidad in cantidades_dict.items():
        part_id = int(part_id_str)
        part = db.query(PackagePart).filter(
            PackagePart.id == part_id,
            PackagePart.package_id == package_id
        ).first()
        
        if not part:
            raise HTTPException(404, f"Part ID {part_id} no encontrado en este package")
        
        part.cantidad = int(nueva_cantidad)
        actualizados.append({
            "part_id": part_id,
            "filename": part.part_filename,
            "nueva_cantidad": part.cantidad
        })
    
    db.commit()
    
    return {
        "message": f"{len(actualizados)} cantidades actualizadas",
        "package_id": package_id,
        "actualizados": actualizados
    }

@router.delete("/{package_id}/setup/{part_id}")
def eliminar_setup_de_package(
    package_id: int,
    part_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un setup específico de un package"""
    from app.models.package_part_model import PackagePart
    
    # Verificar package existe
    package = package_service.obtener_package_por_id(db, package_id)
    if not package:
        raise HTTPException(404, "Package no encontrado o expirado")
    
    # Buscar el part
    part = db.query(PackagePart).filter(
        PackagePart.id == part_id,
        PackagePart.package_id == package_id
    ).first()
    
    if not part:
        raise HTTPException(404, "Setup no encontrado en este package")
    
    filename = part.part_filename
    db.delete(part)
    db.commit()
    
    return {
        "message": "Setup eliminado del package",
        "package_id": package_id,
        "eliminado": {
            "part_id": part_id,
            "filename": filename
        }
    }

@router.delete("/{package_id}")
def eliminar_package_completo(package_id: int, db: Session = Depends(get_db)):
    """Elimina un package completo con todos sus setups"""
    package = package_service.obtener_package_por_id(db, package_id)
    if not package:
        raise HTTPException(404, "Package no encontrado")
    
    nombre = package.nombre
    total_parts = len(package.parts)
    
    db.delete(package)
    db.commit()
    
    return {
        "message": "Package eliminado exitosamente",
        "eliminado": {
            "id": package_id,
            "nombre": nombre,
            "total_setups_eliminados": total_parts
        }
    }

@router.post("/admin/cleanup")
def limpiar_packages_expirados(db: Session = Depends(get_db)):
    """Endpoint para job de limpieza manual"""
    count = package_service.eliminar_packages_expirados(db)
    return {
        "message": f"{count} packages expirados eliminados"
    }

@router.post("/{package_id}/agregar_setup")
async def agregar_setup_a_package(
    package_id: int,
    file: UploadFile = File(...),
    cantidad: int = Form(...),
    db: Session = Depends(get_db)
):
    """Agrega un setup (archivo .stp) a un package existente"""
    from app.models.package_part_model import PackagePart
    
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
        "message": "Setup agregado al package exitosamente",
        "package_id": package_id,
        "part": {
            "id": new_part.id,
            "filename": new_part.part_filename,
            "cantidad": new_part.cantidad,
            "part_number": parsed_data.get("part_number", "N/A")
        }
    }

@router.post("/preview")
async def preview_archivos(
    files: List[UploadFile] = File(...)
):
    """
    Paso 1: Sube archivos .stp y obtén vista previa con datos parseados.
    NO guarda nada en la base de datos.
    Retorna información de cada archivo para que el usuario asigne cantidades.
    """
    preview_data = []
    errores = []
    
    for idx, file in enumerate(files):
        # Validar extensión
        if not file.filename.endswith(".stp"):
            errores.append({
                "archivo": file.filename,
                "error": "Solo se aceptan archivos .stp"
            })
            continue
        
        # Guardar temporalmente
        temp_path = f"temp_{file.filename}"
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Parsear
            parsed_data = parse_setup(temp_path)
            
            # Limpiar temporal
            os.remove(temp_path)
            
            # Agregar a preview
            preview_data.append({
                "index": idx,
                "filename": file.filename,
                "part_number": parsed_data.get("part_number", "N/A"),
                "thickness": parsed_data.get("thickness", "N/A"),
                "sheet_size": parsed_data.get("sheet_size", "N/A"),
                "total_stations": len(parsed_data.get("stations", [])),
                "runtime": parsed_data.get("runtime", "N/A"),
                "uph": parsed_data.get("uph", "N/A"),
                "parsed_data_complete": parsed_data  # Datos completos para confirmar después
            })
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            errores.append({
                "archivo": file.filename,
                "error": f"Error al parsear: {str(e)}"
            })
    
    return {
        "message": "Preview generado. Asigna cantidades y usa /package/confirmar para guardar.",
        "total_archivos": len(files),
        "archivos_validos": len(preview_data),
        "archivos_con_error": len(errores),
        "preview": preview_data,
        "errores": errores if errores else None
    }

@router.post("/confirmar")
async def confirmar_package(
    db: Session = Depends(get_db),
    nombre: str = Form(...),
    descripcion: str = Form(""),
    preview_data: str = Form(...),  # JSON string con los datos del preview
    cantidades: str = Form(...)  # JSON string: "[10, 20, 30]"
):
    """
    Paso 2: Confirma y crea el package con las cantidades asignadas.
    Recibe el preview_data que retornó /preview y las cantidades correspondientes.
    """
    import json
    
    # Parsear preview_data
    try:
        preview_list = json.loads(preview_data)
    except json.JSONDecodeError:
        raise HTTPException(400, "preview_data debe ser JSON válido")
    
    # Parsear cantidades
    try:
        cantidades_clean = cantidades.strip()
        if not cantidades_clean.startswith('['):
            cantidades_clean = '[' + cantidades_clean + ']'
        cantidades_list = json.loads(cantidades_clean)
        cantidades_list = [int(x) for x in cantidades_list]
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(400, f"cantidades debe ser JSON válido: {str(e)}")
    
    # Validar que coincidan
    if len(preview_list) != len(cantidades_list):
        raise HTTPException(400, f"Número de archivos ({len(preview_list)}) y cantidades ({len(cantidades_list)}) no coincide")
    
    # Construir parts_data
    parts_data = []
    for item, cantidad in zip(preview_list, cantidades_list):
        parts_data.append({
            "filename": item["filename"].replace("temp_", "").replace(".stp", ""),
            "cantidad": cantidad,
            "parsed_data": item["parsed_data_complete"]
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