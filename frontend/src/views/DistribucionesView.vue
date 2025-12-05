<template>
  <div class="distribuciones-view">
    <Card>
      <div class="header">
        <h1>⚙️ Distribuciones</h1>
        <button @click="goToCreate" class="btn btn-primary">➕ Nueva Distribución</button>
      </div>

      <LoadingSpinner v-if="store.loading && !store.distribuciones.length" />

      <div v-else-if="store.hasDistribuciones" class="list">
        <Card v-for="dist in store.distribuciones" :key="dist.id" class="item">
          <h3>{{ dist.package_nombre }}</h3>
          <p>Demanda: {{ dist.demanda }} | Horas: {{ dist.horas_objetivo }}</p>
          <p :class="dist.es_factible ? 'success' : 'error'">
            {{ dist.es_factible ? '✅ Factible' : '❌ No Factible' }}
          </p>
          <button @click="viewDetails(dist.id)" class="btn btn-secondary">Ver Detalles</button>
          <button @click="deleteItem(dist.id)" class="btn btn-danger">Eliminar</button>
        </Card>
      </div>

      <div v-else class="empty">
        <h2>No hay distribuciones</h2>
        <button @click="goToCreate" class="btn btn-primary">Crear Distribución</button>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/classifier'
import Card from '../components/Card.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const store = useAppStore()

onMounted(() => store.loadDistribuciones())

const goToCreate = () => router.push('/distribuciones/create')
const viewDetails = (id) => router.push(`/distribuciones/${id}`)
const deleteItem = async (id) => {
  if (confirm('¿Eliminar?')) await store.deleteDistribucion(id)
}
</script>

<style scoped>
.header { display: flex; justify-content: space-between; margin-bottom: 2rem; }
.list { display: grid; gap: 1rem; }
.item { display: grid; gap: 0.5rem; }
.btn { padding: 0.5rem 1rem; margin-right: 0.5rem; border: none; border-radius: 6px; cursor: pointer; }
.btn-primary { background: #667eea; color: white; }
.btn-secondary { background: white; color: #667eea; border: 2px solid #667eea; }
.btn-danger { background: #f56565; color: white; }
.success { color: #48bb78; font-weight: 600; }
.error { color: #f56565; font-weight: 600; }
.empty { text-align: center; padding: 3rem; }
</style>
