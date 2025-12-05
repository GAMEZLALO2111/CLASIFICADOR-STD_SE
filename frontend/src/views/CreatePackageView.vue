<template>
  <div class="create-package-view">
    <Card>
      <h1>➕ Crear Nuevo Package</h1>
      
      <Alert v-if="store.error" type="error" :message="store.error" @close="store.clearError()" />

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label>Nombre del Package</label>
          <input v-model="nombre" type="text" required class="form-input" />
        </div>

        <div class="form-group">
          <label>Descripción (opcional)</label>
          <textarea v-model="descripcion" rows="3" class="form-input"></textarea>
        </div>

        <div class="form-group">
          <label>Archivos .stp</label>
          <input type="file" accept=".stp" multiple @change="handleFiles" ref="fileInput" class="form-input" />
        </div>

        <div v-if="preview.length" class="preview-section">
          <h3>Archivos Cargados</h3>
          <div v-for="(item, idx) in preview" :key="idx" class="preview-item">
            <span>{{ item.filename }}</span>
            <input v-model.number="cantidades[idx]" type="number" min="1" placeholder="Cantidad" required />
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="store.loading || !preview.length" class="btn btn-primary">
            {{ store.loading ? 'Creando...' : 'Crear Package' }}
          </button>
          <button type="button" @click="goBack" class="btn btn-secondary">Cancelar</button>
        </div>
      </form>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/classifier'
import Card from '../components/Card.vue'
import Alert from '../components/Alert.vue'
import api from '../services/api'

const router = useRouter()
const store = useAppStore()

const nombre = ref('')
const descripcion = ref('')
const preview = ref([])
const cantidades = ref([])
const fileInput = ref(null)

const handleFiles = async (event) => {
  const files = Array.from(event.target.files)
  try {
    const response = await api.previewArchivos(files)
    preview.value = response.preview
    cantidades.value = response.preview.map(() => 1)
  } catch (error) {
    store.error = error.message || 'Error al procesar archivos'
  }
}

const handleSubmit = async () => {
  try {
    await store.crearPackage(nombre.value, descripcion.value, preview.value, cantidades.value)
    router.push('/packages')
  } catch (error) {
    console.error(error)
  }
}

const goBack = () => router.push('/packages')
</script>

<style scoped>
.create-package-view { max-width: 800px; margin: 0 auto; }
h1 { color: #2d3748; margin-bottom: 2rem; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #4a5568; }
.form-input { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 6px; font-size: 1rem; }
.form-input:focus { outline: none; border-color: #667eea; }
.preview-section { background: #f7fafc; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; }
.preview-item { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.preview-item input { width: 100px; padding: 0.5rem; border: 2px solid #e2e8f0; border-radius: 6px; }
.form-actions { display: flex; gap: 1rem; }
.btn { padding: 0.75rem 1.5rem; font-size: 1rem; font-weight: 600; border: none; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; flex: 1; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: #667eea; color: white; }
.btn-primary:hover:not(:disabled) { background: #5568d3; }
.btn-secondary { background: white; color: #667eea; border: 2px solid #667eea; }
.btn-secondary:hover { background: #f7fafc; }
</style>
