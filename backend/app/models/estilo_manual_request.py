from pydantic import BaseModel, Field
from typing import List, Optional


class EstacionManual(BaseModel):
    """Configuración de una estación con su herramienta"""
    estacion: str = Field(..., description="Número de estación (ej: '201', '103')")
    tipo: str = Field(..., description="Tipo de herramienta (A, B, C, D, E)")
    tool_number: str = Field(..., description="Número de herramienta")
    angulo: int = Field(0, description="Ángulo de la herramienta (0, 45, 90)")
    tiene_guia: bool = Field(False, description="Si la herramienta tiene guía")
    es_autoindex: bool = Field(False, description="Si es autoindex")
    parts_que_usan: List[str] = Field(default_factory=list, description="Parts que usan esta estación")


class CrearEstiloManualRequest(BaseModel):
    """Request para crear un estilo manual"""
    nombre: str = Field(..., description="Nombre descriptivo del estilo")
    machine_id: int = Field(..., description="ID de la máquina donde se aplicará")
    part_numbers: List[str] = Field(..., description="Lista de números de parte a procesar")
    estaciones: List[EstacionManual] = Field(..., description="Configuración de estaciones y herramientas")
    notas: Optional[str] = Field(None, description="Notas adicionales del usuario")


class EstiloManualResponse(BaseModel):
    """Response con el estilo manual creado"""
    id: int
    nombre: str
    machine_id: int
    machine_nombre: str
    tipo_maquina: str
    part_numbers: List[str]
    estilo_json: List[dict]
    notas: Optional[str]
    created_at: str
    expires_at: str
    activa: bool

    class Config:
        from_attributes = True
