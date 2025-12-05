<template>
  <div class="create-machine-view">
    <Card>
      <h1>➕ Crear Nueva Máquina</h1>
      
      <Alert v-if="store.error" type="error" :message="store.error" @close="store.clearError()" />

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label>Nombre de la Máquina *</label>
          <input v-model="formData.nombre" type="text" required class="form-input" placeholder="Ej: T-101" />
        </div>

        <div class="form-group">
          <label>Modelo *</label>
          <input v-model="formData.modelo" type="text" required class="form-input" placeholder="Ej: TRUMPF TruPunch 3000" />
        </div>

        <div class="form-group">
          <label>Template / Tipo de Máquina *</label>
          <select v-model.number="formData.template_id" required class="form-input">
            <option value="">Seleccionar template...</option>
            <option v-for="template in store.templates" :key="template.id" :value="template.id">
              {{ template.tipo_maquina }} ({{ template.estaciones_totales }} estaciones, {{ template.autoindex_count }} autoindex)
            </option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Mesa X (mm) *</label>
            <input v-model.number="formData.mesa_x" type="number" required class="form-input" placeholder="Ej: 2500" />
          </div>

          <div class="form-group">
            <label>Mesa Y (mm) *</label>
            <input v-model.number="formData.mesa_y" type="number" required class="form-input" placeholder="Ej: 1250" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Thickness Mínimo (mm) *</label>
            <input v-model.number="formData.thickness_min" type="number" step="0.1" required class="form-input" placeholder="Ej: 0.5" />
          </div>

          <div class="form-group">
            <label>Thickness Máximo (mm) *</label>
            <input v-model.number="formData.thickness_max" type="number" step="0.1" required class="form-input" placeholder="Ej: 6.0" />
          </div>
        </div>

        <div class="form-group">
          <label>Estaciones Dañadas (opcional)</label>
          <input v-model="estacionesDanadas" type="text" class="form-input" placeholder="Ej: 1A, 2B, 3C (separadas por comas)" />
          <small class="form-hint">Ingresa las estaciones que no están disponibles, separadas por comas</small>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input v-model="formData.activa" type="checkbox" />
            <span>Máquina Activa</span>
          </label>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="store.loading" class="btn btn-primary">
            {{ store.loading ? 'Creando...' : 'Crear Máquina' }}
          </button>
          <button type="button" @click="goBack" class="btn btn-secondary">
            Cancelar
          </button>
        </div>
      </form>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/classifier'
import Card from '../components/Card.vue'
import Alert from '../components/Alert.vue'

const router = useRouter()
const store = useAppStore()

const formData = reactive({
  nombre: '',
  modelo: '',
  template_id: '',
  mesa_x: 2500,
  mesa_y: 1250,
  thickness_min: 0.5,
  thickness_max: 6.0,
  activa: true
})

const estacionesDanadas = ref('')

onMounted(async () => {
  await store.loadTemplates()
})

const handleSubmit = async () => {
  try {
    // Procesar estaciones dañadas
    const estaciones = estacionesDanadas.value
      .split(',')
      .map(e => e.trim())
      .filter(e => e.length > 0)

    const data = {
      ...formData,
      estaciones_dañadas: estaciones
    }

    await store.crearMachine(data)
    router.push('/machines')
  } catch (error) {
    console.error(error)
  }
}

const goBack = () => {
  router.push('/machines')
}
</script>

<style scoped>
.create-machine-view {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #2d3748;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #4a5568;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-hint {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #718096;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  color: #4a5568;
}

.checkbox-label input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #f7fafc;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
