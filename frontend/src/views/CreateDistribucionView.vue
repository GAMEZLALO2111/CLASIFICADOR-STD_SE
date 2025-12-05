<template>
  <div class="create-dist-view">
    <Card>
      <h1 class="page-title">🎯 Nueva Distribución de Producción</h1>
      <p class="page-subtitle">Configure los parámetros para la asignación óptima de parts a máquinas</p>

      <Alert v-if="error" type="error" @close="error = null">{{ error }}</Alert>
      <Alert v-if="successMessage" type="success" @close="successMessage = null">{{ successMessage }}</Alert>

      <form @submit.prevent="handleSubmit" class="form">
        <!-- Package Selection -->
        <div class="form-section">
          <h3>📦 Package</h3>
          <div class="form-group">
            <label>Seleccionar Package *</label>
            <select v-model="packageId" required class="form-input" @change="onPackageChange">
              <option value="">-- Seleccione un package --</option>
              <option v-for="pkg in store.packages" :key="pkg.id" :value="pkg.id">
                {{ pkg.nombre }} ({{ pkg.parts?.length || 0 }} parts)
              </option>
            </select>
          </div>
        </div>

        <!-- Parameters -->
        <div class="form-section">
          <h3>⚙️ Parámetros de Producción</h3>
          
          <div class="form-row">
            <div class="form-group">
              <label>Demanda *</label>
              <input 
                v-model.number="demanda" 
                type="number" 
                min="1" 
                required 
                class="form-input"
                placeholder="ej: 100"
              />
              <small>Cantidad de unidades a producir</small>
            </div>

            <div class="form-group">
              <label>Horas Objetivo por Máquina *</label>
              <input 
                v-model.number="horasObjetivo" 
                type="number" 
                min="1" 
                required 
                class="form-input"
                placeholder="ej: 96 o 144"
              />
              <small>Horas máximas disponibles por máquina</small>
            </div>
          </div>
        </div>

        <!-- Machine Selection -->
        <div class="form-section">
          <h3>🏭 Máquinas Disponibles</h3>
          <p class="section-description">
            Seleccione las máquinas que estarán disponibles para esta distribución. 
            El algoritmo asignará los parts respetando las capacidades de cada máquina.
          </p>
          
          <div class="machines-grid">
            <div 
              v-for="machine in store.machines" 
              :key="machine.id" 
              class="machine-card"
              :class="{ selected: machineIds.includes(machine.id) }"
              @click="toggleMachine(machine.id)"
            >
              <input 
                type="checkbox" 
                :value="machine.id" 
                v-model="machineIds"
                class="machine-checkbox"
              />
              <div class="machine-info">
                <h4>{{ machine.nombre }}</h4>
                <span class="machine-type">{{ machine.tipo_maquina }}</span>
                <div class="machine-specs">
                  <span>⚡ {{ getStations(machine.tipo_maquina) }} estaciones</span>
                </div>
              </div>
            </div>
          </div>
          
          <p v-if="machineIds.length === 0" class="warning-text">
            ⚠️ Debe seleccionar al menos una máquina
          </p>
        </div>

        <!-- Actions -->
        <div class="form-actions">
          <button 
            type="submit" 
            :disabled="store.loading || machineIds.length === 0" 
            class="btn btn-primary btn-lg"
          >
            <span v-if="!store.loading">🚀 Crear Distribución</span>
            <span v-else>⏳ Procesando...</span>
          </button>
          <button type="button" @click="goBack" class="btn btn-secondary btn-lg">
            ← Cancelar
          </button>
        </div>
      </form>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/classifier'
import Card from '../components/Card.vue'
import Alert from '../components/Alert.vue'

const router = useRouter()
const store = useAppStore()

const packageId = ref('')
const demanda = ref(100)
const horasObjetivo = ref(96)
const machineIds = ref([])
const error = ref(null)
const successMessage = ref(null)

onMounted(async () => {
  try {
    await Promise.all([store.loadPackages(), store.loadMachines()])
    // Pre-seleccionar todas las máquinas por defecto
    machineIds.value = store.machines.map(m => m.id)
  } catch (err) {
    error.value = 'Error al cargar datos iniciales'
  }
})

const onPackageChange = () => {
  error.value = null
}

const toggleMachine = (id) => {
  const index = machineIds.value.indexOf(id)
  if (index > -1) {
    machineIds.value.splice(index, 1)
  } else {
    machineIds.value.push(id)
  }
}

const getStations = (tipo) => {
  const stations = {
    '4I': 52,
    '2I': 20,
    '45STA': 8
  }
  return stations[tipo] || '?'
}

const handleSubmit = async () => {
  error.value = null
  successMessage.value = null
  
  if (!packageId.value) {
    error.value = 'Debe seleccionar un package'
    return
  }
  
  if (machineIds.value.length === 0) {
    error.value = 'Debe seleccionar al menos una máquina'
    return
  }
  
  try {
    const result = await store.crearDistribucion(
      packageId.value, 
      demanda.value, 
      horasObjetivo.value, 
      machineIds.value
    )
    successMessage.value = '✅ Distribución creada exitosamente!'
    setTimeout(() => {
      router.push(`/distribuciones/${result.id}`)
    }, 1000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error al crear distribución'
  }
}

const goBack = () => router.push('/distribuciones')
</script>

<style scoped>
.create-dist-view { 
  max-width: 1000px; 
  margin: 0 auto; 
}

.page-title {
  font-size: 2rem;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: #718096;
  margin-bottom: 2rem;
}

.form-section {
  background: #f7fafc;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.form-section h3 {
  margin-bottom: 1rem;
  color: #2d3748;
}

.section-description {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group { 
  margin-bottom: 1.5rem; 
}

.form-group label { 
  display: block; 
  margin-bottom: 0.5rem; 
  font-weight: 600;
  color: #2d3748;
}

.form-group small {
  display: block;
  color: #718096;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.form-input { 
  width: 100%; 
  padding: 0.75rem; 
  border: 2px solid #e2e8f0; 
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.machines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.machine-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: start;
  gap: 0.75rem;
}

.machine-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.machine-card.selected {
  border-color: #667eea;
  background: #eef2ff;
}

.machine-checkbox {
  margin-top: 0.25rem;
  cursor: pointer;
}

.machine-info {
  flex: 1;
}

.machine-info h4 {
  margin: 0 0 0.25rem 0;
  color: #2d3748;
  font-size: 1rem;
}

.machine-type {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.machine-specs {
  margin-top: 0.5rem;
  color: #718096;
  font-size: 0.85rem;
}

.warning-text {
  color: #f59e0b;
  font-weight: 600;
  margin-top: 1rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
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

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e2e8f0;
  color: #2d3748;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .machines-grid {
    grid-template-columns: 1fr;
  }
}
</style>
