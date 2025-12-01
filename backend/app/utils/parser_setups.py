import re
from typing import List, Optional


def parse_setup(content: str):
    # -------------------------
    # 1) PART NUMBER
    # -------------------------
    part_match = re.search(r"([A-Z0-9\-]+-SW)", content)
    part_number = part_match.group(1).replace("-SW", "") if part_match else None

    # -------------------------
    # 2) THICKNESS
    # -------------------------
    thick_match = re.search(r"THICKNESS\s*:\s*([0-9.]+)", content)
    thickness = float(thick_match.group(1)) if thick_match else None

    # -------------------------
    # 3) SHEET SIZE
    # -------------------------
    sheet_match = re.search(r"SHEET SIZE\s*:\s*([0-9]+)\s*x\s*([0-9]+)", content, re.I)
    if sheet_match:
        s1, s2 = int(sheet_match.group(1)), int(sheet_match.group(2))
        sheet_size = sorted([s1, s2], reverse=True)
    else:
        sheet_size = None

    # -------------------------
    # 4) STATIONS (3 dígitos)
    # -------------------------
    stations = re.findall(r"\n\s*([0-9]{3})\b", content)
    stations = list(sorted(set(stations)))

    # -------------------------
    # 5) TOOL NUMBERS
    # -------------------------
    tool_numbers = re.findall(r"\b([0-9]{4,6})\b", content)
    tool_numbers = list(sorted(set(tool_numbers)))

    # -------------------------
    # 6) SYM
    # -------------------------
    sym_match = re.search(r"sym\s*=\s*([0-9]+)", content, re.I)
    sym = int(sym_match.group(1)) if sym_match else None

    # -------------------------
    # 7) RUN TIME MINS
    # -------------------------
    run_match = re.search(r"=\s*([0-9.]+)\s*mins", content, re.I)
    run_time = float(run_match.group(1)) if run_match else None

    # -------------------------
    # 8) UPH
    # -------------------------
    if sym and run_time:
        total_time = run_time + 6  # sumarle siempre 6 minutos
        uph = round((sym * 60) / total_time, 2)
    else:
        uph = None

    return {
        "part_number": part_number,
        "thickness": thickness,
        "sheet_size": sheet_size,
        "stations": stations,
        "tool_numbers": tool_numbers,
        "sym": sym,
        "run_time_mins": run_time,
        "uph": uph
    }
