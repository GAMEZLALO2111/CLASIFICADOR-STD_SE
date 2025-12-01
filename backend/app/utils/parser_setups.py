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
    #   5) STATIONS & TOOL NUMBERS
    # =========================================================
    stations = []
    tool_numbers = []

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue

        # formato general: "201 ... 74500.2"
        match = re.match(r'^(\d{3})[a-zA-Z]?\s+.+?(\d{4,6}(?:\.\d+)?)\s*$', line)

        if match:
            station = match.group(1)
            tool_num = match.group(2)

            # ignorar encabezados
            if "TOOL" in line.upper() and "TYPE" in line.upper():
                continue

            # validar que el tool number sea razonable
            if float(tool_num.split('.')[0]) >= 1000:
                stations.append(station)
                tool_numbers.append(tool_num)

    # eliminar duplicados manteniendo orden
    stations = list(dict.fromkeys(stations))
    tool_numbers = list(dict.fromkeys(tool_numbers))

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
        "sym": sym,
        "run_time_mins": run_time,
        "uph": uph
    }
