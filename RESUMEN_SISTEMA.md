# CLASIFICADOR-STD: Sistema Experto de Distribución de Partes en Máquinas Punch Press

## CONTEXTO DEL NEGOCIO
Sistema de manufactura para Flex que distribuye automáticamente partes de metal (parts) en máquinas punch press. El objetivo es programar máquinas de forma óptima respetando límites físicos de capacidad (estaciones de herramientas) y tiempo de producción.

## PROBLEMA QUE RESUELVE
Antes: Los ingenieros asignaban parts manualmente, causando:
- Máquinas sobrecargadas (>52 herramientas)
- Tiempo excedido (>96 horas de producción)
- Máquinas desbalanceadas (unas llenas, otras vacías)
- Process lento y propenso a errores humanos

Ahora: El sistema automáticamente distribuye parts cumpliendo REGLAS DURAS sin excepción.

## REGLAS DURAS DEL SISTEMA (NO NEGOCIABLES)
1. **Tiempo ≤ horas_objetivo** (default 96h): NUNCA exceder tiempo disponible por máquina
2. **Overflow = 0**: Máximo 52 estaciones de herramientas por máquina (tipo 4I)
3. **División de parts**: Máximo 2 divisiones por part (puede estar en máximo 2 máquinas)
4. **Redondos flexibles**: Tool numbers que inician con "1" (ej: 10120) pueden ir en estaciones con o sin guía

## ARQUITECTURA DEL SISTEMA

### BACKEND (FastAPI + Python)
**Ubicación:** `backend/`
**Puerto:** 8000
**Base de datos:** SQLite (`clasificador.db`)

**Archivos clave:**
- `app/main.py`: Punto de entrada FastAPI
- `app/utils/algoritmo_asignacion.py`: **CORE DEL SISTEMA** - Algoritmo de distribución con reglas duras
- `app/services/distribucion_service.py`: Lógica de negocio para crear distribuciones
- `app/services/excel_service.py`: Genera archivos Excel por máquina (estilos para programación)
- `app/routers/distribucion_router.py`: API endpoints (`/distribucion/crear`, `/distribucion/listar`, etc.)
- `app/database/db.py`: Configuración SQLAlchemy
- `test_algoritmo.py`: Script de prueba del algoritmo

**Modelos principales:**
- `Package`: Conjunto de parts (ej: "Package STD 360x")
- `PackagePart`: Part individual con cantidad, UPH, grosor, herramientas
- `Machine`: Máquina física con tipo (4I, 2I, 45STA)
- `MachineTemplate`: Plantilla con estaciones y configuración
- `Distribucion`: Resultado de una distribución (metadata)
- `DistribucionStorage`: Almacena JSON completo de la distribución

### FRONTEND (Vue 3 + Vite)
**Ubicación:** `frontend/`
**Puerto:** 5173
**Framework:** Vue 3 + Pinia + Vue Router

**Vistas principales:**
- `CreateDistribucionView.vue`: Formulario para crear distribución
  - Selector de package
  - Parámetros: demanda, horas objetivo
  - Selector visual de máquinas (tarjetas clickeables)
- `DistribucionDetailView.vue`: Dashboard de resultados
  - Stats cards: máquinas usadas, total parts, horas totales, % utilización
  - Barras de progreso por máquina (color-coded: verde/amarillo/naranja/rojo)
  - Lista de parts por máquina
  - Preview de estilo (herramientas asignadas)
  - Botones de descarga Excel

**Componentes:**
- `NavBar.vue`: Navegación
- `Alert.vue`: Notificaciones
- `Card.vue`, `LoadingSpinner.vue`: UI reutilizables

**Servicios:**
- `services/api.js`: Cliente axios con proxy `/api` → `http://localhost:8000`
- `stores/classifier.js`: Estado global Pinia

## FLUJO COMPLETO DEL SISTEMA

### 1. PREPARACIÓN DE DATOS (Manual previo)
- Subir package con sus parts
- Parsear archivos de setup (extraer tool numbers, UPH, thickness, sheet_size)
- Almacenar en base de datos

### 2. CREAR DISTRIBUCIÓN (Usuario)
**Frontend → Backend:**
```
Usuario en CreateDistribucionView:
1. Selecciona package (ej: "STD 360x 12 Maquinas.xlsx")
2. Ingresa demanda (ej: 100 unidades)
3. Define horas_objetivo (default: 96h)
4. Selecciona máquinas disponibles (multi-select con checkboxes)
5. Click "Crear Distribución"

POST /api/distribucion/crear
Body: {
  package_id: 1,
  demanda: 100,
  horas_objetivo: 96,
  machine_ids: [1, 2, 3, 4]
}
```

### 3. ALGORITMO DE ASIGNACIÓN (Core del backend)
**Archivo:** `backend/app/utils/algoritmo_asignacion.py`

**Estrategia (paso a paso):**

**FASE 1: Agrupar por compatibilidad**
```
- Calcula score entre partes (0-100):
  * Mismo grosor (thickness): +30
  * Mismo tamaño lámina (sheet_size): +30
  * Herramientas en común: +40
- Ordena parts por UPH ascendente (lentos primero)
- Agrupa parts con score ≥70 
- VALIDACIÓN: Herramientas únicas del grupo ≤52 (regla dura)
```

**FASE 2: Asignar grupos a máquinas**
```
Para cada grupo:
  1. Calcular horas necesarias = Σ(cantidad / uph)
  
  2. VALIDACIÓN TIEMPO (Regla Dura):
     Si horas_grupo > tiempo_disponible:
       - Ajustar: remover part menos compatible
       - Repetir hasta que quepa
  
  3. VALIDACIÓN OVERFLOW (Regla Dura):
     Si herramientas_únicas > 52:
       - Si máquina vacía: remover part menos compatible
       - Si máquina con parts: crear nueva máquina
  
  4. ASIGNAR grupo a máquina actual
  
  5. Si máquina llena (>90%): crear nueva máquina
```

**FASE 3: Procesar parts pendientes**
```
Parts que no cupieron en grupos:
  Para cada part:
    1. Intentar asignar completo a máquina existente
    2. Validar tiempo y overflow
    3. Si no cabe:
       - OPCIÓN A: Crear nueva máquina
       - OPCIÓN B: Dividir por cantidad (si <2 divisiones)
         * cantidad_que_cabe = tiempo_disponible * uph
         * parte_asignada (cantidad parcial)
         * parte_pendiente (resto)
       - Marcar división global
    4. Si no se puede: ERROR con mensaje claro
```

**FASE 4: Minimizar máquinas (Optimización)**
```
- Identificar máquinas con baja carga
- Intentar consolidar parts en menos máquinas
- Respetar reglas duras al consolidar
- Eliminar máquinas vacías
```

**Output:**
```python
{
  1: [parte1, parte2, parte3],  # Máquina 1
  2: [parte4, parte5],          # Máquina 2
  3: [parte6, parte7, parte8]   # Máquina 3
}
```

### 4. GENERAR RESULTADO (Backend)
```
distribucion_service.py:
1. Ejecuta algoritmo de asignación
2. Valida resultado (tiempo, overflow, divisiones)
3. Crea registro Distribucion en DB
4. Almacena JSON completo en DistribucionStorage
5. Para cada máquina:
   - Genera estilo (lista de herramientas únicas)
   - Aplica redondos flexibles (sin guía si es posible)
   - Crea archivo Excel listo para técnico
6. Retorna JSON con metadata + asignaciones
```

### 5. VISUALIZAR RESULTADOS (Frontend)
```
Frontend recibe respuesta → Navega a DistribucionDetailView
Dashboard muestra:
- Header: nombre, fecha, status
- Stats: 
  * Total máquinas usadas
  * Total parts asignados
  * Horas productivas totales
  * % utilización promedio
- Por cada máquina:
  * Nombre y tipo
  * Barra progreso (horas usadas / disponibles)
  * Lista de parts asignados
  * Herramientas únicas del estilo
  * ⚠️ Alertas si overflow o exceso tiempo
  * Botón descarga Excel individual
- Botón descarga batch (todos los estilos en ZIP)
```

### 6. DESCARGA DE ESTILOS (Para técnicos)
```
GET /api/distribucion/{id}/descargar-estilo/{maquina_id}
Retorna: archivo Excel con formato específico:
- Header: "ESTILO MÁQUINA: {nombre}"
- Metadata: tipo, package, demanda, tiempos
- Lista parts asignados (part number, cantidad, horas)
- TABLA DE CONFIGURACIÓN:
  * Estación | Tipo | Tool Number | Ángulo | Tiene Guía | Autoindex | Parts que usan
  * Ordenado por estación (1-52)
  * Redondos optimizados (sin guía donde sea posible)
- Sección especial: Herramientas fuera del estilo (si hay overflow)
```

## TIPOS DE MÁQUINAS
```
4I:    52 estaciones (principal)
2I:    20 estaciones (menor capacidad)
45STA:  8 estaciones (muy limitada)
```

## DATOS IMPORTANTES
**Cálculos:**
- Horas por part = cantidad / uph
- Utilización = (horas_usadas / horas_objetivo) * 100
- Compatibilidad = score promedio entre todos los pares de parts

**Límites:**
- MAX_MAQUINAS: 20 (límite de seguridad)
- MAX_INTENTOS división: 3
- MAX_DIVISIONES por part: 2

## COMANDOS PARA EJECUTAR

**Backend:**
```bash
cd backend
py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Prueba algoritmo:**
```bash
cd backend
py test_algoritmo.py
```

## ACCESO DE RED
- Local: `http://localhost:5173`
- Red: `http://10.106.113.32:5173` (requiere firewall configurado)
- Backend proxy automático via Vite

## ESTADO ACTUAL
✅ Backend funcionando con algoritmo completo
✅ Frontend con interfaz profesional
✅ Todo guardado en GitHub (GAMEZLALO2111/CLASIFICADOR-STD_SE)
🔄 Pendiente: Configurar acceso de red para otros usuarios

## ARCHIVOS CRÍTICOS PARA ENTENDER
1. `backend/app/utils/algoritmo_asignacion.py` - CORAZÓN DEL SISTEMA
2. `backend/app/services/distribucion_service.py` - Orquestación
3. `frontend/src/views/CreateDistribucionView.vue` - UI creación
4. `frontend/src/views/DistribucionDetailView.vue` - UI resultados
5. `backend/test_algoritmo.py` - Ejemplo de uso
