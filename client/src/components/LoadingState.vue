<script setup>
import { useI18n } from '../composables/useI18n'

// Optional override; defaults to the shared localized "Loading..." text
defineProps({
  message: { type: String, default: '' }
})

const { t } = useI18n()
</script>

<template>
  <div class="loading-state" role="status" aria-live="polite">
    <span class="spinner" aria-hidden="true"></span>
    <span class="loading-text">{{ message || t('common.loading') }}</span>
  </div>
</template>

<style scoped>
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-12) var(--space-4);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: var(--radius-full);
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Keep the spinner visible but static for users who prefer reduced motion */
@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
    border-top-color: var(--color-border);
    border-right-color: var(--color-accent);
  }
}
</style>
