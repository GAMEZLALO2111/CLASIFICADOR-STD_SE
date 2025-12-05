<template>
  <div class="packages-view">
    <Card>
      <div class="header">
        <h1>📦 Packages</h1>
        <button @click="goToCreate" class="btn btn-primary">
          ➕ Crear Package
        </button>
      </div>

      <Alert v-if="store.error" type="error" :message="store.error" @close="store.clearError()" />

      <LoadingSpinner v-if="store.loading && !store.packages.length" message="Cargando packages..." />

      <div v-else-if="store.hasPackages" class="packages-grid">
        <Card v-for="pkg in store.packages" :key="pkg.id" class="package-card">
          <div class="package-header">
            <h3>{{ pkg.nombre }}</h3>
            <span class="package-id">ID: {{ pkg.id }}</span>
          </div>
          
          <p v-if="pkg.descripcion" class="package-desc">{{ pkg.descripcion }}</p>
          
          <div class="package-info">
            <div class="info-item">
              <span class="label">Parts:</span>
              <span class="value">{{ pkg.total_parts }}</span>
            </div>
            <div class="info-item">
              <span class="label">Creado:</span>
              <span class="value">{{ formatDate(pkg.fecha_creacion) }}</span>
            </div>
            <div class="info-item">
              <span class="label">Expira:</span>
              <span class="value">{{ formatDate(pkg.fecha_expiracion) }}</span>
            </div>
          </div>

          <div class="package-actions">
            <button @click="viewDetails(pkg.id)" class="btn btn-secondary btn-sm">
              👁️ Ver Detalles
            </button>
            <button @click="deletePackage(pkg.id)" class="btn btn-danger btn-sm">
              🗑️ Eliminar
            </button>
          </div>
        </Card>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📦</div>
        <h2>No hay packages</h2>
        <p>Crea tu primer package para comenzar</p>
        <button @click="goToCreate" class="btn btn-primary">
          Crear Package
        </button>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/classifier'
import Card from '../components/Card.vue'
import Alert from '../components/Alert.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()
const store = useAppStore()

onMounted(() => {
  store.loadPackages()
})

const goToCreate = () => {
  router.push('/packages/create')
}

const viewDetails = (id) => {
  router.push(`/distribuciones/create?package=${id}`)
}

const deletePackage = async (id) => {
  if (confirm('¿Estás seguro de eliminar este package?')) {
    try {
      await store.deletePackage(id)
    } catch (error) {
      console.error(error)
    }
  }
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.packages-view {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e2e8f0;
}

.header h1 {
  margin: 0;
  color: #2d3748;
}

.packages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.package-card {
  transition: transform 0.2s;
}

.package-card:hover {
  transform: translateY(-4px);
}

.package-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.package-header h3 {
  margin: 0;
  color: #2d3748;
}

.package-id {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.package-desc {
  color: #718096;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.package-info {
  background: #f7fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #4a5568;
}

.value {
  color: #2d3748;
}

.package-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
  flex: 1;
}

.btn-secondary:hover {
  background: #f7fafc;
}

.btn-danger {
  background: #f56565;
  color: white;
}

.btn-danger:hover {
  background: #e53e3e;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h2 {
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #718096;
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .packages-grid {
    grid-template-columns: 1fr;
  }

  .header {
    flex-direction: column;
    gap: 1rem;
  }

  .btn {
    width: 100%;
  }
}
</style>
