<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && backlogItem" class="modal-overlay" @click="close">
        <div class="modal-container" role="dialog" aria-modal="true" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              {{ isView ? t('dashboard.purchaseOrder.viewTitle') : t('dashboard.purchaseOrder.createTitle') }}
            </h3>
            <button class="close-button" type="button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
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
          </div>

          <div class="modal-footer">
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
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

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

const formatDate = (s) => {
  if (!s) return 'N/A'
  // Parse the YYYY-MM-DD part as a local date; new Date('YYYY-MM-DD') is UTC and shows the previous day in western timezones
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(s)
  const d = m ? new Date(+m[1], +m[2] - 1, +m[3]) : new Date(s)
  if (isNaN(d.getTime())) return s
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
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

const onKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) close()
}
onMounted(() => document.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => document.removeEventListener('keydown', onKeydown))
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 1rem;
}

.modal-container {
  background: var(--color-surface, #fff);
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border, #e2e8f0);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
  letter-spacing: -0.025em;
}

.close-button {
  background: none;
  border: none;
  color: var(--color-text-muted, #64748b);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.close-button:hover {
  background: #f1f5f9;
  color: var(--color-text, #0f172a);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

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
  outline: none;
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
  color: #2563eb;
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

.modal-footer {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid var(--color-border, #e2e8f0);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
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

/* Modal transition animations */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
