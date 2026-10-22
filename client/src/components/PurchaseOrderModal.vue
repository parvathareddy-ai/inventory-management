<template>
  <BaseModal
    :is-open="isOpen && !!backlogItem"
    :title="isView ? t('dashboard.purchaseOrder.viewTitle') : t('dashboard.purchaseOrder.createTitle')"
    size="sm"
    @close="close"
  >
    <!-- Context: which backlog item this PO relates to -->
    <div class="context-card">
      <div class="context-name">{{ translateProductName(backlogItem.item_name) }}</div>
      <div class="context-meta">
        <span>SKU: {{ backlogItem.item_sku }}</span>
        <span>{{ t('dashboard.purchaseOrder.order') }}: {{ backlogItem.order_id }}</span>
        <span>{{ t('dashboard.purchaseOrder.shortage') }}: {{ shortage }}</span>
      </div>
    </div>

    <!-- View mode -->
    <template v-if="isView">
      <p v-if="!po" class="empty-text">{{ t('dashboard.purchaseOrder.none') }}</p>
      <div v-else class="info-grid">
        <div v-for="row in viewRows" :key="row.key" class="info-item">
          <div class="info-label">{{ row.label }}</div>
          <div class="info-value" :class="row.class">
            <span v-if="row.key === 'status'" class="badge info">{{ row.value }}</span>
            <template v-else>{{ row.value }}</template>
          </div>
        </div>
      </div>
    </template>

    <!-- Create mode -->
    <form v-else id="po-form" class="po-form" novalidate @submit.prevent="submit">
      <div class="form-field">
        <label for="po-supplier">{{ t('dashboard.purchaseOrder.supplier') }}</label>
        <input id="po-supplier" v-model="form.supplier_name" type="text" maxlength="120" autocomplete="off" />
      </div>

      <div class="form-row">
        <div class="form-field">
          <label for="po-qty">{{ t('dashboard.purchaseOrder.quantity') }}</label>
          <input id="po-qty" v-model.number="form.quantity" type="number" min="1" step="1" />
        </div>
        <div class="form-field">
          <label for="po-cost">{{ t('dashboard.purchaseOrder.unitCost') }} (USD)</label>
          <input id="po-cost" v-model.number="form.unit_cost" type="number" min="0" step="0.01" />
        </div>
      </div>

      <div class="form-field">
        <label for="po-date">{{ t('dashboard.purchaseOrder.expectedDelivery') }}</label>
        <input id="po-date" v-model="form.expected_delivery_date" type="date" :min="today" />
      </div>

      <div class="form-field">
        <label for="po-notes">{{ t('dashboard.purchaseOrder.notes') }}</label>
        <textarea id="po-notes" v-model="form.notes" rows="3" maxlength="500"></textarea>
      </div>

      <div class="total-row">
        <span>{{ t('dashboard.purchaseOrder.totalCost') }}</span>
        <strong>{{ totalDisplay }}</strong>
      </div>

      <div v-if="errorMessage" class="form-error" role="alert">{{ errorMessage }}</div>
    </form>

    <template #footer>
      <button class="btn-secondary" type="button" @click="close">
        {{ isView ? t('dashboard.purchaseOrder.close') : t('dashboard.purchaseOrder.cancel') }}
      </button>
      <button
        v-if="!isView"
        class="btn-primary"
        type="submit"
        form="po-form"
        :disabled="!isValid || submitting"
      >
        {{ submitting ? t('dashboard.purchaseOrder.submitting') : t('dashboard.purchaseOrder.submit') }}
      </button>
    </template>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'
import { ref, reactive, computed, watch } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'
import { formatDate as formatDate_ } from '../utils/format'

const { t, translateProductName } = useI18n()

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  backlogItem: { type: Object, default: null },
  mode: {
    type: String,
    default: 'create',
    validator: (v) => ['create', 'view'].includes(v)
  }
})

const emit = defineEmits(['close', 'po-created'])

const isView = computed(() => props.mode === 'view')
const po = computed(() => props.backlogItem?.purchase_order || null)

const shortage = computed(() => {
  if (!props.backlogItem) return 0
  return Math.max(0, props.backlogItem.quantity_needed - props.backlogItem.quantity_available)
})

// Local-time YYYY-MM-DD (toISOString would use UTC and can be off by a day)
const toDateInput = (d) => {
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}
const today = computed(() => toDateInput(new Date()))

const form = reactive({
  supplier_name: '',
  quantity: 1,
  unit_cost: null,
  expected_delivery_date: '',
  notes: ''
})
const submitting = ref(false)
const errorMessage = ref('')

const resetForm = () => {
  form.supplier_name = ''
  // Default to the shortage so the PO covers the gap; never below the API minimum of 1
  form.quantity = Math.max(1, shortage.value)
  form.unit_cost = null
  form.expected_delivery_date = ''
  form.notes = ''
  errorMessage.value = ''
  submitting.value = false
}

// Reset whenever the modal opens or a different item is selected
watch(() => [props.isOpen, props.backlogItem], ([open]) => {
  if (open) resetForm()
}, { immediate: true })

const total = computed(() => (Number(form.quantity) || 0) * (Number(form.unit_cost) || 0))
const totalDisplay = computed(() => formatCurrencyWithDecimals(total.value, 'USD', 2))

const isValid = computed(() =>
  form.supplier_name.trim().length > 0 &&
  Number.isInteger(form.quantity) && form.quantity >= 1 &&
  typeof form.unit_cost === 'number' && form.unit_cost >= 0 &&
  !!form.expected_delivery_date && form.expected_delivery_date >= today.value
)

// The PO detail view is English-only today, so the locale is fixed
const formatDate = (s) => formatDate_(s, { locale: 'en', month: 'long', empty: 'N/A' })
const money = (n) => formatCurrencyWithDecimals(Number(n) || 0, 'USD', 2)

const viewRows = computed(() => {
  const p = po.value
  if (!p) return []
  const L = (k) => t(`dashboard.purchaseOrder.${k}`)
  return [
    { key: 'id', label: L('poId'), value: p.id, class: 'mono' },
    { key: 'status', label: L('status'), value: p.status },
    { key: 'supplier', label: L('supplier'), value: p.supplier_name },
    { key: 'quantity', label: L('quantity'), value: p.quantity },
    { key: 'unit_cost', label: L('unitCost'), value: money(p.unit_cost) },
    { key: 'total', label: L('totalCost'), value: money(p.quantity * p.unit_cost) },
    { key: 'delivery', label: L('expectedDelivery'), value: formatDate(p.expected_delivery_date) },
    { key: 'created', label: L('createdDate'), value: formatDate(p.created_date) },
    { key: 'notes', label: L('notes').replace(/\s*[(（].*$/, ''), value: p.notes || '-' }
  ]
})

const close = () => {
  if (submitting.value) return
  emit('close')
}

const submit = async () => {
  if (!isValid.value || submitting.value) return
  submitting.value = true
  errorMessage.value = ''
  try {
    const payload = {
      backlog_item_id: props.backlogItem.id,
      supplier_name: form.supplier_name.trim(),
      quantity: form.quantity,
      unit_cost: form.unit_cost,
      expected_delivery_date: form.expected_delivery_date
    }
    const notes = form.notes.trim()
    if (notes) payload.notes = notes
    const created = await api.createPurchaseOrder(payload)
    emit('po-created', created)
  } catch (err) {
    // FastAPI returns detail as a string (400/404/409) or a list (422)
    const detail = err?.response?.data?.detail
    errorMessage.value = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map(d => d.msg).join('; ')
        : t('dashboard.purchaseOrder.error')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>

.context-card {
  background: #f8fafc;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.context-name {
  font-weight: 700;
  color: var(--color-text, #0f172a);
  margin-bottom: 0.25rem;
}

.context-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem 1rem;
  font-size: 0.813rem;
  color: var(--color-text-muted, #64748b);
}

.po-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-field label {
  font-size: 0.813rem;
  font-weight: 600;
  color: var(--color-text-muted, #64748b);
}

.form-field input,
.form-field textarea {
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-border-strong, #cbd5e1);
  border-radius: 8px;
  font-size: 0.875rem;
  font-family: inherit;
  color: var(--color-text, #0f172a);
  background: #fff;
}

.form-field input:focus,
.form-field textarea:focus {
  border-color: var(--color-accent, #2563eb);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f8fafc;
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 8px;
  font-size: 0.875rem;
  color: var(--color-text-muted, #64748b);
}

.total-row strong {
  font-size: 1.125rem;
  color: var(--color-text, #0f172a);
}

.form-error {
  padding: 0.75rem 1rem;
  background: var(--color-danger-soft, #fef2f2);
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.875rem;
}

.empty-text {
  color: var(--color-text-muted, #64748b);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.info-label {
  font-size: 0.813rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted, #64748b);
}

.info-value {
  font-size: 0.938rem;
  font-weight: 500;
  color: var(--color-text, #0f172a);
  word-break: break-word;
}

.info-value.mono {
  font-family: 'Monaco', 'Courier New', monospace;
  color: var(--color-info-text);
}

.badge.info {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  background: #dbeafe;
  color: #1e40af;
  font-size: 0.813rem;
  font-weight: 600;
}

.btn-secondary,
.btn-primary {
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
}

.btn-secondary {
  background: #f1f5f9;
  border: 1px solid var(--color-border, #e2e8f0);
  color: #334155;
}

.btn-secondary:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.btn-primary {
  background: var(--color-accent, #2563eb);
  border: 1px solid var(--color-accent, #2563eb);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-accent-hover, #1d4ed8);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
