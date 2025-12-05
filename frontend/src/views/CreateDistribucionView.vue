<template>
  <div class="create-dist-view">
    <Card>
      <h1>➕ Nueva Distribución</h1>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label>Package</label>
          <select v-model="packageId" required class="form-input">
            <option value="">Seleccionar...</option>
            <option v-for="pkg in store.packages" :key="pkg.id" :value="pkg.id">
              {{ pkg.nombre }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Demanda</label>
          <input v-model.number="demanda" type="number" min="1" required class="form-input" />
        </div>

        <div class="form-group">
          <label>Horas Objetivo</label>
          <input v-model.number="horasObjetivo" type="number" min="1" required class="form-input" />
        </div>

        <div class="form-group">
          <label>Máquinas Disponibles</label>
          <div v-for="machine in store.machines" :key="machine.id" class="checkbox">
            <input type="checkbox" :value="machine.id" v-model="machineIds" />
            <span>{{ machine.nombre }} ({{ machine.tipo_maquina }})</span>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="store.loading" class="btn btn-primary">
            {{ store.loading ? 'Creando...' : 'Crear' }}
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

const packageId = ref('')
const demanda = ref(100)
const horasObjetivo = ref(8)
const machineIds = ref([])

onMounted(async () => {
  await Promise.all([store.loadPackages(), store.loadMachines()])
})

const handleSubmit = async () => {
  try {
    const result = await store.crearDistribucion(packageId.value, demanda.value, horasObjetivo.value, machineIds.value)
    router.push(`/distribuciones/${result.id}`)
  } catch (error) {
    console.error(error)
  }
}

const goBack = () => router.push('/distribuciones')
</script>

<style scoped>
.create-dist-view { max-width: 800px; margin: 0 auto; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; }
.form-input { width: 100%; padding: 0.75rem; border: 2px solid #e2e8f0; border-radius: 6px; }
.checkbox { margin-bottom: 0.5rem; }
.form-actions { display: flex; gap: 1rem; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; flex: 1; }
.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: white; color: #667eea; border: 2px solid #667eea; }
</style>
