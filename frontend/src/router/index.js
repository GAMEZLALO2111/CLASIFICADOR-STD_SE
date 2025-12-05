import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PackagesView from '../views/PackagesView.vue'
import CreatePackageView from '../views/CreatePackageView.vue'
import DistribucionesView from '../views/DistribucionesView.vue'
import CreateDistribucionView from '../views/CreateDistribucionView.vue'
import DistribucionDetailView from '../views/DistribucionDetailView.vue'
import EstilosView from '../views/EstilosView.vue'
import CreateEstiloView from '../views/CreateEstiloView.vue'
import MachinesView from '../views/MachinesView.vue'
import CreateMachineView from '../views/CreateMachineView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/packages',
      name: 'packages',
      component: PackagesView
    },
    {
      path: '/packages/create',
      name: 'create-package',
      component: CreatePackageView
    },
    {
      path: '/distribuciones',
      name: 'distribuciones',
      component: DistribucionesView
    },
    {
      path: '/distribuciones/create',
      name: 'create-distribucion',
      component: CreateDistribucionView
    },
    {
      path: '/distribuciones/:id',
      name: 'distribucion-detail',
      component: DistribucionDetailView
    },
    {
      path: '/estilos',
      name: 'estilos',
      component: EstilosView
    },
    {
      path: '/estilos/create',
      name: 'create-estilo',
      component: CreateEstiloView
    },
    {
      path: '/machines',
      name: 'machines',
      component: MachinesView
    },
    {
      path: '/machines/create',
      name: 'create-machine',
      component: CreateMachineView
    }
  ]
})

export default router
