import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para manejo de errores
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    const message = error.response?.data?.detail || error.message || 'Error de conexión'
    return Promise.reject({ message })
  }
)

export default {
  // ===== PACKAGES =====
  listarPackages() {
    return apiClient.get('/package/listar')
  },

  obtenerPackage(packageId) {
    return apiClient.get(`/package/${packageId}`)
  },

  previewArchivos(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })
    return apiClient.post('/package/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  confirmarPackage(nombre, descripcion, previewData, cantidades) {
    const formData = new FormData()
    formData.append('nombre', nombre)
    formData.append('descripcion', descripcion)
    formData.append('preview_data', JSON.stringify(previewData))
    formData.append('cantidades', JSON.stringify(cantidades))
    return apiClient.post('/package/confirmar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  eliminarPackage(packageId) {
    return apiClient.delete(`/package/${packageId}`)
  },

  // ===== MACHINES =====
  listarMachines(soloActivas = true) {
    return apiClient.get('/machine/listar', { params: { solo_activas: soloActivas } })
  },

  obtenerMachine(machineId) {
    return apiClient.get(`/machine/${machineId}`)
  },

  listarTemplates() {
    return apiClient.get('/machine/templates')
  },

  crearMachine(data) {
    return apiClient.post('/machine/crear', data)
  },

  actualizarMachine(machineId, data) {
    return apiClient.put(`/machine/${machineId}`, data)
  },

  eliminarMachine(machineId) {
    return apiClient.delete(`/machine/${machineId}`)
  },

  inicializarTemplates() {
    return apiClient.post('/machine/admin/init_templates')
  },

  // ===== DISTRIBUCIONES =====
  crearDistribucion(packageId, demanda, horasObjetivo, machineIds) {
    return apiClient.post('/distribucion/crear', {
      package_id: packageId,
      demanda: demanda,
      horas_objetivo: horasObjetivo,
      machine_ids: machineIds
    })
  },

  listarDistribuciones() {
    return apiClient.get('/distribucion/listar')
  },

  obtenerDistribucion(distribucionId) {
    return apiClient.get(`/distribucion/${distribucionId}`)
  },

  descargarEstiloMaquina(distribucionId, machineId) {
    return axios({
      url: `/api/distribucion/${distribucionId}/maquina/${machineId}/estilo-excel`,
      method: 'GET',
      responseType: 'blob'
    })
  },

  eliminarDistribucion(distribucionId) {
    return apiClient.delete(`/distribucion/${distribucionId}`)
  },

  // ===== ESTILOS MANUALES =====
  crearEstiloDesdeArchivos(nombre, machineId, archivos, notas) {
    const formData = new FormData()
    formData.append('nombre', nombre)
    formData.append('machine_id', machineId)
    if (notas) formData.append('notas', notas)
    archivos.forEach(archivo => {
      formData.append('archivos', archivo)
    })
    return apiClient.post('/estilo/crear-desde-archivos', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  listarEstilosManuales() {
    return apiClient.get('/estilo/listar')
  },

  obtenerEstiloManual(estiloId) {
    return apiClient.get(`/estilo/${estiloId}`)
  },

  descargarEstiloManual(estiloId) {
    return axios({
      url: `/api/estilo/${estiloId}/excel`,
      method: 'GET',
      responseType: 'blob'
    })
  },

  eliminarEstiloManual(estiloId) {
    return apiClient.delete(`/estilo/${estiloId}`)
  },

  // Health check
  healthCheck() {
    return apiClient.get('/')
  }
}
