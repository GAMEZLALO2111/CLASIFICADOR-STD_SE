import os
import re


def parse_stp(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    text = "".join(lines).lower()

    # -----------------------------
    # 1) DRAWING NAME -> PART NUMBER
    # -----------------------------
    pn_match = re.search(r"drawing name\s*:\s*(.+)", text)
    if not pn_match:
        raise ValueError(f"[ERROR] No DRAWING NAME en {file_path}")

    full_name = pn_match.group(1).strip()

    if "sw" not in full_name:
        raise ValueError(f"[ERROR] No 'SW' en DRAWING NAME de {file_path}")

    part_number = full_name.split("sw")[0].strip()
    part_number = part_number.replace("-", "").replace("_", "")

    # -----------------------------
    # 2) THICKNESS
    # -----------------------------
    thick_match = re.search(r"thickness\s*:\s*([0-9.]+)", text)
    if not thick_match:
        raise ValueError(f"[ERROR] No THICKNESS en {file_path}")
    thickness = float(thick_match.group(1))

    # -----------------------------
    # 3) SHEET SIZE
    # -----------------------------
    size_match = re.search(r"sheet size\s*:\s*([0-9.]+)\s*x\s*([0-9.]+)", text)
    if not size_match:
        raise ValueError(f"[ERROR] No SHEET SIZE en {file_path}")
    x = float(size_match.group(1))
    y = float(size_match.group(2))
    sheet_x, sheet_y = max(x, y), min(x, y)

    # -----------------------------
    # 4) ESTACIONES + TN (sin duplicados)
    # -----------------------------
    estaciones = []
    tool_numbers = set()

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 2:
            continue

        est_raw = parts[0]

        # siempre 3 dígitos, ignorar 'S'
        if est_raw[:3].isdigit():
            estacion = int(est_raw[:3])
            estaciones.append(estacion)

            # tool number al final
            nums = re.findall(r"[0-9.]+", line)
            if nums:
                tn = nums[-1]
                tool_numbers.add(tn)

    if not estaciones:
        raise ValueError(f"[ERROR] No estaciones detectadas en {file_path}")

    # eliminar duplicados manteniendo orden
    estaciones_unicas = list(dict.fromkeys(estaciones))
    tool_numbers_unicos = list(tool_numbers)

    # -----------------------------
    # 5) SYM
    # -----------------------------
    sym_match = re.search(r"sym\s*=\s*([0-9]+)", text)
    if not sym_match:
        raise ValueError(f"[ERROR] No SYM en {file_path}")
    sym = int(sym_match.group(1))

    # -----------------------------
    # 6) RUN TIME (mins)
    # -----------------------------
    rt_match = re.search(r"([0-9.]+)\s*mins", text)
    if not rt_match:
        raise ValueError(f"[ERROR] No RUN TIME mins en {file_path}")
    runtime = float(rt_match.group(1)) + 6  # +6 colchón

    # -----------------------------
    # 7) UPH
    # -----------------------------
    uph = round((sym * 60) / runtime, 2)

    return {
        "archivo": os.path.basename(file_path),
        "part_number": part_number,
        "thickness": thickness,
        "sheet_x": sheet_x,
        "sheet_y": sheet_y,

        # ESTACIONES
        "estaciones": estaciones_unicas,
        "total_estaciones": len(estaciones_unicas),

        # TOOL NUMBERS
        "tool_numbers": tool_numbers_unicos,
        "total_tool_numbers": len(tool_numbers_unicos),

        # PRODUCCIÓN
        "sym": sym,
        "runtime": runtime,
        "uph": uph
    }


# =====================================
# PROCESAR CARPETA COMPLETA
# =====================================
def parse_folder(folder_path):
    resultados = []
    errores = []

    for file in os.listdir(folder_path):
        if file.lower().endswith((".txt", ".stp")):
            full_path = os.path.join(folder_path, file)
            try:
                data = parse_stp(full_path)
                resultados.append(data)
            except Exception as err:
                errores.append(f"{file}: {err}")

    return resultados, errores


# =====================================
# EJECUCIÓN PRINCIPAL
# =====================================
if __name__ == "__main__":
    folder = input("Pon la ruta de la carpeta con tus .stp: ")

    resultados, errores = parse_folder(folder)

    print("\n===== ARCHIVOS PROCESADOS =====\n")
    for r in resultados:
        print(r)
        print("------------------------------------")

    if errores:
        print("\n===== ERRORES DETECTADOS =====")
        for e in errores:
            print(e)
