<template>
  <div class="home-view">
    <Card class="hero-card">
      <h1 class="title">Sistema Clasificador STD</h1>
      <p class="subtitle">
        Sistema experto para distribución de setups en máquinas CNC, gestión de packages y generación de estilos de herramientas
      </p>
      <div class="cta-buttons">
        <button @click="goToPackages" class="btn btn-primary">
          Gestionar Packages
        </button>
        <button @click="goToDistribuciones" class="btn btn-secondary">
          Ver Distribuciones
        </button>
      </div>
    </Card>

    <div class="features-grid">
      <Card class="feature-card">
        <div class="feature-icon">📦</div>
        <h3>Packages</h3>
        <p>Crea packages subiendo archivos .stp con configuraciones de parts</p>
      </Card>

      <Card class="feature-card">
        <div class="feature-icon">⚙️</div>
        <h3>Distribución Automática</h3>
        <p>Asigna parts a máquinas de forma óptima según demanda y capacidad</p>
      </Card>

      <Card class="feature-card">
        <div class="feature-icon">🛠️</div>
        <h3>Estilos de Herramientas</h3>
        <p>Genera estilos unificados para configuración de máquinas</p>
      </Card>

      <Card class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Reportes Excel</h3>
        <p>Descarga configuraciones en formato Excel para los técnicos</p>
      </Card>
    </div>

    <Card class="info-card">
      <h2>Flujo de Trabajo</h2>
      <ol class="steps-list">
        <li><strong>Crear Package:</strong> Sube archivos .stp y asigna cantidades</li>
        <li><strong>Crear Distribución:</strong> Selecciona package, demanda y máquinas disponibles</li>
        <li><strong>Revisar Asignaciones:</strong> Ve qué parts van a qué máquinas</li>
        <li><strong>Descargar Estilos:</strong> Genera archivos Excel con configuración de estaciones</li>
        <li><strong>Estilos Manuales:</strong> Crea configuraciones personalizadas cuando lo necesites</li>
      </ol>
    </Card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import Card from '../components/Card.vue'

const router = useRouter()

const goToPackages = () => {
  router.push('/packages')
}

const goToDistribuciones = () => {
  router.push('/distribuciones')
}
</script>

<style scoped>
.home-view {
  max-width: 1200px;
  margin: 0 auto;
}

.hero-card {
  text-align: center;
  padding: 3rem 2rem;
  margin-bottom: 3rem;
}

.title {
  font-size: 2.5rem;
  color: #2d3748;
  margin-bottom: 1rem;
  font-weight: 700;
}

.subtitle {
  font-size: 1.25rem;
  color: #718096;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.cta-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.feature-card {
  text-align: center;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: #718096;
  line-height: 1.6;
}

.info-card {
  margin-bottom: 2rem;
}

.info-card h2 {
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.steps-list {
  color: #4a5568;
  line-height: 2;
  font-size: 1.1rem;
}

.steps-list li {
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {
  .title {
    font-size: 1.75rem;
  }

  .subtitle {
    font-size: 1rem;
  }

  .cta-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
