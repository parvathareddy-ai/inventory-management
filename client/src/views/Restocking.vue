<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <!-- Budget slider stays mounted during refetches so dragging is never interrupted -->
    <div class="card budget-card">
      <div class="budget-header">
        <label for="budget-slider" class="budget-label">{{ t('restocking.budgetSlider') }}</label>
        <span class="budget-value">{{ formatCurrency(budget) }}</span>
      </div>
      <input
        id="budget-slider"
        v-model.number="budget"
        class="budget-slider"
        type="range"
        min="0"
        max="100000"
        step="1000"
        :style="{ '--fill': (budget / 100000 * 100) + '%' }"
      />
      <div class="budget-scale">
        <span>{{ formatCurrency(0) }}</span>
        <span>{{ formatCurrency(100000) }}</span>
      </div>
    </div>

    <!-- Outside the v-if chain so a failed refetch cannot hide the confirmation -->
    <div v-if="confirmation" class="confirmation" role="status">
      <div>
        <strong>{{ t('restocking.orderPlaced') }}</strong>
        <span class="confirmation-text">
          {{ t('restocking.orderConfirmation', { id: confirmation.id, date: formatDate(confirmation.expected_delivery) }) }}
        </span>
      </div>
      <router-link to="/orders" class="confirmation-link">{{ t('restocking.viewOrders') }}</router-link>
    </div>
    <!-- Not retryable: re-clicking would re-submit a purchase, so the user re-confirms via the Place Order button -->
    <ErrorState v-if="orderError" :message="orderError" :retryable="false" />

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="t('restocking.loadError')" :detail="error" @retry="retryLoad" />
    <div v-else-if="recommendations">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.budget') }}</div>
          <div class="stat-value">{{ formatCurrency(recommendations.budget) }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.plannedSpend') }}</div>
          <div class="stat-value">{{ formatCurrency(recommendations.total_cost) }}</div>
          <div class="stat-meta">{{ t('restocking.itemsPlanned', { count: recommendations.items.length }) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ formatCurrency(recommendations.remaining_budget) }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ recommendations.items.length }})</h3>
          <button
            type="button"
            class="place-order-btn"
            :disabled="recommendations.items.length === 0 || submitting || planStale"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="recommendations.items.length === 0" class="empty-state">
          {{ t('restocking.emptyState') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.item') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.supplier') }}</th>
                <th class="num">{{ t('restocking.table.quantity') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations.items" :key="item.sku">
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ translateProductName(item.name) }}</td>
                <td>
                  <span :class="['badge', item.trend]">{{ trendLabel(item.trend) }}</span>
                </td>
                <td>{{ item.supplier }}</td>
                <td class="num">{{ item.quantity.toLocaleString() }}</td>
                <td class="num">{{ formatUnitCost(item.unit_cost) }}</td>
                <td class="num"><strong>{{ formatCurrency(item.line_total) }}</strong></td>
                <td class="num">{{ item.lead_time_days }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import LoadingState from '../components/LoadingState.vue'
import ErrorState from '../components/ErrorState.vue'
import { formatCurrency as formatCurrencyUtil, formatCurrencyWithDecimals } from '../utils/currency'

const DEBOUNCE_MS = 250

export default {
  name: 'Restocking',
  components: { LoadingState, ErrorState },
  setup() {
    const { t, currentCurrency, currentLocale, translateProductName } = useI18n()

    // Budget is always held in USD; conversion happens only at display time
    const budget = ref(25000)
    const recommendations = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const submitting = ref(false)
    const orderError = ref(null)
    const confirmation = ref(null)
    // True from a slider change until the matching plan arrives, so a quick click cannot
    // submit a plan that no longer matches the budget on screen
    const planStale = ref(false)

    let debounceTimer = null
    // Monotonic id so a slow earlier response cannot overwrite a newer one
    let requestSeq = 0

    const formatCurrency = (value) => formatCurrencyUtil(value, currentCurrency.value)
    // Unit costs are small and fractional (e.g. $42.50), so whole-dollar rounding would misstate them
    const formatUnitCost = (value) => formatCurrencyWithDecimals(value, currentCurrency.value, 2)

    const formatDate = (dateString) => {
      // Parse a bare YYYY-MM-DD as a local date; new Date() treats it as UTC and shows a day early
      const dateOnly = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateString)
      const date = dateOnly ? new Date(+dateOnly[1], +dateOnly[2] - 1, +dateOnly[3]) : new Date(dateString)
      if (isNaN(date.getTime())) return dateString
      return date.toLocaleDateString(currentLocale.value === 'ja' ? 'ja-JP' : 'en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Fall back to the raw trend if the server sends a value without a translation
    const trendLabel = (trend) => {
      const key = `trends.${trend}`
      const label = t(key)
      return label === key ? trend : label
    }

    const loadRecommendations = async () => {
      const seq = ++requestSeq
      try {
        const data = await api.getRestockingRecommendations(budget.value)
        if (seq !== requestSeq) return // stale response
        recommendations.value = data
        planStale.value = false
        error.value = null
      } catch (err) {
        if (seq !== requestSeq) return
        planStale.value = false
        console.error(err)
        error.value = err?.message || 'Error'
      } finally {
        if (seq === requestSeq) loading.value = false
      }
    }

    // Debounce slider changes
    watch(budget, () => {
      planStale.value = true
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(loadRecommendations, DEBOUNCE_MS)
    })

    const placeOrder = async () => {
      if (submitting.value || !recommendations.value || recommendations.value.items.length === 0) return
      submitting.value = true
      orderError.value = null
      confirmation.value = null
      const plan = recommendations.value
      try {
        const order = await api.submitRestockingOrder({
          budget: plan.budget,
          items: plan.items.map(i => ({ sku: i.sku, quantity: i.quantity }))
        })
        confirmation.value = order
        // Refetch: units just ordered are subtracted from the shortfall, so the plan shrinks
        await loadRecommendations()
      } catch (err) {
        // Server returns { detail } on 400; fall back to the generic message
        orderError.value = err.response?.data?.detail || t('restocking.orderError')
      } finally {
        submitting.value = false
      }
    }

    // Retry shows the spinner again; loadRecommendations is sequence-guarded so repeated clicks cannot race
    const retryLoad = () => {
      loading.value = true
      error.value = null
      return loadRecommendations()
    }

    onMounted(loadRecommendations)
    onBeforeUnmount(() => clearTimeout(debounceTimer))

    return {
      t,
      budget,
      recommendations,
      loading,
      error,
      submitting,
      orderError,
      confirmation,
      planStale,
      formatCurrency,
      formatUnitCost,
      formatDate,
      trendLabel,
      translateProductName,
      placeOrder,
      retryLoad
    }
  }
}
</script>

<style scoped>
.budget-card {
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
}

.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 0.75rem;
}

.budget-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
}

.budget-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #0f172a;
}

/* Custom range slider: filled track via --fill, set inline from the budget value */
.budget-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  cursor: pointer;
  background: linear-gradient(to right, #0f172a 0%, #0f172a var(--fill), #e2e8f0 var(--fill), #e2e8f0 100%);
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #0f172a;
  cursor: pointer;
}

.budget-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #0f172a;
  cursor: pointer;
}

.budget-slider:focus-visible::-webkit-slider-thumb {
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.25);
}

.budget-slider:focus-visible::-moz-range-thumb {
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.25);
}

.budget-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
}

.stat-meta {
  margin-top: 0.25rem;
  font-size: 0.813rem;
  color: #64748b;
}

.place-order-btn {
  background: #0f172a;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.place-order-btn:hover:not(:disabled) {
  background: #1e293b;
}

.place-order-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.confirmation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.938rem;
}

.confirmation-text {
  margin-left: 0.5rem;
}

.confirmation-link {
  color: #0f172a;
  font-weight: 500;
  text-decoration: underline;
}

.empty-state {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

th.num,
td.num {
  text-align: right;
}
</style>
