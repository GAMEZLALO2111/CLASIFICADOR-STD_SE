# 📋 API DE ESTILOS - Documentación

## Sistema Completo de Gestión de Estilos

El sistema permite trabajar con estilos de dos formas:
1. **Desde Distribución Automática**: Descargar el estilo de una máquina después de calcular una distribución
2. **Estilo Manual**: Crear configuraciones personalizadas sin distribución automática

---

## 🔄 OPCIÓN 1: Estilos desde Distribución Automática

### Flujo de trabajo:
1. Usuario crea distribución con `POST /distribucion/crear`
2. Ve resultados en pantalla (JSON)
3. Descarga estilo de una máquina específica

### Endpoint: Descargar Estilo de Máquina

```http
GET /distribucion/{distribucion_id}/maquina/{machine_id}/estilo-excel
```

**Parámetros:**
- `distribucion_id`: ID de la distribución guardada
- `machine_id`: ID de la máquina (1, 2, 3, etc.)

**Response:**
- Archivo Excel descargable con el estilo de la máquina

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/distribucion/1/maquina/1/estilo-excel" \
  --output estilo_T-101.xlsx
```

**Contenido del Excel:**
- Hoja única optimizada para el técnico
- Información general (máquina, package, demanda, tiempos)
- Parts asignados a esa máquina
- Tabla completa de estaciones con:
  - Estación, Tipo, Tool Number, Ángulo, Tiene Guía, Autoindex
  - Parts que usan cada estación
- Herramientas fuera de estilo (si hay)

---

## ✏️ OPCIÓN 2: Estilos Manuales

### Flujo de trabajo:
1. Usuario sube archivos .stp de los parts que quiere procesar
2. Selecciona la máquina donde se aplicará el estilo
3. Sistema parsea automáticamente los setups y calcula el estilo unificado
4. Sistema guarda el estilo (expira en 30 días)
5. Usuario puede descargarlo en Excel cuando lo necesite

### 1. Crear Estilo Manual desde Archivos

```http
POST /estilo/crear-desde-archivos
```

**Content-Type:** `multipart/form-data`

**Form Parameters:**
- `nombre` (string, requerido): Nombre descriptivo del estilo
- `machine_id` (int, requerido): ID de la máquina (1, 2, 3, etc.)
- `archivos` (file[], requerido): Uno o más archivos .stp
- `notas` (string, opcional): Notas adicionales

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/estilo/crear-desde-archivos" \
  -F "nombre=Estilo Personalizado T-101" \
  -F "machine_id=1" \
  -F "archivos=@TYEH-1171208_01-SW.stp" \
  -F "archivos=@TYEH-1171206_01-SW.stp" \
  -F "notas=Configuración especial para producción nocturna"
```

**Ejemplo con JavaScript:**
```javascript
const formData = new FormData();
formData.append('nombre', 'Estilo Personalizado T-101');
formData.append('machine_id', 1);
formData.append('notas', 'Configuración especial');

// Agregar múltiples archivos
files.forEach(file => {
  formData.append('archivos', file);
});

const response = await fetch('http://localhost:8000/estilo/crear-desde-archivos', {
  method: 'POST',
  body: formData
});
```

**Response:**
```json
{
  "id": 1,
  "nombre": "Estilo Personalizado T-101",
  "machine_id": 1,
  "machine_nombre": "T-101",
  "tipo_maquina": "4I",
  "part_numbers": ["TYEH-1171208_01-SW", "TYEH-1171206_01-SW"],
  "estilo_json": [...],
  "notas": "Configuración especial para producción nocturna",
  "created_at": "2025-12-04T10:30:00",
  "expires_at": "2026-01-03T10:30:00",
  "activa": true
}
```

### 2. Listar Estilos Manuales

```http
GET /estilo/listar
```

**Response:**
```json
[
  {
    "id": 1,
    "nombre": "Estilo Personalizado T-101",
    "machine_id": 1,
    "machine_nombre": "T-101",
    "tipo_maquina": "4I",
    "part_numbers": ["TYEH-1171208_01-SW"],
    "created_at": "2025-12-04T10:30:00",
    "expires_at": "2026-01-03T10:30:00",
    "activa": true
  }
]
```

### 3. Obtener Estilo Manual Específico

```http
GET /estilo/{estilo_id}
```

**Ejemplo:**
```bash
GET /estilo/1
```

### 4. Descargar Estilo Manual en Excel

```http
GET /estilo/{estilo_id}/excel
```

**Response:**
- Archivo Excel con la configuración del estilo

**Ejemplo:**
```bash
curl -X GET "http://localhost:8000/estilo/1/excel" \
  --output estilo_manual_T-101.xlsx
```

### 5. Eliminar Estilo Manual

```http
DELETE /estilo/{estilo_id}
```

**Response:**
```json
{
  "message": "Estilo 'Estilo Personalizado T-101' eliminado"
}
```

---

## 📊 Comparación de Opciones

| Característica | Desde Distribución | Manual |
|---------------|-------------------|--------|
| **Cálculo automático** | ✅ Sí | ❌ No |
| **Requiere package** | ✅ Sí | ❌ No |
| **Optimización** | ✅ Automática | ⚙️ Usuario decide |
| **Flexibilidad** | ⚙️ Limitada | ✅ Total |
| **Tiempo de expiración** | 1 día | 30 días |
| **Uso típico** | Producción estándar | Setups especiales |

---

## 🎯 Casos de Uso

### Caso 1: Producción Normal
1. Usar distribución automática
2. Descargar estilo por máquina
3. Técnico programa según el Excel

### Caso 2: Setup Experimental
1. Crear estilo manual
2. Definir herramientas personalizadas
3. Guardar para futuras referencias

### Caso 3: Mantenimiento
1. Crear estilo con herramientas de respaldo
2. Documentar configuración alternativa
3. Usar cuando máquinas principales están ocupadas

---

## 🔧 Frontend - Flujo Recomendado

### Vista de Distribución:
```
┌────────────────────────────────────┐
│ Distribución #1 - Package 1171174  │
│ ✅ Factible - 3 máquinas usadas    │
├────────────────────────────────────┤
│ Máquina T-101                      │
│   📊 Ver Detalles                  │
│   🔧 Descargar Estilo              │ ← Botón individual
├────────────────────────────────────┤
│ Máquina T-102                      │
│   📊 Ver Detalles                  │
│   🔧 Descargar Estilo              │
├────────────────────────────────────┤
│ Máquina T-103                      │
│   📊 Ver Detalles                  │
│   🔧 Descargar Estilo              │
├────────────────────────────────────┤
│ 📥 Descargar Reporte Completo      │ ← Excel con todo
└────────────────────────────────────┘
```

### Vista de Estilos Manuales:
```
┌────────────────────────────────────┐
│ 📋 Mis Estilos                     │
├────────────────────────────────────┤
│ ✏️ Crear Nuevo Estilo              │
│ 📂 Cargar desde Distribución       │
├────────────────────────────────────┤
│ Estilos Guardados:                 │
│                                    │
│ • Estilo T-101 Producción          │
│   Machine: T-101 | Expires: 15 días│
│   🔧 Descargar  📝 Editar  🗑️ Borrar│
│                                    │
│ • Setup Experimental T-102         │
│   Machine: T-102 | Expires: 28 días│
│   🔧 Descargar  📝 Editar  🗑️ Borrar│
└────────────────────────────────────┘
```

---

## ⚡ Ejemplo Completo: JavaScript

```javascript
// === OPCIÓN 1: Descargar estilo desde distribución ===
async function descargarEstiloDistribucion(distribucionId, machineId) {
  const response = await fetch(
    `http://localhost:8000/distribucion/${distribucionId}/maquina/${machineId}/estilo-excel`
  );
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `estilo_maquina_${machineId}.xlsx`;
  a.click();
}

// === OPCIÓN 2: Crear estilo manual ===
async function crearEstiloManual() {
  const estilo = {
    nombre: "Estilo Personalizado",
    machine_id: 1,
    part_numbers: ["PART-001", "PART-002"],
    estaciones: [
      {
        estacion: "201",
        tipo: "B",
        tool_number: "72050.1",
        angulo: 0,
        tiene_guia: false,
        es_autoindex: true,
        parts_que_usan: ["PART-001"]
      }
    ],
    notas: "Configuración especial"
  };
  
  const response = await fetch('http://localhost:8000/estilo/crear', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(estilo)
  });
  
  const result = await response.json();
  console.log('Estilo creado:', result);
}

// === Descargar estilo manual ===
async function descargarEstiloManual(estiloId) {
  const response = await fetch(
    `http://localhost:8000/estilo/${estiloId}/excel`
  );
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `estilo_manual_${estiloId}.xlsx`;
  a.click();
}
```

---

## 📝 Notas Importantes

1. **Expiración**: 
   - Distribuciones: 1 día
   - Estilos manuales: 30 días

2. **Formato Excel**:
   - Optimizado para técnicos de máquina
   - Muestra TODOS los parts que usan cada estación
   - Incluye alertas de herramientas fuera de estilo

3. **Validaciones**:
   - Máquina debe existir en BD
   - Estaciones deben tener formato válido
   - Parts pueden ser cualquier string (no se valida contra BD)

4. **Permisos**: 
   - Todos los endpoints son públicos por ahora
   - Considerar agregar autenticación en producción
