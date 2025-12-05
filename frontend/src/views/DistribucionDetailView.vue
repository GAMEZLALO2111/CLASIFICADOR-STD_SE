<template>
  <div class="detail-view">
    <LoadingSpinner v-if="loading" />
    
    <div v-else-if="distribucion" class="content">
      <!-- Header -->
      <Card class="header-card">
        <div class="header-content">
          <div>
            <h1 class="page-title">📦 {{ distribucion.package_nombre }}</h1>
            <div class="metadata">
              <span class="badge">Demanda: {{ distribucion.demanda }} unidades</span>
              <span class="badge">Horas objetivo: {{ distribucion.horas_objetivo }}h</span>
              <span class="badge">Máquinas: {{ distribucion.asignaciones?.length || 0 }}</span>
            </div>
          </div>
          
          <div class="status-badge" :class="{ success: distribucion.es_factible, error: !distribucion.es_factible }">
            {{ distribucion.es_factible ? '✅ Factible' : '❌ No Factible' }}
          </div>
        </div>
      </Card>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <Card class="stat-card">
          <div class="stat-icon">🏭</div>
          <div class="stat-content">
            <h3>{{ distribucion.asignaciones?.length || 0 }}</h3>
            <p>Máquinas Utilizadas</p>
          </div>
        </Card>
        
        <Card class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-content">
            <h3>{{ totalParts }}</h3>
            <p>Parts Asignados</p>
          </div>
        </Card>
        
        <Card class="stat-card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <h3>{{ totalHoras.toFixed(1) }}h</h3>
            <p>Tiempo Total</p>
          </div>
        </Card>
        
        <Card class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <h3>{{ promedioUtilizacion.toFixed(1) }}%</h3>
            <p>Utilización Promedio</p>
          </div>
        </Card>
      </div>

      <!-- Machines Grid -->
      <h2 class="section-title">🏭 Detalle por Máquina</h2>
      
      <div class="machines-grid">
        <Card v-for="asignacion in distribucion.asignaciones" :key="asignacion.machine_id" class="machine-detail-card">
          <div class="machine-header">
            <div>
              <h3>{{ asignacion.machine_nombre }}</h3>
              <span class="machine-type-badge">{{ asignacion.tipo_maquina }}</span>
            </div>
            <button @click="descargarEstilo(asignacion.machine_id)" class="btn-icon" title="Descargar Excel">
              📥
            </button>
          </div>

          <!-- Progress Bar -->
          <div class="progress-section">
            <div class="progress-header">
              <span>Tiempo Utilizado</span>
              <span class="progress-value">
                {{ asignacion.tiempo_total_usado.toFixed(2) }}h / {{ asignacion.tiempo_disponible }}h
              </span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :class="getProgressClass(asignacion)"
                :style="{ width: getUtilizacion(asignacion) + '%' }"
              ></div>
            </div>
            <p class="progress-percentage">
              {{ getUtilizacion(asignacion).toFixed(1) }}% utilización
            </p>
          </div>

          <!-- Parts List -->
          <div class="parts-section">
            <h4>📋 Parts Asignados ({{ asignacion.parts_asignados.length }})</h4>
            <div class="parts-list">
              <div v-for="part in asignacion.parts_asignados" :key="part.part_number" class="part-item">
                <div class="part-info">
                  <strong>{{ part.part_number }}</strong>
                  <span class="part-quantity">{{ part.cantidad_asignada }} pzs</span>
                </div>
                <div class="part-stats">
                  <span>⏱️ {{ part.horas_corrida.toFixed(2) }}h</span>
                  <span>🔧 {{ part.estaciones_unificadas }} est.</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Estilo Preview -->
          <div v-if="asignacion.estilo && asignacion.estilo.length > 0" class="estilo-preview">
            <h4>🔧 Vista Previa Estilo</h4>
            <div class="estilo-summary">
              <span>Total herramientas: {{ asignacion.estilo.length }}</span>
              <span class="overflow-indicator" :class="getOverflowClass(asignacion)">
                {{ getOverflowStatus(asignacion) }}
              </span>
            </div>
          </div>
        </Card>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button @click="descargarTodo" class="btn btn-primary btn-lg">
          📥 Descargar Todos los Estilos
        </button>
        <button @click="goBack" class="btn btn-secondary btn-lg">
          ← Volver a Lista
        </button>
      </div>
    </div>

    <Card v-else>
      <p class="error-message">❌ No se pudo cargar la distribución</p>
      <button @click="goBack" class="btn btn-secondary">← Volver</button>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/classifier'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const distribucion = ref(null)
const loading = ref(true)

const totalParts = computed(() => {
  if (!distribucion.value?.asignaciones) return 0
  return distribucion.value.asignaciones.reduce((sum, a) => sum + a.parts_asignados.length, 0)
})

const totalHoras = computed(() => {
  if (!distribucion.value?.asignaciones) return 0
  return distribucion.value.asignaciones.reduce((sum, a) => sum + a.tiempo_total_usado, 0)
})

const promedioUtilizacion = computed(() => {
  if (!distribucion.value?.asignaciones || distribucion.value.asignaciones.length === 0) return 0
  const totalUtil = distribucion.value.asignaciones.reduce((sum, a) => {
    return sum + getUtilizacion(a)
  }, 0)
  return totalUtil / distribucion.value.asignaciones.length
})

onMounted(async () => {
  try {
    distribucion.value = await store.getDistribucion(route.params.id)
  } catch (err) {
    console.error('Error loading distribucion:', err)
  } finally {
    loading.value = false
  }
})

const getUtilizacion = (asignacion) => {
  return (asignacion.tiempo_total_usado / asignacion.tiempo_disponible) * 100
}

const getProgressClass = (asignacion) => {
  const util = getUtilizacion(asignacion)
  if (util > 95) return 'excellent'
  if (util > 80) return 'good'
  if (util > 50) return 'medium'
  return 'low'
}

const getOverflowStatus = (asignacion) => {
  const maxStations = asignacion.tipo_maquina === '4I' ? 52 : 
                      asignacion.tipo_maquina === '2I' ? 20 : 8
  const used = asignacion.estilo.length
  const overflow = used - maxStations
  
  if (overflow > 0) return `⚠️ Overflow: +${overflow}`
  return `✅ OK (${used}/${maxStations})`
}

const getOverflowClass = (asignacion) => {
  const maxStations = asignacion.tipo_maquina === '4I' ? 52 : 
                      asignacion.tipo_maquina === '2I' ? 20 : 8
  const used = asignacion.estilo.length
  return used > maxStations ? 'overflow-error' : 'overflow-ok'
}

const descargarEstilo = async (machineId) => {
  try {
    const response = await api.descargarEstiloMaquina(route.params.id, machineId)
    const url = window.URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `estilo_machine_${machineId}.xlsx`
    a.click()
  } catch (error) {
    console.error('Error descargando estilo:', error)
    alert('Error al descargar el estilo Excel')
  }
}

const descargarTodo = async () => {
  for (const asignacion of distribucion.value.asignaciones) {
    await descargarEstilo(asignacion.machine_id)
    // Pequeña pausa entre descargas
    await new Promise(resolve => setTimeout(resolve, 500))
  }
}

const goBack = () => router.push('/distribuciones')
</script>

<style scoped>
.detail-view { 
  max-width: 1400px; 
  margin: 0 auto; 
}

.content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Header */
.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: start;
}

.page-title {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.metadata {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
}

.status-badge {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.1rem;
}

.status-badge.success {
  background: #48bb78;
}

.status-badge.error {
  background: #f56565;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-icon {
  font-size: 3rem;
}

.stat-content h3 {
  font-size: 2rem;
  margin: 0;
  color: #2d3748;
}

.stat-content p {
  margin: 0;
  color: #718096;
  font-size: 0.9rem;
}

/* Section Title */
.section-title {
  font-size: 1.5rem;
  color: #2d3748;
  margin: 2rem 0 1rem 0;
}

/* Machines Grid */
.machines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.machine-detail-card {
  padding: 1.5rem;
}

.machine-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1.5rem;
}

.machine-header h3 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
}

.machine-type-badge {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-icon {
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #667eea;
  border-color: #667eea;
  transform: scale(1.1);
}

/* Progress Section */
.progress-section {
  margin-bottom: 1.5rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #718096;
}

.progress-value {
  font-weight: 600;
  color: #2d3748;
}

.progress-bar {
  height: 20px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 10px;
}

.progress-fill.excellent {
  background: linear-gradient(90deg, #48bb78, #38a169);
}

.progress-fill.good {
  background: linear-gradient(90deg, #4299e1, #3182ce);
}

.progress-fill.medium {
  background: linear-gradient(90deg, #ed8936, #dd6b20);
}

.progress-fill.low {
  background: linear-gradient(90deg, #f56565, #e53e3e);
}

.progress-percentage {
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #718096;
  text-align: right;
}

/* Parts Section */
.parts-section {
  margin-bottom: 1.5rem;
}

.parts-section h4 {
  margin-bottom: 0.75rem;
  color: #2d3748;
}

.parts-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem;
}

.part-item {
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.part-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.part-info strong {
  color: #2d3748;
}

.part-quantity {
  color: #667eea;
  font-weight: 600;
}

.part-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.85rem;
  color: #718096;
}

/* Estilo Preview */
.estilo-preview {
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.estilo-preview h4 {
  margin-bottom: 0.5rem;
  color: #2d3748;
}

.estilo-summary {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.overflow-indicator {
  font-weight: 600;
}

.overflow-ok {
  color: #48bb78;
}

.overflow-error {
  color: #f56565;
}

/* Actions */
.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-lg {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #f7fafc;
}

.error-message {
  color: #f56565;
  font-size: 1.2rem;
  text-align: center;
  padding: 2rem;
}

@media (max-width: 768px) {
  .machines-grid {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>
