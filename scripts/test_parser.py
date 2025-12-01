import re

def parse_stp(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    text = "".join(lines).lower()

    # -----------------------------
    # 1) EXTRAER DRAWING NAME
    # -----------------------------
    pn_match = re.search(r"drawing name\s*:\s*(.+)", text)
    if not pn_match:
        raise ValueError(f"[ERROR] No se encontró DRAWING NAME en {file_path}")

    full_name = pn_match.group(1).strip()
    # cortar todo después de "sw"
    if "sw" in full_name:
        part_number = full_name.split("sw")[0].strip().replace("-", "").replace("_", "")
    else:
        raise ValueError(f"[ERROR] No se encontró 'SW' en DRAWING NAME de {file_path}")

    # -----------------------------
    # 2) THICKNESS
    # -----------------------------
    thick_match = re.search(r"thickness\s*:\s*([0-9.]+)", text)
    if not thick_match:
        raise ValueError(f"[ERROR] No se encontró THICKNESS en {file_path}")
    thickness = float(thick_match.group(1))

    # -----------------------------
    # 3) SHEET SIZE
    # -----------------------------
    size_match = re.search(r"sheet size\s*:\s*([0-9.]+)\s*x\s*([0-9.]+)", text)
    if not size_match:
        raise ValueError(f"[ERROR] No se encontró SHEET SIZE en {file_path}")
    x = float(size_match.group(1))
    y = float(size_match.group(2))
    sheet_x, sheet_y = max(x, y), min(x, y)

    # -----------------------------
    # 4) EXTRAER ESTACIONES Y TOOL NO.
    # -----------------------------
    herramientas = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2:
            est = parts[0]

            # solo estaciones de 3 dígitos, ignorar la S
            if est[:3].isdigit():
                estacion = int(est[:3])  

                # tool number es el último valor numérico de la línea
                tool_no_match = re.findall(r"[0-9.]+", line)
                if tool_no_match:
                    tool_no = tool_no_match[-1]
                    herramientas.append({"estacion": estacion, "tool_no": tool_no})

    if not herramientas:
        raise ValueError(f"[ERROR] No se encontraron herramientas en {file_path}")

    # -----------------------------
    # 5) SYM
    # -----------------------------
    sym_match = re.search(r"sym\s*=\s*([0-9]+)", text)
    if not sym_match:
        raise ValueError(f"[ERROR] No se encontró SYM en {file_path}")
    sym = int(sym_match.group(1))

    # -----------------------------
    # 6) RUNTIME (mins)
    # -----------------------------
    rt_match = re.search(r"([0-9.]+)\s*mins", text)
    if not rt_match:
        raise ValueError(f"[ERROR] No se encontró RUN TIME mins en {file_path}")
    runtime = float(rt_match.group(1)) + 6  # agregar colchón

    # -----------------------------
    # 7) UPH
    # -----------------------------
    uph = round((sym * 60) / runtime, 2)

    return {
        "part_number": part_number,
        "thickness": thickness,
        "sheet_x": sheet_x,
        "sheet_y": sheet_y,
        "herramientas": herramientas,
        "sym": sym,
        "runtime": runtime,
        "uph": uph
    }


# --------------------------------------
# EJECUCIÓN DE PRUEBA
# --------------------------------------
if __name__ == "__main__":
    path = input("Pon la ruta completa de un archivo .stp: ")
    data = parse_stp(path)
    print("\n\n===== RESULTADO DEL PARSER =====")
    for k, v in data.items():
        print(f"{k}: {v}")
