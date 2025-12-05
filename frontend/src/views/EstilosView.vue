<template>
  <div class="estilos-view">
    <Card>
      <div class="header">
        <h1>🛠️ Estilos Manuales</h1>
        <button @click="goToCreate" class="btn btn-primary">➕ Crear Estilo</button>
      </div>

      <LoadingSpinner v-if="store.loading && !store.estilos.length" />

      <div v-else-if="store.hasEstilos" class="list">
        <Card v-for="estilo in store.estilos" :key="estilo.id" class="item">
          <h3>{{ estilo.nombre }}</h3>
          <p>Máquina: {{ estilo.machine_nombre }} | Tipo: {{ estilo.tipo_maquina }}</p>
          <p>Parts: {{ estilo.part_numbers.length }}</p>
          <p>Expira: {{ new Date(estilo.expires_at).toLocaleDateString('es-ES') }}</p>
          <button @click="descargar(estilo.id)" class="btn btn-primary">📥 Descargar</button>
          <button @click="deleteItem(estilo.id)" class="btn btn-danger">Eliminar</button>
        </Card>
      </div>

      <div v-else class="empty">
        <h2>No hay estilos manuales</h2>
        <button @click="goToCreate" class="btn btn-primary">Crear Estilo</button>
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
import api from '../services/api'

const router = useRouter()
const store = useAppStore()

onMounted(() => store.loadEstilos())

const goToCreate = () => router.push('/estilos/create')
const deleteItem = async (id) => {
  if (confirm('¿Eliminar?')) await store.deleteEstilo(id)
}

const descargar = async (id) => {
  try {
    const response = await api.descargarEstiloManual(id)
    const url = window.URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `estilo_manual_${id}.xlsx`
    a.click()
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped>
.header { display: flex; justify-content: space-between; margin-bottom: 2rem; }
.list { display: grid; gap: 1rem; }
.item { display: grid; gap: 0.5rem; }
.btn { padding: 0.5rem 1rem; margin-right: 0.5rem; border: none; border-radius: 6px; cursor: pointer; }
.btn-primary { background: #667eea; color: white; }
.btn-danger { background: #f56565; color: white; }
.empty { text-align: center; padding: 3rem; }
</style>
