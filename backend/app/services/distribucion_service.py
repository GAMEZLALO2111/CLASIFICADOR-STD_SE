from sqlalchemy.orm import Session
from app.models.package_model import Package
from app.models.machine_model import Machine
from app.models.distribucion_model import *
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
import json


def agrupar_parts_por_preferencias(requerimientos: Dict) -> List[Dict]:
    """
    Agrupa parts por thickness, sheet_size y herramientas comunes
    para intentar asignarlos a la misma máquina (optimización)
    """
    grupos = []
    agrupados = set()
    
    for req_id, req_data in requerimientos.items():
        if req_id in agrupados:
            continue
        
        thickness = req_data["thickness"]
        sheet_size = tuple(req_data["sheet_size"])
        tools_set = set(req_data["tool_numbers"])
        
        # Crear grupo con este part
        grupo = {
            "part_ids": [req_id],
            "thickness": thickness,
            "sheet_size": sheet_size,
            "tools": tools_set
        }
        agrupados.add(req_id)
        
        # Buscar otros parts con mismas características
        for other_id, other_data in requerimientos.items():
            if other_id in agrupados:
                continue
            
            # Mismo thickness y sheet_size = grupo preferido
            if (other_data["thickness"] == thickness and 
                tuple(other_data["sheet_size"]) == sheet_size):
                grupo["part_ids"].append(other_id)
                grupo["tools"].update(other_data["tool_numbers"])
                agrupados.add(other_id)
        
        grupos.append(grupo)
    
    # Ordenar grupos: más herramientas compartidas primero (más eficiente)
    grupos.sort(key=lambda g: len(g["tools"]), reverse=True)
    
    return grupos


def ordenar_machines_por_preferencia(
    machines: List[Machine],
    thickness_objetivo: float,
    sheet_size_objetivo: Tuple,
    asignaciones_dict: Dict
) -> List[Machine]:
    """
    Ordena máquinas priorizando las que ya tienen parts con
    características similares (para maximizar unificación)
    """
    scored_machines = []
    
    for machine in machines:
        score = 0
        machine_data = asignaciones_dict[machine.id]
        
        # Prioridad 1: Ya tiene parts con mismo thickness
        for part in machine_data["parts_asignados"]:
            # Buscar thickness del part (aproximado)
            if abs(machine.thickness_min - thickness_objetivo) < 0.01:
                score += 10
                break
        
        # Prioridad 2: Tiene herramientas que podríamos unificar
        if len(machine_data["herramientas_unificadas"]) > 0:
            score += 5
        
        # Prioridad 3: Máquina con más tiempo disponible
        tiempo_disponible = 24 - machine_data["tiempo_usado"]
        score += tiempo_disponible / 10
        
        scored_machines.append((score, machine))
    
    # Ordenar por score descendente
    scored_machines.sort(key=lambda x: x[0], reverse=True)
    
    return [m for _, m in scored_machines]

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
    
    # 8. Crear respuesta
    distribucion_response = DistribucionResponse(
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
    
    # 9. Guardar distribución en BD (expira en 1 día)
    from app.models.distribucion_storage_model import DistribucionStorage
    import json
    
    dist_storage = DistribucionStorage(
        package_id=package_id,
        package_nombre=package.nombre,
        demanda=demanda,
        horas_objetivo=horas_objetivo,
        machine_ids=machine_ids,
        resultado_json=json.loads(distribucion_response.model_dump_json()),
        es_factible=es_factible
    )
    db.add(dist_storage)
    db.commit()
    db.refresh(dist_storage)
    
    return distribucion_response


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
        
        # Validar part_number
        part_number_value = parsed_data.get("part_number", {})
        if isinstance(part_number_value, dict):
            part_number_str = part_number_value.get("full", "N/A")
        else:
            part_number_str = str(part_number_value)
        
        requerimientos[part.id] = {
            "part_id": part.id,
            "filename": part.part_filename,
            "part_number": part_number_str,
            "cantidad_total": total_necesario,
            "cantidad_restante": total_necesario,
            "parsed_data": parsed_data,
            "uph": uph,
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
    Lógica principal de asignación con unificación de herramientas
    """
    asignaciones_dict = {}  # machine_id -> AsignacionMaquina
    
    # Inicializar estructura para cada máquina
    for machine in machines:
        asignaciones_dict[machine.id] = {
            "machine": machine,
            "parts_asignados": [],
            "tiempo_usado": 0.0,
            "herramientas_unificadas": {},  # TN -> info de unificación
            "estaciones_usadas": set(),
            "alertas": [],
            "errores": []
        }
    
    # Agrupar parts por preferencias (thickness, sheet_size, herramientas)
    grupos_preferencia = agrupar_parts_por_preferencias(requerimientos)
    
    # Procesar cada grupo (intentando mantenerlos juntos en misma máquina)
    for grupo in grupos_preferencia:
        # Procesar parts del grupo
        for req_id in grupo["part_ids"]:
            req_data = requerimientos[req_id]
            cantidad_pendiente = req_data["cantidad_total"]
            part_number_str = req_data["part_number"]
            
            # Convertir part_number dict a string si es necesario
            if isinstance(part_number_str, dict):
                part_number_str = part_number_str.get("full", "N/A")
            
            # Buscar máquina preferida para este grupo
            machines_ordenadas = ordenar_machines_por_preferencia(
                machines, 
                grupo["thickness"], 
                grupo["sheet_size"],
                asignaciones_dict
            )
            
            # Intentar asignar a máquinas disponibles (preferidas primero)
            for machine in machines_ordenadas:
                if cantidad_pendiente <= 0:
                    break
                
                machine_data = asignaciones_dict[machine.id]
                tiempo_disponible = horas_objetivo - machine_data["tiempo_usado"]
                
                if tiempo_disponible <= 0.1:  # Al menos 0.1 hora disponible
                    continue  # Máquina llena
                
                # Calcular cuánto puede producir esta máquina
                uph = req_data["parsed_data"].get("uph", 0)
                if uph <= 0:
                    machine_data["alertas"].append(f"Part {part_number_str} tiene UPH=0 o inválido")
                    continue
                
                # Piezas que puede hacer en el tiempo disponible
                piezas_posibles = int(tiempo_disponible * uph)
                piezas_a_asignar = min(piezas_posibles, cantidad_pendiente)
                
                if piezas_a_asignar <= 0:
                    continue
                
                # Calcular tiempo real que tomará
                horas_por_pieza = 1.0 / uph
                
                # Calcular tiempo real que tomará (verificación)
                horas_necesarias = piezas_a_asignar / uph
                
                # Validar que no exceda tiempo disponible
                if horas_necesarias > tiempo_disponible:
                    # Ajustar piezas para que quepa exactamente
                    piezas_a_asignar = int(tiempo_disponible * uph)
                    horas_necesarias = piezas_a_asignar / uph
                
                if piezas_a_asignar <= 0 or horas_necesarias <= 0:
                    continue
                
                # Crear asignación de este part a esta máquina
                asignacion_part = AsignacionPart(
                    part_filename=req_data["filename"],
                    part_number=part_number_str,
                    cantidad_requerida=req_data["cantidad_total"],
                    cantidad_asignada=piezas_a_asignar,
                    horas_corrida=round(horas_necesarias, 2),
                    estaciones_usadas=len(req_data["stations"]),
                    estaciones_unificadas=0  # Se calculará después
                )
                
                machine_data["parts_asignados"].append(asignacion_part)
                machine_data["tiempo_usado"] += horas_necesarias
                cantidad_pendiente -= piezas_a_asignar
                
                # Procesar herramientas para unificación
                procesar_herramientas_part(
                    req_data,
                    machine_data,
                    machine,
                    part_number_str
                )
        
            # Si quedó cantidad pendiente después de intentar todas las máquinas, es error crítico
            if cantidad_pendiente > 0:
                # Registrar error en todas las máquinas para indicar capacidad insuficiente
                error_msg = f"Part {req_data['part_number']}: Faltan {cantidad_pendiente} piezas sin asignar. CAPACIDAD INSUFICIENTE - Se requieren más máquinas."
                for machine_data in asignaciones_dict.values():
                    machine_data["errores"].append(error_msg)
                break  # Salir del ciclo de máquinas
    
    # Generar estilos para cada máquina
    resultado = []
    for machine_id, machine_data in asignaciones_dict.items():
        if len(machine_data["parts_asignados"]) == 0:
            continue  # Máquina no usada
        
        estilo, estilo_overflow = generar_estilo(
            machine_data["herramientas_unificadas"],
            machine_data["machine"]
        )
        
        # Actualizar conteo de estaciones unificadas
        for part in machine_data["parts_asignados"]:
            part.estaciones_unificadas = len(estilo)
        
        asignacion = AsignacionMaquina(
            machine_id=machine_data["machine"].id,
            machine_nombre=machine_data["machine"].nombre,
            tipo_maquina=machine_data["machine"].template.tipo_maquina,
            parts_asignados=machine_data["parts_asignados"],
            tiempo_total_usado=round(machine_data["tiempo_usado"], 2),
            tiempo_disponible=horas_objetivo,
            tiempo_sobrante=round(horas_objetivo - machine_data["tiempo_usado"], 2),
            estilo=estilo,
            estaciones_fuera_estilo=estilo_overflow,
            alertas=machine_data["alertas"],
            errores=machine_data["errores"]
        )
        
        resultado.append(asignacion)
    
    return resultado


def procesar_herramientas_part(req_data: Dict, machine_data: Dict, machine: Machine, part_number_str: str):
    """
    Procesa las herramientas de un part para unificación
    """
    tools_data = req_data["parsed_data"].get("tools_data", [])
    
    # Si tools_data está vacío, usar stations y tool_numbers
    if not tools_data:
        stations = req_data["parsed_data"].get("stations", [])
        tool_numbers = req_data["parsed_data"].get("tool_numbers", [])
        angles = req_data["parsed_data"].get("angles", [])
        
        if not angles:
            angles = [0.0] * len(tool_numbers)
        
        tools_data = [
            {"station": st, "tool_number": tn, "angle": ang}
            for st, tn, ang in zip(stations, tool_numbers, angles)
        ]
    
    template_config = machine.template.estaciones_config
    if isinstance(template_config, str):
        template_config = json.loads(template_config)
    
    for tool_info in tools_data:
        tn = tool_info["tool_number"]
        station_orig = tool_info["station"]
        angle = tool_info.get("angle", 0.0)
        
        # Determinar si requiere guía (por estación original)
        station_config = template_config.get(station_orig, {})
        requiere_guia = station_config.get("tiene_guia", False)
        es_autoindex = station_config.get("es_autoindex", False)
        tipo_estacion = station_config.get("tipo", "A")
        
        # Si ya está unificada esta herramienta, actualizar info
        if tn in machine_data["herramientas_unificadas"]:
            unified = machine_data["herramientas_unificadas"][tn]
            unified["count"] += 1
            if part_number_str not in unified["parts"]:
                unified["parts"].append(part_number_str)
            
            # Si es autoindex, mantener estación original
            if es_autoindex:
                unified["station_final"] = station_orig
                unified["es_autoindex"] = True
        else:
            # Primera vez que vemos esta herramienta
            machine_data["herramientas_unificadas"][tn] = {
                "tool_number": tn,
                "angle": angle,  # Tomamos ángulo de primera aparición
                "requiere_guia": requiere_guia,
                "es_autoindex": es_autoindex,
                "tipo_estacion": tipo_estacion,
                "station_orig": station_orig,
                "station_final": station_orig,  # Por defecto, misma estación
                "count": 1,
                "parts": [part_number_str]
            }


def generar_estilo(herramientas_unificadas: Dict, machine: Machine) -> Tuple[List[EstiloEstacion], List[EstiloEstacion]]:
    """
    Genera el estilo de distribución de herramientas por estación.
    Cada TN único va a UNA sola estación (unificación real).
    Retorna (estilo_normal, estilo_overflow)
    """
    template_config = machine.template.estaciones_config
    if isinstance(template_config, str):
        template_config = json.loads(template_config)
    
    estaciones_dañadas = [str(e) for e in machine.estaciones_dañadas]
    estaciones_disponibles = {
        est: config for est, config in template_config.items()
        if est not in estaciones_dañadas
    }
    
    estilo = []
    estilo_overflow = []
    estaciones_asignadas = set()
    
    # Obtener lista de herramientas ÚNICAS (la clave es el TN)
    herramientas_unicas = list(herramientas_unificadas.values())
    
    # Total de estaciones del template
    total_estaciones_disponibles = len(estaciones_disponibles)
    limite_overflow = total_estaciones_disponibles + 10
    
    # Primero asignar herramientas autoindex (no se mueven)
    for tool_data in herramientas_unicas:
        if tool_data["es_autoindex"]:
            station = tool_data["station_orig"]  # Mantener estación original
            estaciones_asignadas.add(station)
            
            estilo_item = EstiloEstacion(
                estacion=station,
                tipo=tool_data["tipo_estacion"],
                tool_number=tool_data["tool_number"],
                angulo=tool_data["angle"],
                tiene_guia=tool_data["requiere_guia"],
                es_autoindex=True,
                parts_que_usan=tool_data["parts"]
            )
            estilo.append(estilo_item)
    
    # Luego asignar resto de herramientas respetando tipo y guía
    for tool_data in herramientas_unicas:
        if tool_data["es_autoindex"]:
            continue  # Ya asignada
        
        tn = tool_data["tool_number"]
        
        # Buscar estación compatible
        station_asignada = None
        for est, config in estaciones_disponibles.items():
            if est in estaciones_asignadas:
                continue  # Ya ocupada
            
            # Debe coincidir tipo y guía
            if (config["tipo"] == tool_data["tipo_estacion"] and
                config["tiene_guia"] == tool_data["requiere_guia"]):
                station_asignada = est
                estaciones_asignadas.add(est)
                break
        
        estilo_item = EstiloEstacion(
            estacion=station_asignada if station_asignada else "SIN_ASIGNAR",
            tipo=tool_data["tipo_estacion"],
            tool_number=tn,
            angulo=tool_data["angle"],
            tiene_guia=tool_data["requiere_guia"],
            es_autoindex=False,
            parts_que_usan=tool_data["parts"]
        )
        
        # Decidir si va a estilo normal o overflow
        total_asignadas = len(estilo) + len(estilo_overflow) + 1
        
        if station_asignada and total_asignadas <= total_estaciones_disponibles:
            # Cabe en estilo normal
            estilo.append(estilo_item)
        elif total_asignadas <= limite_overflow:
            # Va a overflow pero dentro de tolerancia +10
            estilo_overflow.append(estilo_item)
        else:
            # Excede incluso el límite +10
            estilo_overflow.append(estilo_item)
    
    return estilo, estilo_overflow


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
    
    # Verificar si todas las cantidades fueron asignadas (CRÍTICO)
    total_piezas_asignadas = {}
    for asig in asignaciones:
        for part in asig.parts_asignados:
            part_num = part.part_number
            if part_num not in total_piezas_asignadas:
                total_piezas_asignadas[part_num] = 0
            total_piezas_asignadas[part_num] += part.cantidad_asignada
    
    parts_faltantes = []
    for req_data in requerimientos.values():
        part_num = req_data["part_number"]
        requerido = req_data["cantidad_total"]
        asignado = total_piezas_asignadas.get(part_num, 0)
        
        if asignado < requerido:
            faltante = requerido - asignado
            parts_faltantes.append(f"{part_num} (faltan {faltante} piezas)")
            errores.append(f"Part {part_num}: Faltan {faltante} piezas sin asignar")
            es_factible = False
    
    # Si hay parts faltantes, agregar mensaje claro de capacidad insuficiente
    if parts_faltantes:
        errores.insert(0, f"❌ CAPACIDAD INSUFICIENTE: Se requieren más máquinas para completar todos los parts. Parts incompletos: {', '.join(parts_faltantes)}")
    
    # Verificar overflow de estaciones
    maquinas_con_overflow_critico = []
    for asig in asignaciones:
        total_estaciones = len(asig.estilo) + len(asig.estaciones_fuera_estilo)
        
        if len(asig.estaciones_fuera_estilo) > 0:
            if len(asig.estaciones_fuera_estilo) <= 10:
                alertas.append(
                    f"⚠️ Máquina {asig.machine_nombre}: {len(asig.estaciones_fuera_estilo)} "
                    f"herramientas fuera del estilo (dentro del límite de +10 tolerancia)"
                )
            else:
                maquinas_con_overflow_critico.append(f"{asig.machine_nombre} ({len(asig.estaciones_fuera_estilo)} herramientas fuera)")
                errores.append(
                    f"❌ Máquina {asig.machine_nombre}: {len(asig.estaciones_fuera_estilo)} "
                    f"herramientas fuera del estilo (EXCEDE límite de +10 estaciones)"
                )
                es_factible = False
    
    # Mensaje adicional si hay overflow crítico
    if maquinas_con_overflow_critico:
        errores.insert(0, f"❌ OVERFLOW CRÍTICO: Las siguientes máquinas exceden capacidad: {', '.join(maquinas_con_overflow_critico)}. Redistribuir a más máquinas.")
        
        # Verificar tiempo sobrante
        if asig.tiempo_sobrante > horas_objetivo * 0.5:
            alertas.append(
                f"Máquina {asig.machine_nombre}: Tiempo sobrante alto ({asig.tiempo_sobrante:.1f}h de {horas_objetivo}h)"
            )
    
    # Alertas de máquinas no utilizadas
    if len(asignaciones) == 0:
        errores.append("No se pudo asignar ninguna máquina (verificar compatibilidad)")
        es_factible = False
    
    return es_factible, alertas, errores


def generar_resumen(
    asignaciones: List[AsignacionMaquina],
    demanda: int,
    horas_objetivo: float
) -> Dict:
    """
    Genera resumen de la distribución
    """
    total_horas_usadas = sum(a.tiempo_total_usado for a in asignaciones)
    total_parts_procesados = sum(len(a.parts_asignados) for a in asignaciones)
    
    return {
        "total_maquinas_usadas": len(asignaciones),
        "demanda_objetivo": demanda,
        "horas_objetivo": horas_objetivo,
        "total_horas_productivas": round(total_horas_usadas, 2),
        "eficiencia_promedio": round((total_horas_usadas / (len(asignaciones) * horas_objetivo) * 100) if asignaciones else 0, 1),
        "total_parts_distintos": total_parts_procesados
    }
