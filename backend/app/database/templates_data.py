# Configuración de templates de máquinas

TEMPLATE_4I = {
    "tipo_maquina": "4I",
    "estaciones_totales": 58,
    "autoindex_count": 4,
    "estaciones_config": {}
}

TEMPLATE_2I = {
    "tipo_maquina": "2I",
    "estaciones_totales": 58,
    "autoindex_count": 2,
    "estaciones_config": {}
}

TEMPLATE_45STA = {
    "tipo_maquina": "45STA",
    "estaciones_totales": 45,
    "autoindex_count": 4,
    "estaciones_config": {}
}

# ============== 4-INDEX ==============

# Tipo A (24 estaciones)
tipo_a_4i = [103, 204, 305, 112, 213, 314, 117, 218, 319, 126, 227, 328, 132, 233, 334, 141, 242, 343, 146, 247, 348, 155, 256, 357]
# Estaciones tipo A SIN GUÍA (dato crítico para asignación)
sin_guia_a_4i = [202, 213, 218, 227, 233, 242, 247, 258]

for est in tipo_a_4i:
    TEMPLATE_4I["estaciones_config"][str(est)] = {
        "tipo": "A",
        "es_autoindex": False,
        "tiene_guia": est not in sin_guia_a_4i
    }

# Tipo B (20 estaciones) - TODAS SIN GUÍA
tipo_b_4i = [201, 106, 307, 108, 309, 110, 311, 120, 321, 122, 323, 124, 325, 230, 135, 336, 137, 338, 139, 340, 149, 350, 151, 352, 153, 354]
autoindex_b_4i = [201, 230]

for est in tipo_b_4i:
    TEMPLATE_4I["estaciones_config"][str(est)] = {
        "tipo": "B",
        "es_autoindex": est in autoindex_b_4i,
        "tiene_guia": False  # TODAS tipo B sin guía
    }

# Tipo C (4 estaciones) - TODAS CON GUÍA
tipo_c_4i = [202, 216, 231, 245]

for est in tipo_c_4i:
    TEMPLATE_4I["estaciones_config"][str(est)] = {
        "tipo": "C",
        "es_autoindex": False,
        "tiene_guia": True
    }

# Tipo D (2 estaciones) - TODAS CON GUÍA
tipo_d_4i = [229, 258]

for est in tipo_d_4i:
    TEMPLATE_4I["estaciones_config"][str(est)] = {
        "tipo": "D",
        "es_autoindex": False,
        "tiene_guia": True
    }

# Tipo E (2 estaciones) - TODAS CON GUÍA
tipo_e_4i = [115, 144]
autoindex_e_4i = [115, 144]

for est in tipo_e_4i:
    TEMPLATE_4I["estaciones_config"][str(est)] = {
        "tipo": "E",
        "es_autoindex": True,  # AMBAS son autoindex
        "tiene_guia": True
    }

# ============== 2-INDEX ==============

# Tipo A (28 estaciones)
tipo_a_2i = [102, 203, 304, 107, 208, 309, 111, 212, 313, 116, 217, 318, 129, 230, 331, 134, 235, 336, 138, 239, 143, 244, 345, 147, 248, 349, 152, 253, 354, 165, 266, 367, 170, 271, 372]
sin_guia_a_2i = [102, 203, 107, 208, 111, 212, 116, 217, 129, 230, 134, 138, 239, 143, 244, 147, 248, 152, 253, 170]

for est in tipo_a_2i:
    TEMPLATE_2I["estaciones_config"][str(est)] = {
        "tipo": "A",
        "es_autoindex": False,
        "tiene_guia": est not in sin_guia_a_2i
    }

# Tipo B (12 estaciones) - TODAS SIN GUÍA
tipo_b_2i = [105, 306, 114, 315, 220, 132, 333, 141, 342, 150, 351, 168, 369]
autoindex_b_2i = [220, 256]

for est in tipo_b_2i:
    TEMPLATE_2I["estaciones_config"][str(est)] = {
        "tipo": "B",
        "es_autoindex": est in autoindex_b_2i,
        "tiene_guia": False
    }

# Tipo C (4 estaciones) - TODAS CON GUÍA
tipo_c_2i = [210, 228, 246, 264]

for est in tipo_c_2i:
    TEMPLATE_2I["estaciones_config"][str(est)] = {
        "tipo": "C",
        "es_autoindex": False,
        "tiene_guia": True
    }

# Tipo D (2 estaciones) - TODAS CON GUÍA
tipo_d_2i = [219, 255]

for est in tipo_d_2i:
    TEMPLATE_2I["estaciones_config"][str(est)] = {
        "tipo": "D",
        "es_autoindex": False,
        "tiene_guia": True
    }

# Tipo E (2 estaciones) - TODAS CON GUÍA
tipo_e_2i = [201, 237]

for est in tipo_e_2i:
    TEMPLATE_2I["estaciones_config"][str(est)] = {
        "tipo": "E",
        "es_autoindex": False,
        "tiene_guia": True
    }

# ============== 45-ESTACIONES ==============

# Tipo A (22 estaciones)
tipo_a_45 = [107, 208, 309, 112, 213, 314, 116, 217, 318, 121, 222, 323, 128, 229, 330, 133, 234, 335, 137, 238, 339, 142, 243, 344]
sin_guia_a_45 = [208, 213, 217, 222, 229, 234, 238, 243]

for est in tipo_a_45:
    TEMPLATE_45STA["estaciones_config"][str(est)] = {
        "tipo": "A",
        "es_autoindex": False,
        "tiene_guia": est not in sin_guia_a_45
    }

# Tipo B (12 estaciones) - TODAS SIN GUÍA
tipo_b_45 = [102, 303, 104, 305, 110, 311, 119, 320, 131, 332, 141, 341]
autoindex_b_45 = [215, 236]

for est in tipo_b_45:
    TEMPLATE_45STA["estaciones_config"][str(est)] = {
        "tipo": "B",
        "es_autoindex": est in autoindex_b_45,
        "tiene_guia": False
    }

# Tipo C (6 estaciones) - TODAS CON GUÍA
tipo_c_45 = [201, 206, 225, 226, 236]
autoindex_c_45 = [201, 225, 236]

for est in tipo_c_45:
    TEMPLATE_45STA["estaciones_config"][str(est)] = {
        "tipo": "C",
        "es_autoindex": est in autoindex_c_45,
        "tiene_guia": True
    }

# Tipo D (1 estación) - CON GUÍA
tipo_d_45 = [227]

for est in tipo_d_45:
    TEMPLATE_45STA["estaciones_config"][str(est)] = {
        "tipo": "D",
        "es_autoindex": False,
        "tiene_guia": True
    }

# Tipo E (2 estaciones) - TODAS CON GUÍA
tipo_e_45 = [224, 245]

for est in tipo_e_45:
    TEMPLATE_45STA["estaciones_config"][str(est)] = {
        "tipo": "E",
        "es_autoindex": False,
        "tiene_guia": True
    }

# Lista de templates para inicialización
TEMPLATES = [TEMPLATE_4I, TEMPLATE_2I, TEMPLATE_45STA]