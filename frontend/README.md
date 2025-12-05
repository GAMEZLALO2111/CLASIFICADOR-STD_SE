# Sistema Clasificador STD - Frontend

Aplicación web frontend para el sistema experto de distribución de setups en máquinas CNC.

## 🚀 Características

- **Gestión de Packages**: Crea packages subiendo archivos .stp con configuraciones
- **Distribución Automática**: Asigna parts a máquinas de forma óptima
- **Estilos de Herramientas**: Genera estilos unificados para configuración
- **Descarga de Excel**: Exporta configuraciones listas para los técnicos
- **Acceso en Red**: Disponible para todos los usuarios en la red local

## 🛠️ Tecnologías

- **Vue 3**: Framework JavaScript progresivo
- **Vue Router**: Navegación entre páginas
- **Pinia**: Gestión de estado
- **Axios**: Cliente HTTP para comunicación con el backend
- **Vite**: Herramienta de desarrollo y construcción

## 📋 Requisitos Previos

- Node.js 16+ y npm
- Backend del sistema clasificador en ejecución (puerto 8000)

## 🔧 Instalación

1. Instalar dependencias:
```bash
npm install
```

## 🏃 Ejecución

### Modo Desarrollo
```bash
npm run dev
```
La aplicación estará disponible en:
- Local: `http://localhost:5173`
- Red: `http://<tu-ip>:5173`

### Construcción para Producción
```bash
npm run build
```

### Vista Previa de Producción
```bash
npm run preview
```

## 🌐 Acceso en Red Local

La aplicación está configurada para ser accesible desde cualquier dispositivo en tu red:

1. Inicia el servidor de desarrollo con `npm run dev`
2. Obtén tu dirección IP local:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` o `ip addr`
3. Accede desde otros dispositivos usando: `http://<tu-ip>:5173`

## 📁 Estructura del Proyecto

```
frontend/
├── public/              # Archivos estáticos
├── src/
│   ├── assets/         # Estilos y recursos
│   ├── components/     # Componentes reutilizables
│   │   ├── Alert.vue
│   │   ├── Card.vue
│   │   ├── LoadingSpinner.vue
│   │   └── NavBar.vue
│   ├── views/          # Vistas/Páginas
│   │   ├── HomeView.vue
│   │   ├── ClassifierView.vue
│   │   ├── ResultsView.vue
│   │   └── HistoryView.vue
│   ├── stores/         # Gestión de estado (Pinia)
│   │   └── classifier.js
│   ├── services/       # Servicios API
│   │   └── api.js
│   ├── router/         # Configuración de rutas
│   │   └── index.js
│   ├── App.vue         # Componente raíz
│   └── main.js         # Punto de entrada
├── index.html          # HTML principal
├── package.json        # Dependencias
└── vite.config.js      # Configuración de Vite
```

## 🎨 Componentes Principales

### Vistas
- **HomeView**: Página de inicio con información del sistema
- **PackagesView**: Lista de packages creados
- **CreatePackageView**: Formulario para crear nuevos packages
- **DistribucionesView**: Lista de distribuciones
- **CreateDistribucionView**: Crear nueva distribución
- **DistribucionDetailView**: Detalle de distribución y descarga de estilos
- **EstilosView**: Lista de estilos manuales
- **CreateEstiloView**: Crear estilos manuales desde archivos

### Componentes
- **NavBar**: Barra de navegación principal
- **Card**: Contenedor estilizado
- **Alert**: Alertas y notificaciones
- **LoadingSpinner**: Indicador de carga

## 🔌 API Backend

La aplicación se comunica con el backend (puerto 8000) a través de:

- `POST /api/package/preview`: Vista previa de archivos .stp
- `POST /api/package/confirmar`: Crear package
- `GET /api/package/listar`: Listar packages
- `POST /api/distribucion/crear`: Crear distribución
- `GET /api/distribucion/listar`: Listar distribuciones
- `GET /api/distribucion/{id}/maquina/{machineId}/estilo-excel`: Descargar estilo
- `POST /api/estilo/crear-desde-archivos`: Crear estilo manual
- `GET /api/estilo/listar`: Listar estilos
- `GET /api/estilo/{id}/excel`: Descargar estilo manual

## 🎯 Uso

1. **Crear Package**: Sube archivos .stp y asigna cantidades para cada part
2. **Crear Distribución**: Selecciona package, demanda, horas y máquinas disponibles
3. **Ver Resultados**: Revisa qué parts fueron asignados a cada máquina
4. **Descargar Estilos**: Obtén archivos Excel con configuración de estaciones
5. **Estilos Manuales**: Crea configuraciones personalizadas cuando lo necesites

## 🔒 Seguridad

- Los datos se transmiten a través de conexiones HTTP en la red local
- Para producción, considera implementar HTTPS
- Implementa autenticación si es necesario para tu caso de uso

## 🐛 Solución de Problemas

### La aplicación no carga
- Verifica que el backend esté ejecutándose en el puerto 8000
- Revisa la configuración del proxy en `vite.config.js`

### No se puede acceder desde otros dispositivos
- Asegúrate de que el firewall permita conexiones al puerto 5173
- Verifica que todos los dispositivos estén en la misma red

### Errores de API
- Confirma que el backend esté accesible
- Revisa las URLs en `src/services/api.js`

## 📝 Notas

- El sistema está diseñado para uso en redes locales de trabajo
- Se recomienda realizar pruebas antes del despliegue en producción
- Mantén actualizado Node.js y las dependencias

## 👥 Contribución

Este es un proyecto interno. Para cambios o mejoras, consulta con el equipo de desarrollo.

## 📄 Licencia

Uso interno - Todos los derechos reservados
