<template>
  <div class="machines-view">
    <Card>
      <div class="header">
        <h1>🏭 Máquinas</h1>
        <button @click="goToCreate" class="btn btn-primary">
          ➕ Crear Máquina
        </button>
      </div>

      <Alert v-if="store.error" type="error" :message="store.error" @close="store.clearError()" />

      <LoadingSpinner v-if="store.loading && !store.machines.length" message="Cargando máquinas..." />

      <div v-else-if="store.hasMachines" class="machines-grid">
        <Card v-for="machine in store.machines" :key="machine.id" class="machine-card">
          <div class="machine-header">
            <h3>{{ machine.nombre }}</h3>
            <span class="machine-badge" :class="machine.activa ? 'active' : 'inactive'">
              {{ machine.activa ? '✓ Activa' : '✕ Inactiva' }}
            </span>
          </div>
          
          <div class="machine-info">
            <div class="info-row">
              <span class="label">Modelo:</span>
              <span class="value">{{ machine.modelo }}</span>
            </div>
            <div class="info-row">
              <span class="label">Tipo:</span>
              <span class="value">{{ machine.tipo_maquina }}</span>
            </div>
            <div class="info-row">
              <span class="label">Mesa:</span>
              <span class="value">{{ machine.mesa }}</span>
            </div>
            <div class="info-row">
              <span class="label">Thickness:</span>
              <span class="value">{{ machine.thickness }}</span>
            </div>
            <div v-if="machine.estaciones_dañadas && machine.estaciones_dañadas.length" class="info-row">
              <span class="label">Estaciones dañadas:</span>
              <span class="value damaged">{{ machine.estaciones_dañadas.join(', ') }}</span>
            </div>
          </div>

          <div class="machine-actions">
            <button @click="deleteMachine(machine.id)" class="btn btn-danger btn-sm">
              🗑️ Eliminar
            </button>
          </div>
        </Card>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">🏭</div>
        <h2>No hay máquinas registradas</h2>
        <p>Crea tu primera máquina para comenzar</p>
        <button @click="goToCreate" class="btn btn-primary">
          Crear Máquina
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
  store.loadMachines()
})

const goToCreate = () => {
  router.push('/machines/create')
}

const deleteMachine = async (id) => {
  if (confirm('¿Estás seguro de eliminar esta máquina?')) {
    try {
      await store.deleteMachine(id)
    } catch (error) {
      console.error(error)
    }
  }
}
</script>

<style scoped>
.machines-view {
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

.machines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.machine-card {
  transition: transform 0.2s;
}

.machine-card:hover {
  transform: translateY(-4px);
}

.machine-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f7fafc;
}

.machine-header h3 {
  margin: 0;
  color: #2d3748;
}

.machine-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
}

.machine-badge.active {
  background: #c6f6d5;
  color: #22543d;
}

.machine-badge.inactive {
  background: #fed7d7;
  color: #742a2a;
}

.machine-info {
  background: #f7fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: 600;
  color: #4a5568;
}

.value {
  color: #2d3748;
}

.value.damaged {
  color: #e53e3e;
  font-weight: 600;
}

.machine-actions {
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
  width: 100%;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
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
  .machines-grid {
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
