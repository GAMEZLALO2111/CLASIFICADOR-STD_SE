<template>
  <div class="detail-view">
    <Card v-if="distribucion">
      <h1>{{ distribucion.package_nombre }}</h1>
      <p>Demanda: {{ distribucion.demanda }} | Horas: {{ distribucion.horas_objetivo }}</p>
      <p :class="distribucion.es_factible ? 'success' : 'error'">
        {{ distribucion.es_factible ? '✅ Factible' : '❌ No Factible' }}
      </p>

      <h2>Máquinas Asignadas</h2>
      <Card v-for="asignacion in distribucion.asignaciones" :key="asignacion.machine_id" class="machine-card">
        <h3>{{ asignacion.machine_nombre }}</h3>
        <p>Parts: {{ asignacion.parts_asignados.length }}</p>
        <p>Tiempo: {{ asignacion.tiempo_total_usado.toFixed(2) }}h / {{ asignacion.tiempo_disponible }}h</p>
        <button @click="descargarEstilo(asignacion.machine_id)" class="btn btn-primary">
          📥 Descargar Estilo Excel
        </button>
      </Card>

      <button @click="goBack" class="btn btn-secondary">← Volver</button>
    </Card>

    <LoadingSpinner v-else />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '../stores/classifier'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import api from '../services/api'

const route = useRoute()
const router = useRouter()
const store = useAppStore()
const distribucion = ref(null)

onMounted(async () => {
  distribucion.value = await store.getDistribucion(route.params.id)
})

const descargarEstilo = async (machineId) => {
  try {
    const response = await api.descargarEstiloMaquina(route.params.id, machineId)
    const url = window.URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `estilo_machine_${machineId}.xlsx`
    a.click()
  } catch (error) {
    console.error(error)
  }
}

const goBack = () => router.push('/distribuciones')
</script>

<style scoped>
.detail-view { max-width: 1200px; margin: 0 auto; }
.machine-card { margin: 1rem 0; }
.btn { padding: 0.75rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; margin-top: 1rem; }
.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: white; color: #667eea; border: 2px solid #667eea; }
.success { color: #48bb78; font-weight: 600; }
.error { color: #f56565; font-weight: 600; }
</style>
