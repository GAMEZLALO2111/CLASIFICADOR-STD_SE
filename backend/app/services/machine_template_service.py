from sqlalchemy.orm import Session
from app.models.machine_template_model import MachineTemplate
from app.database.templates_data import TEMPLATES
from app.models.distribucion_model import EstiloEstacion
from typing import List, Optional, Dict
import json

def inicializar_templates(db: Session) -> int:
    """
    Carga los templates predefinidos en la BD si no existen
    Retorna cantidad de templates creados
    """
    count = 0
    for template_data in TEMPLATES:
        # Verificar si ya existe
        existe = db.query(MachineTemplate).filter(
            MachineTemplate.tipo_maquina == template_data["tipo_maquina"]
        ).first()
        
        if not existe:
            nuevo_template = MachineTemplate(**template_data)
            db.add(nuevo_template)
            count += 1
    
    db.commit()
    return count

def obtener_templates(db: Session) -> List[MachineTemplate]:
    """Obtiene todos los templates disponibles"""
    return db.query(MachineTemplate).all()

def obtener_template_por_id(db: Session, template_id: int) -> Optional[MachineTemplate]:
    """Obtiene un template por ID"""
    return db.query(MachineTemplate).filter(MachineTemplate.id == template_id).first()

def obtener_template_por_tipo(db: Session, tipo_maquina: str) -> Optional[MachineTemplate]:
    """Obtiene un template por tipo (4I, 2I, 45STA)"""
    return db.query(MachineTemplate).filter(MachineTemplate.tipo_maquina == tipo_maquina).first()


def calcular_estilo_unificado(setups: List, machine_template: Dict) -> List[EstiloEstacion]:
    """
    Calcula el estilo unificado para una máquina dada una lista de setups parseados.
    
    Args:
        setups: Lista de objetos Setup parseados (con part_number y tools)
        machine_template: Dict con estaciones_config de la máquina
    
    Returns:
        Lista de EstiloEstacion con la configuración unificada
    """
    # Parsear template si viene como string
    template_config = machine_template
    if isinstance(template_config, str):
        template_config = json.loads(template_config)
    
    # Extraer estaciones_config
    estaciones_config = template_config.get("estaciones_config", template_config)
    
    # Unificar herramientas de todos los setups
    herramientas_unificadas = {}
    
    for setup in setups:
        part_number = setup.part_number
        
        for tool in setup.tools:
            tn = tool.tool_number
            station_orig = tool.station
            angle = tool.angle if hasattr(tool, 'angle') else 0.0
            
            # Obtener configuración de estación original
            station_config = estaciones_config.get(station_orig, {})
            requiere_guia = station_config.get("tiene_guia", False)
            es_autoindex = station_config.get("es_autoindex", False)
            tipo_estacion = station_config.get("tipo", "A")
            
            if tn in herramientas_unificadas:
                # Ya existe, agregar el part a la lista
                unified = herramientas_unificadas[tn]
                if part_number not in unified["parts"]:
                    unified["parts"].append(part_number)
                unified["count"] += 1
            else:
                # Primera vez que vemos esta herramienta
                herramientas_unificadas[tn] = {
                    "tool_number": tn,
                    "angle": angle,
                    "requiere_guia": requiere_guia,
                    "es_autoindex": es_autoindex,
                    "tipo_estacion": tipo_estacion,
                    "station_orig": station_orig,
                    "count": 1,
                    "parts": [part_number]
                }
    
    # Generar estilo asignando estaciones
    estilo = []
    estaciones_asignadas = set()
    herramientas_lista = list(herramientas_unificadas.values())
    
    # Primero asignar autoindex (mantienen estación original)
    for tool_data in herramientas_lista:
        if tool_data["es_autoindex"]:
            station = tool_data["station_orig"]
            estaciones_asignadas.add(station)
            
            estilo.append(EstiloEstacion(
                estacion=station,
                tipo=tool_data["tipo_estacion"],
                tool_number=tool_data["tool_number"],
                angulo=tool_data["angle"],
                tiene_guia=tool_data["requiere_guia"],
                es_autoindex=True,
                parts_que_usan=tool_data["parts"]
            ))
    
    # Luego asignar resto de herramientas
    for tool_data in herramientas_lista:
        if tool_data["es_autoindex"]:
            continue  # Ya asignada
        
        tn = tool_data["tool_number"]
        
        # Buscar estación compatible (mismo tipo y guía)
        station_asignada = None
        for est, config in estaciones_config.items():
            if est in estaciones_asignadas:
                continue
            
            if (config["tipo"] == tool_data["tipo_estacion"] and
                config["tiene_guia"] == tool_data["requiere_guia"]):
                station_asignada = est
                estaciones_asignadas.add(est)
                break
        
        estilo.append(EstiloEstacion(
            estacion=station_asignada if station_asignada else "SIN_ASIGNAR",
            tipo=tool_data["tipo_estacion"],
            tool_number=tn,
            angulo=tool_data["angle"],
            tiene_guia=tool_data["requiere_guia"],
            es_autoindex=False,
            parts_que_usan=tool_data["parts"]
        ))
    
    return estilo