<template>
  <BaseModal
    :is-open="isOpen && !!product"
    :title="t('modals.product.title')"
    @close="close"
  >
    <div class="product-header">
      <div class="product-icon">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <rect x="8" y="12" width="32" height="28" rx="2" stroke="currentColor" stroke-width="2.5"/>
          <path d="M16 8V16M32 8V16M8 20H40" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
      </div>
      <div class="product-title-section">
        <h4 class="product-name">{{ product.name }}</h4>
        <div class="product-sku">{{ t('modals.sku') }}: {{ product.sku }}</div>
      </div>
      <span class="stock-badge" :class="getStockBadgeClass(product.stockLevel)">
        {{ stockLabel(product.stockLevel) }}
      </span>
    </div>

    <div class="info-grid">
      <div class="info-item">
        <div class="info-label">{{ t('modals.product.category') }}</div>
        <div class="info-value">{{ product.category }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">{{ t('modals.product.warehouse') }}</div>
        <div class="info-value">{{ product.warehouse }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">{{ t('modals.product.unitsOrdered') }}</div>
        <div class="info-value">{{ product.unitsOrdered }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">{{ t('modals.product.totalRevenue') }}</div>
        <div class="info-value">{{ currencySymbol }}{{ product.revenue.toLocaleString() }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">{{ t('modals.product.currentStock') }}</div>
        <div class="info-value">{{ unitsLabel(product.quantityOnHand) }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">{{ t('modals.product.reorderPoint') }}</div>
        <div class="info-value">{{ unitsLabel(product.reorderPoint) }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">{{ t('modals.product.firstOrderDate') }}</div>
        <div class="info-value">{{ formatDate(product.firstOrderDate) }}</div>
      </div>

      <div class="info-item">
        <div class="info-label">{{ t('modals.product.stockStatus') }}</div>
        <div class="info-value">
          <span :class="['badge', getStockBadgeClass(product.stockLevel)]">
            {{ stockLabel(product.stockLevel) }}
          </span>
        </div>
      </div>
    </div>

    <template #footer>
      <button class="btn-secondary" @click="close">{{ t('common.close') }}</button>
    </template>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { formatDate as formatDate_ } from '../utils/format'

const { t, currentLocale, currentCurrency } = useI18n()

const currencySymbol = computed(() => {
  return currentCurrency.value === 'JPY' ? '¥' : '$'
})

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

// Invalid dates are shown as-is rather than "Invalid Date"
const formatDate = (dateString) =>
  formatDate_(dateString, { locale: currentLocale.value, month: 'long', empty: t('modals.notAvailable') })

// Products with no matching inventory record have no stock numbers; show N/A instead of an unfilled placeholder
const unitsLabel = (count) =>
  count === undefined || count === null ? t('modals.notAvailable') : t('modals.unitsCount', { count })

// stockLevel arrives as an English status string from the parent; the class logic below keys on that raw value
const stockLabel = (stockLevel) => {
  const keys = { 'In Stock': 'inStock', 'Low Stock': 'lowStock', 'Adequate': 'adequate' }
  return keys[stockLevel] ? t(`status.${keys[stockLevel]}`) : stockLevel
}

const getStockBadgeClass = (stockLevel) => {
  if (stockLevel === 'In Stock') return 'success'
  if (stockLevel === 'Low Stock') return 'warning'
  if (stockLevel === 'Out of Stock') return 'danger'
  return 'info'
}
</script>

<style scoped>

.product-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 2rem;
}

.product-icon {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.product-title-section {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.5rem 0;
}

.product-sku {
  font-size: 0.875rem;
  color: #64748b;
  font-family: 'Monaco', 'Courier New', monospace;
}

.stock-badge {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  flex-shrink: 0;
}

.stock-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.stock-badge.warning {
  background: #fed7aa;
  color: #92400e;
}

.stock-badge.danger {
  background: #fecaca;
  color: #991b1b;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.info-value {
  font-size: 0.938rem;
  color: #0f172a;
  font-weight: 500;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  color: #334155;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}
</style>
