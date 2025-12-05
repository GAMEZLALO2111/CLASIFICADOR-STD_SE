from sqlalchemy.orm import Session
from app.models.package_model import Package
from app.models.package_part_model import PackagePart
from datetime import datetime
from typing import List, Optional

def crear_package(
    db: Session,
    nombre: str,
    descripcion: str,
    parts_data: List[dict]  # [{filename, cantidad, parsed_data}, ...]
) -> Package:
    nuevo_package = Package(
        nombre=nombre,
        descripcion=descripcion
    )
    db.add(nuevo_package)
    db.flush()  # Para obtener el ID
    
    # Agregar parts
    for part_data in parts_data:
        package_part = PackagePart(
            package_id=nuevo_package.id,
            part_filename=part_data["filename"],
            cantidad=part_data["cantidad"],
            parsed_data=part_data["parsed_data"]
        )
        db.add(package_part)
    
    db.commit()
    db.refresh(nuevo_package)
    return nuevo_package

def obtener_packages_activos(db: Session) -> List[Package]:
    """Obtiene solo packages no expirados"""
    ahora = datetime.utcnow()
    return db.query(Package).filter(Package.fecha_expiracion > ahora).all()

def obtener_package_por_id(db: Session, package_id: int) -> Optional[Package]:
    """Obtiene package si no está expirado"""
    ahora = datetime.utcnow()
    return db.query(Package).filter(
        Package.id == package_id,
        Package.fecha_expiracion > ahora
    ).first()

def eliminar_packages_expirados(db: Session) -> int:
    """Job de limpieza - elimina packages expirados"""
    ahora = datetime.utcnow()
    count = db.query(Package).filter(Package.fecha_expiracion <= ahora).delete()
    db.commit()
    return count