from pydantic import BaseModel
from typing import List, Dict, Optional

class DistribucionRequest(BaseModel):
    """Request para crear una distribución"""
    package_id: int
    demanda: int  # Cantidad de productos finales
    horas_objetivo: float  # Tiempo disponible (ej: 24, 36, 12)
    machine_ids: List[int]  # IDs de máquinas disponibles para usar

class AsignacionPart(BaseModel):
    """Asignación de un part number a una máquina"""
    part_filename: str
    part_number: str
    cantidad_requerida: int
    cantidad_asignada: int
    horas_corrida: float
    estaciones_usadas: int
    estaciones_unificadas: int

class EstiloEstacion(BaseModel):
    """Distribución de herramienta en una estación"""
    estacion: str
    tipo: str  # A, B, C, D, E
    tool_number: str
    angulo: float
    tiene_guia: bool
    es_autoindex: bool
    parts_que_usan: List[str]  # Lista de part_numbers que usan esta estación

class AsignacionMaquina(BaseModel):
    """Resultado de asignación para una máquina"""
    machine_id: int
    machine_nombre: str
    tipo_maquina: str
    parts_asignados: List[AsignacionPart]
    tiempo_total_usado: float
    tiempo_disponible: float
    tiempo_sobrante: float
    estilo: List[EstiloEstacion]
    estaciones_fuera_estilo: List[EstiloEstacion]  # Si excede capacidad
    alertas: List[str]
    errores: List[str]

class DistribucionResponse(BaseModel):
    """Respuesta completa de la distribución"""
    package_id: int
    package_nombre: str
    demanda: int
    horas_objetivo: float
    asignaciones: List[AsignacionMaquina]
    es_factible: bool
    alertas_generales: List[str]
    errores_generales: List[str]
    resumen: Dict
