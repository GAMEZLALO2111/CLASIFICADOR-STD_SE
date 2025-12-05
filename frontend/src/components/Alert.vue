<template>
  <div v-if="show" class="alert" :class="typeClass">
    <span class="alert-icon">{{ icon }}</span>
    <span class="alert-message">{{ message }}</span>
    <button v-if="closable" @click="$emit('close')" class="alert-close">×</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  show: {
    type: Boolean,
    default: true
  },
  closable: {
    type: Boolean,
    default: true
  }
})

defineEmits(['close'])

const typeClass = computed(() => `alert-${props.type}`)

const icon = computed(() => {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  }
  return icons[props.type]
})
</script>

<style scoped>
.alert {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
}

.alert-icon {
  margin-right: 1rem;
  font-size: 1.5rem;
}

.alert-message {
  flex: 1;
}

.alert-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  margin-left: 1rem;
  opacity: 0.7;
  transition: opacity 0.3s ease;
}

.alert-close:hover {
  opacity: 1;
}

.alert-success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-warning {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
}

.alert-info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}
</style>
