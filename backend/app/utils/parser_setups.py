import re
from typing import List, Optional
import os

def extraer_part_number(nombre_archivo: str) -> dict:
    """
    Extrae:
      PREFIX (TYEH, ETYEH, etc)
      NUMBER (1153532)
      VERSION (02)
      NIVEL (solo SW permitido)
    Ejemplo válido:
      TYEH-1153532_02-SW
      ETYEH-1153532_03-SW
    """
    patron = r"^([A-Z0-9]+)-(\d+)_(\d+)-(SW)"
    match = re.match(patron, nombre_archivo)

    if not match:
        return {
            "full": None,
            "prefix": None,
            "number": None,
            "version": None,
            "nivel": None
        }

    prefix = match.group(1)
    number = match.group(2)
    version = match.group(3)
    nivel = match.group(4)

    full = f"{prefix}-{number}_{version}-{nivel}"

    return {
        "full": full,
        "prefix": prefix,
        "number": number,
        "version": version,
        "nivel": nivel
    }


def parse_setup(file_path: str):
    # =========================================================
    #   1) NOMBRE (part number)
    # =========================================================
    nombre_archivo = os.path.basename(file_path).replace(".stp", "")

    # limpiar prefijos de upload
    for rm in ["temp_", "file-"]:
        if nombre_archivo.startswith(rm):
            nombre_archivo = nombre_archivo[len(rm):]

    part_info = extraer_part_number(nombre_archivo)

    # VALIDAR NIVEL SW
    if part_info["nivel"] != "SW":
        raise ValueError("Solo se aceptan setups de nivel SW.")

    # =========================================================
    #   2) LEER CONTENIDO DEL ARCHIVO
    # =========================================================
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # =========================================================
    #   3) THICKNESS
    # =========================================================
    thick_match = re.search(r"THICKNESS\s*:\s*([0-9.]+)", content)
    thickness = float(thick_match.group(1)) if thick_match else None

    # =========================================================
    #   4) SHEET SIZE
    # =========================================================
    sheet_match = re.search(r"SHEET SIZE\s*:\s*([0-9]+)\s*x\s*([0-9]+)", content, re.I)
    if sheet_match:
        s1, s2 = int(sheet_match.group(1)), int(sheet_match.group(2))
        sheet_size = sorted([s1, s2], reverse=True)
    else:
        sheet_size = None

    # =========================================================
    #   5) STATIONS, TOOL NUMBERS & ANGLES
    # =========================================================
    stations = []
    tool_numbers = []
    angles = []
    tools_data = []  # Lista de dicts con info completa

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue

        # ignorar encabezados
        if "TOOL" in line.upper() and "TYPE" in line.upper():
            continue

        # Buscar patrón: estación, tool number y ángulo
        # Formato: "201 RECTANGULAR ... 90.000 ... 31750.156"
        parts = line.split()
        if len(parts) < 2:
            continue
        
        # Primera columna debe ser estación (3 dígitos)
        if not re.match(r'^\d{3}[a-zA-Z]?$', parts[0]):
            continue
        
        station = re.match(r'^(\d{3})', parts[0]).group(1)
        
        # Buscar tool number (formato XXXXX.X o XXXXX)
        tool_num = None
        angle = None
        
        for i, part in enumerate(parts):
            # Tool number: 4-6 dígitos con posible decimal
            if re.match(r'^\d{4,6}(\.\d+)?$', part):
                tool_num = part
                
                # Buscar ángulo antes del tool number
                # Los ángulos suelen estar 1-3 posiciones antes
                for j in range(max(0, i-5), i):
                    if re.match(r'^\d+\.0+$', parts[j]):
                        potential_angle = float(parts[j])
                        if potential_angle in [0.0, 90.0, 180.0, 270.0, 45.0]:
                            angle = potential_angle
                            break
                break
        
        # Validar y agregar
        if tool_num and float(tool_num.split('.')[0]) >= 1000:
            stations.append(station)
            tool_numbers.append(tool_num)
            angles.append(angle if angle is not None else 0.0)  # Default 0° si no se encuentra
            
            tools_data.append({
                "station": station,
                "tool_number": tool_num,
                "angle": angle if angle is not None else 0.0
            })

    # eliminar duplicados manteniendo orden
    seen = set()
    unique_stations = []
    unique_tool_numbers = []
    unique_angles = []
    unique_tools_data = []
    
    for i, (st, tn) in enumerate(zip(stations, tool_numbers)):
        key = f"{st}_{tn}"
        if key not in seen:
            seen.add(key)
            unique_stations.append(st)
            unique_tool_numbers.append(tn)
            unique_angles.append(angles[i])
            unique_tools_data.append(tools_data[i])
    
    stations = unique_stations
    tool_numbers = unique_tool_numbers
    angles = unique_angles
    tools_data = unique_tools_data

    # =========================================================
    #   6) SYM  (Piezas por blank, NO es booleano)
    # =========================================================
    sym_match = re.search(r"sym\s*=\s*([0-9]+)", content, re.I)
    sym = int(sym_match.group(1)) if sym_match else None

    # =========================================================
    #   7) RUN TIME (mins)
    # =========================================================
    run_match = re.search(r"=\s*([0-9.]+)\s*mins", content, re.I)
    run_time = float(run_match.group(1)) if run_match else None

    # =========================================================
    #   8) UPH  (según tu fórmula oficial)
    # =========================================================
    if sym is not None and run_time is not None:
        total_time = run_time + 6
        uph = round((sym * 60) / total_time, 2)
    else:
        uph = None

    # =========================================================
    #   9) RESPUESTA FINAL
    # =========================================================
    return {
        "part_number": part_info,
        "thickness": thickness,
        "sheet_size": sheet_size,
        "stations": stations,
        "tool_numbers": tool_numbers,
        "angles": angles,
        "tools_data": tools_data,  # Info completa con estación, TN y ángulo
        "sym": sym,
        "run_time_mins": run_time,
        "uph": uph
    }
