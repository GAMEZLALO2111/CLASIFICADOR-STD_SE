<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        <h1>🏭 Clasificador STD</h1>
      </div>
      <ul class="nav-menu">
        <li>
          <RouterLink to="/" class="nav-link" active-class="active">
            Inicio
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/packages" class="nav-link" active-class="active">
            Packages
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/distribuciones" class="nav-link" active-class="active">
            Distribuciones
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/estilos" class="nav-link" active-class="active">
            Estilos
          </RouterLink>
        </li>
        <li>
          <RouterLink to="/machines" class="nav-link" active-class="active">
            Máquinas
          </RouterLink>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.navbar {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.nav-brand h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #667eea;
  font-weight: 700;
}

.nav-menu {
  display: flex;
  gap: 2rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-link {
  text-decoration: none;
  color: #4a5568;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: #f7fafc;
  color: #667eea;
}

.nav-link.active {
  background: #667eea;
  color: white;
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 1rem;
    flex-direction: column;
    height: auto;
    padding-top: 1rem;
    padding-bottom: 1rem;
  }

  .nav-brand h1 {
    font-size: 1.25rem;
  }

  .nav-menu {
    gap: 1rem;
    margin-top: 1rem;
  }
}
</style>
