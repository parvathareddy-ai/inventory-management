<script setup>
import { useI18n } from '../composables/useI18n'

// message: localized headline. detail: optional technical text (e.g. err.message), shown small and secondary.
defineProps({
  message: { type: String, default: '' },
  detail: { type: String, default: '' },
  // Hide Retry where repeating the action is unsafe (e.g. submitting an order)
  retryable: { type: Boolean, default: true }
})

const emit = defineEmits(['retry'])

const { t } = useI18n()
</script>

<template>
  <div class="error-state" role="alert">
    <div class="error-body">
      <p class="error-message">{{ message || t('common.loadError') }}</p>
      <p v-if="detail" class="error-detail">{{ detail }}</p>
    </div>
    <button v-if="retryable" type="button" class="retry-button" @click="emit('retry')">
      {{ t('common.retry') }}
    </button>
  </div>
</template>

<style scoped>
.error-state {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-3);
  background: var(--color-danger-soft);
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin: var(--space-4) 0;
}

.error-body {
  min-width: 0;
}

.error-message {
  color: #991b1b;
  font-size: var(--text-sm);
  font-weight: 600;
}

.error-detail {
  margin-top: var(--space-1);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  overflow-wrap: anywhere;
}

.retry-button {
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border-strong);
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  transition: background-color var(--transition), border-color var(--transition);
}

.retry-button:hover {
  background: var(--color-bg);
  border-color: var(--color-text-muted);
}
</style>
