import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAppStore = defineStore('app', () => {
  const loading = ref(false)
  const error = ref(null)

  // ===== PACKAGES =====
  const packages = ref([])
  const currentPackage = ref(null)

  async function loadPackages() {
    loading.value = true
    error.value = null
    try {
      const response = await api.listarPackages()
      packages.value = response.data || []
    } catch (err) {
      error.value = err.message || 'Error al cargar packages'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getPackage(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.obtenerPackage(id)
      currentPackage.value = response
      return response
    } catch (err) {
      error.value = err.message || 'Error al obtener package'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function crearPackage(nombre, descripcion, previewData, cantidades) {
    loading.value = true
    error.value = null
    try {
      const response = await api.confirmarPackage(nombre, descripcion, previewData, cantidades)
      await loadPackages()
      return response
    } catch (err) {
      error.value = err.message || 'Error al crear package'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deletePackage(id) {
    loading.value = true
    error.value = null
    try {
      await api.eliminarPackage(id)
      await loadPackages()
    } catch (err) {
      error.value = err.message || 'Error al eliminar package'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ===== MACHINES =====
  const machines = ref([])
  const templates = ref([])

  async function loadMachines() {
    loading.value = true
    error.value = null
    try {
      const response = await api.listarMachines()
      machines.value = response.data || []
    } catch (err) {
      error.value = err.message || 'Error al cargar máquinas'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadTemplates() {
    loading.value = true
    error.value = null
    try {
      const response = await api.listarTemplates()
      templates.value = response.data || []
    } catch (err) {
      error.value = err.message || 'Error al cargar templates'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function crearMachine(data) {
    loading.value = true
    error.value = null
    try {
      const response = await api.crearMachine(data)
      await loadMachines()
      return response
    } catch (err) {
      error.value = err.message || 'Error al crear máquina'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteMachine(id) {
    loading.value = true
    error.value = null
    try {
      await api.eliminarMachine(id)
      await loadMachines()
    } catch (err) {
      error.value = err.message || 'Error al eliminar máquina'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ===== DISTRIBUCIONES =====
  const distribuciones = ref([])
  const currentDistribucion = ref(null)

  async function loadDistribuciones() {
    loading.value = true
    error.value = null
    try {
      const response = await api.listarDistribuciones()
      distribuciones.value = response || []
    } catch (err) {
      error.value = err.message || 'Error al cargar distribuciones'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function crearDistribucion(packageId, demanda, horasObjetivo, machineIds) {
    loading.value = true
    error.value = null
    try {
      const response = await api.crearDistribucion(packageId, demanda, horasObjetivo, machineIds)
      currentDistribucion.value = response
      await loadDistribuciones()
      return response
    } catch (err) {
      error.value = err.message || 'Error al crear distribución'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function getDistribucion(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.obtenerDistribucion(id)
      currentDistribucion.value = response
      return response
    } catch (err) {
      error.value = err.message || 'Error al obtener distribución'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteDistribucion(id) {
    loading.value = true
    error.value = null
    try {
      await api.eliminarDistribucion(id)
      await loadDistribuciones()
    } catch (err) {
      error.value = err.message || 'Error al eliminar distribución'
      throw err
    } finally {
      loading.value = false
    }
  }

  // ===== ESTILOS MANUALES =====
  const estilos = ref([])
  const currentEstilo = ref(null)

  async function loadEstilos() {
    loading.value = true
    error.value = null
    try {
      const response = await api.listarEstilosManuales()
      estilos.value = response || []
    } catch (err) {
      error.value = err.message || 'Error al cargar estilos'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function crearEstilo(nombre, machineId, archivos, notas) {
    loading.value = true
    error.value = null
    try {
      const response = await api.crearEstiloDesdeArchivos(nombre, machineId, archivos, notas)
      await loadEstilos()
      return response
    } catch (err) {
      error.value = err.message || 'Error al crear estilo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteEstilo(id) {
    loading.value = true
    error.value = null
    try {
      await api.eliminarEstiloManual(id)
      await loadEstilos()
    } catch (err) {
      error.value = err.message || 'Error al eliminar estilo'
      throw err
    } finally {
      loading.value = false
    }
  }

  // Limpiar error
  function clearError() {
    error.value = null
  }

  // Computed
  const hasPackages = computed(() => packages.value.length > 0)
  const hasDistribuciones = computed(() => distribuciones.value.length > 0)
  const hasEstilos = computed(() => estilos.value.length > 0)
  const hasMachines = computed(() => machines.value.length > 0)

  return {
    loading,
    error,
    clearError,
    // Packages
    packages,
    currentPackage,
    hasPackages,
    loadPackages,
    getPackage,
    crearPackage,
    deletePackage,
    // Machines
    machines,
    templates,
    hasMachines,
    loadMachines,
    loadTemplates,
    crearMachine,
    deleteMachine,
    // Distribuciones
    distribuciones,
    currentDistribucion,
    hasDistribuciones,
    loadDistribuciones,
    crearDistribucion,
    getDistribucion,
    deleteDistribucion,
    // Estilos
    estilos,
    currentEstilo,
    hasEstilos,
    loadEstilos,
    crearEstilo,
    deleteEstilo
  }
})
