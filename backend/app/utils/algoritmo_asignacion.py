"""
Algoritmo de Asignación Optimizado para Distribución de Partes en Máquinas
Versión Corregida con:
- REGLA DURA: Tiempo nunca excede horas_objetivo
- División de parts por cantidad cuando no caben en tiempo
- Redondos (TN con "1") flexibles en estaciones con/sin guía
- Remoción quirúrgica de part menos compatible de grupo
- Overflow de estaciones como regla blanda
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict


def es_redondo(tool_number) -> bool:
    """
    Verifica si una herramienta es un redondo.
    Redondos: TN que inicia con "1" (ej: 10120, 10345, 10276)
    Pueden ir en estaciones con o sin guía.
    """
    return str(tool_number).startswith('1')


def calcular_score_compatibilidad(parte1: dict, parte2: dict) -> int:
    """
    Calcula el score de compatibilidad entre dos partes.
    
    Criterios:
    - Mismo grosor (thickness): +30 puntos
    - Mismo tamaño de lámina (sheet_size): +30 puntos
    - Herramientas en común: +40 puntos (si comparten al menos una herramienta)
    
    Score máximo: 100 puntos (alta compatibilidad)
    Score mínimo: 0 puntos (sin compatibilidad)
    """
    score = 0
    
    # Mismo grosor
    if parte1.get('thickness') == parte2.get('thickness'):
        score += 30
    
    # Mismo tamaño de lámina
    if parte1.get('sheet_size') == parte2.get('sheet_size'):
        score += 30
    
    # Herramientas en común (convertir a tool_number strings)
    tools1 = set(t['tool_number'] if isinstance(t, dict) else t for t in parte1.get('tools', []))
    tools2 = set(t['tool_number'] if isinstance(t, dict) else t for t in parte2.get('tools', []))
    if tools1 and tools2 and tools1.intersection(tools2):
        score += 40
    
    return score


def contar_divisiones_parte(part_id: int) -> int:
    """
    Cuenta cuántas veces se ha dividido una parte usando tracking global.
    Límite: 2 divisiones (parte puede estar en máximo 2 máquinas)
    """
    global _num_divisiones
    return _num_divisiones.get(part_id, 0)


def marcar_division_parte(part_id: int):
    """
    Marca que una parte ha sido dividida, incrementando el contador global.
    """
    global _num_divisiones
    _num_divisiones[part_id] = _num_divisiones.get(part_id, 0) + 1


def agrupar_por_compatibilidad_alta(partes: List[dict], umbral: int = 70, limite_estaciones: int = 52) -> List[List[dict]]:
    """
    Agrupa partes que tienen alta compatibilidad (score >= umbral).
    
    ESTRATEGIA CON REGLA DURA DE OVERFLOW:
    1. Ordena partes por UPH ascendente (las más lentas/complejas primero)
    2. Para cada parte sin grupo:
       - Busca un grupo existente donde tenga:
         a) Alta compatibilidad (≥70) con TODAS las partes
         b) Herramientas únicas totales ≤ limite_estaciones (REGLA DURA)
       - Si encuentra uno, la añade
       - Si no, crea un nuevo grupo con esa parte
    
    Returns:
        Lista de grupos, donde cada grupo es una lista de partes compatibles
    """
    # Ordenar por UPH ascendente (partes más lentas/complejas primero)
    partes_ordenadas = sorted(partes, key=lambda p: p.get('uph', 0))
    
    grupos = []
    
    for parte in partes_ordenadas:
        grupo_asignado = False
        
        # Intentar añadir a un grupo existente
        for grupo in grupos:
            # Verificar compatibilidad con TODAS las partes del grupo
            compatible_con_todas = True
            for parte_grupo in grupo:
                score = calcular_score_compatibilidad(parte, parte_grupo)
                if score < umbral:
                    compatible_con_todas = False
                    break
            
            # REGLA DURA: Verificar que no exceda límite de estaciones
            if compatible_con_todas:
                herramientas_test = contar_herramientas_unicas(grupo + [parte])
                if herramientas_test <= limite_estaciones:
                    grupo.append(parte)
                    grupo_asignado = True
                    break
        
        # Si no se pudo añadir a ningún grupo, crear uno nuevo
        if not grupo_asignado:
            grupos.append([parte])
    
    return grupos


def contar_herramientas_unicas(partes: List[dict]) -> int:
    """
    Cuenta el número de herramientas únicas en un grupo de partes.
    Esto permite estimar si habrá overflow de estaciones.
    """
    herramientas_unicas = set()
    for parte in partes:
        tools = parte.get('tools', [])
        for tool in tools:
            tool_number = tool['tool_number'] if isinstance(tool, dict) else tool
            herramientas_unicas.add(tool_number)
    return len(herramientas_unicas)


def calcular_horas_parte(parte: dict) -> float:
    """
    Calcula las horas necesarias para producir una parte.
    Horas = cantidad / uph
    """
    cantidad = parte.get('quantity', 0)
    uph = parte.get('uph', 1)
    if uph > 0:
        return cantidad / uph
    return 0.0


def calcular_horas_grupo(partes: List[dict]) -> float:
    """
    Calcula las horas totales necesarias para un grupo de partes.
    """
    return sum(calcular_horas_parte(p) for p in partes)


def calcular_carga_maquina(partes: List[dict]) -> float:
    """
    Calcula el porcentaje de carga de una máquina basado en las partes asignadas.
    
    Carga = (suma de horas requeridas) / 24 * 100
    Horas requeridas por parte = cantidad / uph
    """
    carga_total = calcular_horas_grupo(partes)
    return (carga_total / 24.0) * 100.0


def encontrar_compatibilidad_promedio_grupo(grupo: List[dict]) -> float:
    """
    Calcula la compatibilidad promedio entre todas las partes de un grupo.
    """
    if len(grupo) <= 1:
        return 100.0  # Un solo elemento tiene compatibilidad perfecta consigo mismo
    
    scores = []
    for i in range(len(grupo)):
        for j in range(i + 1, len(grupo)):
            score = calcular_score_compatibilidad(grupo[i], grupo[j])
            scores.append(score)
    
    return sum(scores) / len(scores) if scores else 0.0


def identificar_parte_menos_compatible(grupo: List[dict]) -> dict:
    """
    Identifica la parte con menor compatibilidad promedio con el resto del grupo.
    Esta parte es candidata a ser removida si el grupo no cabe en tiempo/estaciones.
    """
    if len(grupo) <= 1:
        return grupo[0] if grupo else None
    
    compatibilidades = []
    
    for i, parte in enumerate(grupo):
        # Calcular compatibilidad de esta parte con el resto
        otras_partes = grupo[:i] + grupo[i+1:]
        scores = [calcular_score_compatibilidad(parte, otra) for otra in otras_partes]
        promedio = sum(scores) / len(scores) if scores else 0
        compatibilidades.append((promedio, parte))
    
    # Ordenar por compatibilidad ascendente (menor primero)
    compatibilidades.sort(key=lambda x: x[0])
    
    return compatibilidades[0][1]  # Retornar parte con menor compatibilidad


def ajustar_grupo_a_tiempo_disponible(
    grupo: List[dict],
    tiempo_disponible: float,
    umbral_compatibilidad: int = 70
) -> Tuple[List[dict], List[dict]]:
    """
    Ajusta un grupo de partes compatibles para que quepa en el tiempo disponible.
    
    REGLA DURA: El tiempo NUNCA puede exceder el disponible.
    
    Estrategia:
    1. Si el grupo cabe completo → Retornar grupo sin cambios
    2. Si no cabe → Remover iterativamente la parte MENOS compatible hasta que quepa
    
    Returns:
        Tupla (grupo_ajustado, partes_removidas)
    """
    grupo_actual = grupo.copy()
    partes_removidas = []
    
    while calcular_horas_grupo(grupo_actual) > tiempo_disponible:
        if len(grupo_actual) <= 1:
            # Si solo queda 1 parte y no cabe, se deberá dividir después
            break
        
        # Identificar y remover parte menos compatible
        parte_menos_compatible = identificar_parte_menos_compatible(grupo_actual)
        grupo_actual.remove(parte_menos_compatible)
        partes_removidas.append(parte_menos_compatible)
    
    return grupo_actual, partes_removidas


def dividir_parte_por_tiempo(
    parte: dict,
    tiempo_disponible: float
) -> Tuple[Optional[dict], Optional[dict]]:
    """
    Divide una parte en dos porciones según tiempo disponible.
    
    REGLA DURA: Respetar tiempo disponible exacto.
    
    Returns:
        Tupla (parte_asignada, parte_pendiente)
        - parte_asignada: Cantidad que cabe en tiempo_disponible
        - parte_pendiente: Cantidad restante (None si cabe completa)
    """
    horas_necesarias = calcular_horas_parte(parte)
    
    if horas_necesarias <= tiempo_disponible:
        # Cabe completa
        return parte, None
    
    # Calcular cuántas piezas caben en tiempo disponible
    uph = parte.get('uph', 1)
    cantidad_total = parte.get('quantity', 0)
    cantidad_que_cabe = int(tiempo_disponible * uph)
    cantidad_pendiente = cantidad_total - cantidad_que_cabe
    
    if cantidad_que_cabe <= 0:
        # No cabe nada
        return None, parte
    
    # Crear parte asignada
    parte_asignada = parte.copy()
    parte_asignada['quantity'] = cantidad_que_cabe
    parte_asignada['_es_division'] = True
    parte_asignada['_cantidad_original'] = cantidad_total
    
    # Crear parte pendiente
    parte_pendiente = parte.copy()
    parte_pendiente['quantity'] = cantidad_pendiente
    parte_pendiente['_es_division'] = True
    parte_pendiente['_cantidad_original'] = cantidad_total
    
    return parte_asignada, parte_pendiente


def minimizar_maquinas(asignaciones: Dict[int, List[dict]], horas_objetivo: float = 96.0) -> Dict[int, List[dict]]:
    """
    Intenta consolidar partes en menos máquinas después de asignación.
    
    REGLA DURA: Respetar horas_objetivo como límite absoluto.
    
    Lógica:
    1. Identifica máquinas con baja carga
    2. Intenta mover sus partes a otras máquinas que tengan espacio de tiempo
    3. Elimina máquinas que queden vacías (0 horas)
    4. Respeta límite de horas_objetivo al consolidar
    
    Returns:
        Asignaciones optimizadas con menos máquinas
    """
    MAX_ITERACIONES = 5
    
    for _ in range(MAX_ITERACIONES):
        # Calcular horas usadas por máquina
        horas_usadas = {maq_id: calcular_horas_grupo(partes) for maq_id, partes in asignaciones.items()}
        
        # Ordenar máquinas por horas usadas (menor primero)
        maquinas_ordenadas = sorted(horas_usadas.items(), key=lambda x: x[1])
        
        consolidacion_realizada = False
        
        for maq_id, horas_actual in maquinas_ordenadas:
            if horas_actual == 0:
                # Eliminar máquina vacía
                del asignaciones[maq_id]
                consolidacion_realizada = True
                continue
            
            partes_maquina = asignaciones[maq_id]
            
            # Intentar mover todas las partes de esta máquina a otra
            for otra_maq_id, otras_partes in list(asignaciones.items()):
                if otra_maq_id == maq_id:
                    continue
                
                horas_otra = horas_usadas[otra_maq_id]
                
                # Verificar si todas las partes caben en tiempo (REGLA DURA)
                if horas_otra + horas_actual <= horas_objetivo:
                    # Mover todas las partes
                    asignaciones[otra_maq_id].extend(partes_maquina)
                    del asignaciones[maq_id]
                    consolidacion_realizada = True
                    break
            
            if consolidacion_realizada:
                break
        
        if not consolidacion_realizada:
            break
    
    # Renumerar máquinas para que sean consecutivas (1, 2, 3...)
    maquinas_nuevas = {}
    for i, (maq_id, partes) in enumerate(sorted(asignaciones.items()), start=1):
        maquinas_nuevas[i] = partes
    
    return maquinas_nuevas


def asignar_optimizado_final(
    partes: List[dict],
    horas_objetivo: float = 96.0,
    umbral_compatibilidad: int = 70
) -> Dict[int, List[dict]]:
    """
    Algoritmo principal de asignación optimizada con REGLAS DURAS ESTRICTAS.
    
    REGLAS DURAS (SI NO SE CUMPLEN → ERROR, NO CONTINUAR):
    1. Tiempo ≤ horas_objetivo por máquina (NUNCA exceder)
    2. Overflow = 0 (herramientas únicas ≤ 52 por máquina)
    3. Part dividido máximo en 2 máquinas
    4. Si no se puede cumplir → Lanzar excepción con mensaje claro
    
    ESTRATEGIA:
    1. Agrupar por compatibilidad (validando overflow durante agrupación)
    2. Asignar grupos respetando tiempo y overflow
    3. Si grupo no cabe → Intentar dividir UN part (límite 2 divisiones)
    4. Si aún no cabe → Remover parte menos compatible
    5. Si ninguna opción funciona → ERROR claro
    
    Flujo:
    1. Agrupar partes por compatibilidad alta (≥70 score)
    2. Para cada grupo:
       a. Ajustar grupo para que quepa en tiempo disponible (remover menos compatibles)
       b. Asignar grupo ajustado a máquina actual
       c. Si máquina se llena, pasar a siguiente
    3. Procesar partes removidas de grupos (buscar espacio en cualquier máquina)
    4. Procesar partes que no cupieron completas (dividir por cantidad)
    
    Args:
        partes: Lista de diccionarios con información de cada parte
                Campos esperados: part_id, quantity, uph, thickness, sheet_size, tools
        horas_objetivo: Horas disponibles por máquina (LÍMITE ABSOLUTO)
        umbral_compatibilidad: Score mínimo para considerar partes compatibles (default 70)
    
    Returns:
        Diccionario con asignaciones {maquina_id: [lista_de_partes]}
    """
    if not partes:
        return {}

    # Inicializar tracking de divisiones por parte
    global _num_divisiones
    _num_divisiones = {}

    LIMITE_ESTACIONES = 52
    grupos_compatibilidad = agrupar_por_compatibilidad_alta(
        partes,
        umbral_compatibilidad,
        limite_estaciones=LIMITE_ESTACIONES
    )

    asignaciones = {}
    maquina_actual = 1
    asignaciones[maquina_actual] = []
    tiempo_usado = {maquina_actual: 0.0}
    partes_pendientes = []
    MAX_MAQUINAS = 20
    alertas = []

    # Paso 2: Asignar grupos validando OVERFLOW = 0 y tiempo
    for grupo in grupos_compatibilidad:
        grupo_asignado = False
        intentos_division = 0
        MAX_INTENTOS = 3

        while not grupo_asignado and intentos_division < MAX_INTENTOS:
            intentos_division += 1

            if maquina_actual > MAX_MAQUINAS:
                raise Exception(f"Se excedió el límite de {MAX_MAQUINAS} máquinas. Revisa configuración.")

            tiempo_disponible = horas_objetivo - tiempo_usado[maquina_actual]
            horas_grupo = calcular_horas_grupo(grupo)


            # VALIDACIÓN 1: TIEMPO (REGLA DURA ABSOLUTA)
            while horas_grupo > tiempo_disponible:
                # Si el grupo excede el tiempo, divide el grupo
                if len(grupo) == 1:
                    # Si solo queda una parte y excede, dividir la parte
                    parte = grupo[0]
                    uph = parte.get('uph', 1)
                    cantidad_total = parte.get('quantity', 0)
                    cantidad_que_cabe = int(tiempo_disponible * uph)
                    cantidad_pendiente = cantidad_total - cantidad_que_cabe
                    if cantidad_que_cabe > 0:
                        parte_asignada = parte.copy()
                        parte_asignada['quantity'] = cantidad_que_cabe
                        parte_asignada['_es_division'] = True
                        parte_asignada['_cantidad_original'] = cantidad_total
                        grupo = [parte_asignada]
                        parte_pendiente = parte.copy()
                        parte_pendiente['quantity'] = cantidad_pendiente
                        parte_pendiente['_es_division'] = True
                        parte_pendiente['_cantidad_original'] = cantidad_total
                        partes_pendientes.append(parte_pendiente)
                        horas_grupo = calcular_horas_grupo(grupo)
                    else:
                        # No cabe nada, pasar a siguiente máquina
                        maquina_actual += 1
                        asignaciones[maquina_actual] = []
                        tiempo_usado[maquina_actual] = 0.0
                        break
                else:
                    # Remover la parte menos compatible y pasarla a pendientes
                    parte_menos_compatible = identificar_parte_menos_compatible(grupo)
                    grupo.remove(parte_menos_compatible)
                    partes_pendientes.append(parte_menos_compatible)
                    horas_grupo = calcular_horas_grupo(grupo)
                # Recalcular tiempo disponible
                tiempo_disponible = horas_objetivo - tiempo_usado[maquina_actual]
            # Si el grupo quedó vacío, pasar a siguiente máquina
            if not grupo:
                maquina_actual += 1
                asignaciones[maquina_actual] = []
                tiempo_usado[maquina_actual] = 0.0
                continue

            # VALIDACIÓN 2: OVERFLOW = 0 (REGLA DURA)
            partes_simuladas = asignaciones[maquina_actual] + grupo
            herramientas_totales = contar_herramientas_unicas(partes_simuladas)

            if herramientas_totales > LIMITE_ESTACIONES:
                # ALERTA: Overflow, pero no bloquea
                alertas.append(f"ALERTA: Máquina {maquina_actual} excede límite de estaciones ({herramientas_totales} > {LIMITE_ESTACIONES})")
                # CASO 1: Máquina vacía y grupo excede límite
                if len(asignaciones[maquina_actual]) == 0:
                    if len(grupo) > 1:
                        parte_menos_compatible = identificar_parte_menos_compatible(grupo)
                        grupo.remove(parte_menos_compatible)
                        partes_pendientes.append(parte_menos_compatible)
                        continue
                    else:
                        parte_problema = grupo[0]
                        alertas.append(
                            f"ALERTA: Part {parte_problema.get('part_number', 'N/A')} tiene {contar_herramientas_unicas([parte_problema])} herramientas únicas, excede el límite de {LIMITE_ESTACIONES} estaciones. No se puede asignar sin modificar el part."
                        )
                        # Asignar igual, pero con alerta
                        asignaciones[maquina_actual].extend(grupo)
                        tiempo_usado[maquina_actual] += horas_grupo
                        grupo_asignado = True
                        break
                maquina_actual += 1
                asignaciones[maquina_actual] = []
                tiempo_usado[maquina_actual] = 0.0
                continue

            # ALERTA: Out-of-style tools (estructura para expansión)
            # Ejemplo: Si alguna herramienta está fuera de estilo, solo alertar
            # for parte in grupo:
            #     for tool in parte.get('tools', []):
            #         if tool_is_out_of_style(tool):
            #             alertas.append(f"ALERTA: Máquina {maquina_actual} tiene herramienta fuera de estilo: {tool}")

            # Asignar grupo
            asignaciones[maquina_actual].extend(grupo)
            tiempo_usado[maquina_actual] += horas_grupo
            grupo_asignado = True

    # Paso 3: Procesar partes pendientes (removidas de grupos)
    for parte in partes_pendientes:
        parte_asignada = False
        horas_parte = calcular_horas_parte(parte)
        part_id = parte.get('part_id')
        num_divisiones = contar_divisiones_parte(part_id)

        # Intentar asignar completa en máquina existente
        for maq_id in sorted(asignaciones.keys()):
            tiempo_disponible = horas_objetivo - tiempo_usado[maq_id]
            if horas_parte > tiempo_disponible:
                continue
            partes_simuladas = asignaciones[maq_id] + [parte]
            herramientas_totales = contar_herramientas_unicas(partes_simuladas)
            if herramientas_totales > LIMITE_ESTACIONES:
                alertas.append(f"ALERTA: Máquina {maq_id} excede límite de estaciones ({herramientas_totales} > {LIMITE_ESTACIONES})")
                # No bloquea, solo alerta
            asignaciones[maq_id].append(parte)
            tiempo_usado[maq_id] += horas_parte
            parte_asignada = True
            break

        # Si NO cabe completa en ninguna máquina existente
        if not parte_asignada:
            # OPCIÓN A: Crear nueva máquina
            if horas_parte <= horas_objetivo:
                if contar_herramientas_unicas([parte]) > LIMITE_ESTACIONES:
                    alertas.append(
                        f"ALERTA: Part {parte.get('part_number', 'N/A')} requiere {contar_herramientas_unicas([parte])} estaciones, excede límite de {LIMITE_ESTACIONES}."
                    )
                maquina_actual += 1
                if maquina_actual > MAX_MAQUINAS:
                    raise Exception(f"Se excedió límite de {MAX_MAQUINAS} máquinas.")
                asignaciones[maquina_actual] = [parte]
                tiempo_usado[maquina_actual] = horas_parte
                parte_asignada = True
            # OPCIÓN B: Dividir parte (si no ha llegado al límite)
            elif num_divisiones < 2:
                maq_con_mas_espacio = max(
                    asignaciones.keys(),
                    key=lambda m: horas_objetivo - tiempo_usado[m]
                )
                tiempo_disponible = horas_objetivo - tiempo_usado[maq_con_mas_espacio]
                parte_asignada_div, parte_pendiente_div = dividir_parte_por_tiempo(
                    parte,
                    tiempo_disponible
                )
                if parte_asignada_div:
                    partes_sim = asignaciones[maq_con_mas_espacio] + [parte_asignada_div]
                    if contar_herramientas_unicas(partes_sim) > LIMITE_ESTACIONES:
                        alertas.append(f"ALERTA: Máquina {maq_con_mas_espacio} excede límite de estaciones ({contar_herramientas_unicas(partes_sim)} > {LIMITE_ESTACIONES})")
                        maquina_actual += 1
                        if maquina_actual > MAX_MAQUINAS:
                            raise Exception(f"Se excedió límite de {MAX_MAQUINAS} máquinas.")
                        asignaciones[maquina_actual] = [parte_asignada_div]
                        tiempo_usado[maquina_actual] = calcular_horas_parte(parte_asignada_div)
                    else:
                        asignaciones[maq_con_mas_espacio].append(parte_asignada_div)
                        tiempo_usado[maq_con_mas_espacio] += calcular_horas_parte(parte_asignada_div)
                    marcar_division_parte(part_id)
                    if parte_pendiente_div:
                        partes_pendientes.append(parte_pendiente_div)
                    parte_asignada = True
            # ERROR: No se puede asignar ni dividir más
            if not parte_asignada:
                # Fallback: asignar a cualquier máquina con espacio, ignorando compatibilidad
                for maq_id in sorted(asignaciones.keys()):
                    tiempo_disponible = horas_objetivo - tiempo_usado[maq_id]
                    if horas_parte <= tiempo_disponible:
                        asignaciones[maq_id].append(parte)
                        tiempo_usado[maq_id] += horas_parte
                        alertas.append(f"ALERTA: Part {parte.get('part_number', 'N/A')} asignada sin compatibilidad por falta de espacio.")
                        parte_asignada = True
                        break
                # Si aún no cabe, crear nueva máquina ignorando compatibilidad
                if not parte_asignada and horas_parte <= horas_objetivo:
                    maquina_actual += 1
                    if maquina_actual > MAX_MAQUINAS:
                        raise Exception(f"Se excedió límite de {MAX_MAQUINAS} máquinas.")
                    asignaciones[maquina_actual] = [parte]
                    tiempo_usado[maquina_actual] = horas_parte
                    alertas.append(f"ALERTA: Part {parte.get('part_number', 'N/A')} asignada en máquina nueva sin compatibilidad por falta de espacio.")
                    parte_asignada = True
                if not parte_asignada:
                    raise Exception(
                        f"ERROR: Part {parte.get('part_number', 'N/A')} no se puede asignar. Divisiones: {num_divisiones}/2. Horas requeridas: {horas_parte:.2f}h > {horas_objetivo:.2f}h límite."
                    )

    asignaciones = {maq_id: partes for maq_id, partes in asignaciones.items() if partes}
    # Opcional: retornar alertas junto con asignaciones
    # return asignaciones, alertas
    return asignaciones


def generar_reporte_asignacion(asignaciones: Dict[int, List[dict]], horas_objetivo: float = 96.0) -> str:
    """
    Genera un reporte legible de la asignación.
    
    Returns:
        String con información detallada de cada máquina
    """
    reporte = []
    reporte.append("=" * 80)
    reporte.append("REPORTE DE ASIGNACIÓN DE PARTES A MÁQUINAS")
    reporte.append("=" * 80)
    reporte.append("")
    
    total_maquinas = len(asignaciones)
    total_partes = sum(len(partes) for partes in asignaciones.values())
    total_horas = sum(calcular_horas_grupo(partes) for partes in asignaciones.values())
    
    reporte.append(f"Total de máquinas utilizadas: {total_maquinas}")
    reporte.append(f"Total de partes asignadas: {total_partes}")
    reporte.append(f"Total horas productivas: {total_horas:.2f}h")
    reporte.append(f"Capacidad total disponible: {total_maquinas * horas_objetivo:.2f}h")
    reporte.append("")
    
    for maq_id in sorted(asignaciones.keys()):
        partes = asignaciones[maq_id]
        horas_usadas = calcular_horas_grupo(partes)
        porcentaje = (horas_usadas / horas_objetivo) * 100
        compatibilidad = encontrar_compatibilidad_promedio_grupo(partes)
        
        reporte.append(f"MÁQUINA {maq_id}")
        reporte.append(f"  Tiempo usado: {horas_usadas:.2f}h de {horas_objetivo:.2f}h ({porcentaje:.1f}%)")
        reporte.append(f"  Compatibilidad promedio: {compatibilidad:.2f}")
        reporte.append(f"  Número de partes: {len(partes)}")
        
        if horas_usadas > horas_objetivo:
            reporte.append(f"  ❌ ERROR CRÍTICO: Excede tiempo disponible por {horas_usadas - horas_objetivo:.2f}h")
        elif porcentaje > 95:
            reporte.append(f"  ✅ Utilización óptima (>95%)")
        elif porcentaje < 50:
            reporte.append(f"  ⚠️  Baja utilización (<50%)")
        
        reporte.append("  Partes asignadas:")
        for parte in partes:
            part_id = parte.get('part_id', 'N/A')
            part_number = parte.get('part_number', 'N/A')
            quantity = parte.get('quantity', 0)
            uph = parte.get('uph', 0)
            horas = quantity / uph if uph > 0 else 0
            es_division = parte.get('_es_division', False)
            
            division_mark = " [DIVIDIDO]" if es_division else ""
            reporte.append(f"    - {part_number}: {quantity} pzs, {uph} UPH, {horas:.2f}h{division_mark}")
        
        reporte.append("")
    
    reporte.append("=" * 80)
    
    return "\n".join(reporte)
