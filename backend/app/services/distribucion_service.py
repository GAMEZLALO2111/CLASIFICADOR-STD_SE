from sqlalchemy.orm import Session
from backend.app.models.package_model import Package
from backend.app.models.machine_model import Machine
from backend.app.models.distribucion_model import *
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
import json

def crear_distribucion(
    db: Session,
    package_id: int,
    demanda: int,
    horas_objetivo: float,
    machine_ids: List[int]
) -> DistribucionResponse:
    """
    Algoritmo principal de distribución de parts a máquinas
    """
    
    # 1. Obtener package y validar
    package = db.query(Package).filter(Package.id == package_id).first()
    if not package:
        raise ValueError(f"Package {package_id} no encontrado")
    
    if not package.parts or len(package.parts) == 0:
        raise ValueError(f"Package {package_id} no tiene setups")
    
    # 2. Obtener máquinas y validar
    machines = db.query(Machine).filter(
        Machine.id.in_(machine_ids),
        Machine.activa == 1
    ).all()
    
    if not machines:
        raise ValueError("No hay máquinas activas disponibles")
    
    # 3. Calcular requerimientos totales
    requerimientos = calcular_requerimientos(package, demanda)
    
    # 4. Aplicar reglas duras (filtrar máquinas incompatibles)
    machines_compatibles = aplicar_reglas_duras(package, machines, requerimientos)
    
    if not machines_compatibles:
        return DistribucionResponse(
            package_id=package_id,
            package_nombre=package.nombre,
            demanda=demanda,
            horas_objetivo=horas_objetivo,
            asignaciones=[],
            es_factible=False,
            alertas_generales=[],
            errores_generales=["No hay máquinas compatibles con las especificaciones del package"],
            resumen={}
        )
    
    # 5. Asignar parts a máquinas
    asignaciones = asignar_parts_a_machines(
        package, 
        requerimientos, 
        machines_compatibles, 
        horas_objetivo,
        db
    )
    
    # 6. Evaluar factibilidad
    es_factible, alertas_gen, errores_gen = evaluar_factibilidad(
        asignaciones, 
        requerimientos, 
        horas_objetivo
    )
    
    # 7. Generar resumen
    resumen = generar_resumen(asignaciones, demanda, horas_objetivo)
    
    return DistribucionResponse(
        package_id=package_id,
        package_nombre=package.nombre,
        demanda=demanda,
        horas_objetivo=horas_objetivo,
        asignaciones=asignaciones,
        es_factible=es_factible,
        alertas_generales=alertas_gen,
        errores_generales=errores_gen,
        resumen=resumen
    )


def calcular_requerimientos(package: Package, demanda: int) -> Dict:
    """
    Calcula cuántas piezas se necesitan de cada part number
    """
    requerimientos = {}
    
    for part in package.parts:
        cantidad_por_producto = part.cantidad
        total_necesario = cantidad_por_producto * demanda
        
        parsed_data = part.parsed_data
        uph = parsed_data.get("uph", 0)
        horas_por_pieza = 1 / uph if uph > 0 else 0
        
        requerimientos[part.id] = {
            "part_id": part.id,
            "filename": part.part_filename,
            "part_number": parsed_data.get("part_number", {}).get("full", "N/A"),
            "cantidad_total": total_necesario,
            "cantidad_restante": total_necesario,
            "parsed_data": parsed_data,
            "horas_por_pieza": horas_por_pieza,
            "thickness": parsed_data.get("thickness", 0),
            "sheet_size": parsed_data.get("sheet_size", [0, 0]),
            "stations": parsed_data.get("stations", []),
            "tool_numbers": parsed_data.get("tool_numbers", []),
        }
    
    return requerimientos


def aplicar_reglas_duras(
    package: Package, 
    machines: List[Machine], 
    requerimientos: Dict
) -> List[Machine]:
    """
    Filtra máquinas que NO cumplen reglas duras
    """
    compatibles = []
    
    for machine in machines:
        es_compatible = True
        
        # Obtener template config - ya es dict, no necesita json.loads
        if hasattr(machine.template, 'estaciones_config'):
            if isinstance(machine.template.estaciones_config, str):
                template_config = json.loads(machine.template.estaciones_config)
            else:
                template_config = machine.template.estaciones_config
        else:
            template_config = {}
        
        estaciones_dañadas_str = [str(e) for e in machine.estaciones_dañadas]
        estaciones_disponibles = [est for est in template_config.keys() if est not in estaciones_dañadas_str]
        
        for req_data in requerimientos.values():
            # Regla 1: Thickness compatible
            thickness = req_data["thickness"]
            if machine.thickness_min > 0 and machine.thickness_max > 0:
                if not (machine.thickness_min <= thickness <= machine.thickness_max):
                    es_compatible = False
                    break
            
            # Regla 2: Sheet size cabe en mesa
            sheet_x, sheet_y = req_data["sheet_size"]
            if machine.mesa_x > 0 and machine.mesa_y > 0:
                if sheet_x > machine.mesa_x or sheet_y > machine.mesa_y:
                    es_compatible = False
                    break
            
            # Regla 3: Tipo de máquina (por ahora todas compatibles, pero podría haber restricciones)
            # TODO: Agregar lógica si ciertos parts solo pueden ir en ciertos tipos
        
        if es_compatible:
            compatibles.append(machine)
    
    return compatibles


def asignar_parts_a_machines(
    package: Package,
    requerimientos: Dict,
    machines: List[Machine],
    horas_objetivo: float,
    db: Session
) -> List[AsignacionMaquina]:
    """
    Lógica principal de asignación
    """
    asignaciones = []
    idx_machine = 0
    
    for req_data in requerimientos.values():
        if req_data["cantidad_restante"] <= 0:
            continue
        
        # Tomar siguiente máquina disponible (round-robin simple)
        if idx_machine >= len(machines):
            # TODO: Manejar caso donde no hay más máquinas
            break
        
        machine = machines[idx_machine % len(machines)]
        
        # Crear asignación para esta máquina
        # TODO: Implementar unificación de herramientas
        # TODO: Calcular estilo
        # TODO: Calcular tiempos
        
        idx_machine += 1
    
    return asignaciones


def evaluar_factibilidad(
    asignaciones: List[AsignacionMaquina],
    requerimientos: Dict,
    horas_objetivo: float
) -> Tuple[bool, List[str], List[str]]:
    """
    Evalúa si la distribución es factible
    """
    alertas = []
    errores = []
    es_factible = True
    
    # TODO: Implementar lógica de evaluación
    
    return es_factible, alertas, errores


def generar_resumen(
    asignaciones: List[AsignacionMaquina],
    demanda: int,
    horas_objetivo: float
) -> Dict:
    """
    Genera resumen de la distribución
    """
    return {
        "total_maquinas_usadas": len(asignaciones),
        "demanda_objetivo": demanda,
        "horas_objetivo": horas_objetivo
    }
