<template>
  <div class="create-estilo-view">
    <Card>
      <h1>➕ Crear Estilo Manual</h1>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label>Nombre del Estilo</label>
          <input v-model="nombre" type="text" required class="form-input" />
        </div>

        <div class="form-group">
          <label>Máquina</label>
          <select v-model="machineId" required class="form-input">
            <option value="">Seleccionar...</option>
            <option v-for="machine in store.machines" :key="machine.id" :value="machine.id">
              {{ machine.nombre }} ({{ machine.tipo_maquina }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Archivos .stp</label>
          <input type="file" accept=".stp" multiple @change="handleFiles" class="form-input" />
        </div>

        <div class="form-group">
          <label>Notas (opcional)</label>
          <textarea v-model="notas" rows="3" class="form-input"></textarea>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="store.loading || !archivos.length" class="btn btn-primary">
            {{ store.loading ? 'Creando...' : 'Crear Estilo' }}
          </button>
          <button type="button" @click="goBack" class="btn btn-secondary">Cancelar</button>
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

const router = useRouter()
const store = useAppStore()

const nombre = ref('')
const machineId = ref('')
const archivos = ref([])
const notas = ref('')

onMounted(() => store.loadMachines())

const handleFiles = (event) => {
  archivos.value = Array.from(event.target.files)
}

const handleSubmit = async () => {
  try {
    await store.crearEstilo(nombre.value, machineId.value, archivos.value, notas.value)
    router.push('/estilos')
  } catch (error) {
    console.error(error)
  }
}

const goBack = () => router.push('/estilos')
</script>

<style scoped>
.create-estilo-view { max-width: 800px; margin: 0 auto; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
.form-input { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 6px; }
.form-actions { display: flex; gap: 1rem; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; flex: 1; }
.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: white; color: #667eea; border: 2px solid #667eea; }
</style>
