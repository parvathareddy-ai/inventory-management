<template>
  <div class="orders">
    <div class="page-header">
      <h1>{{ t('orders.title') }}</h1>
      <p>{{ t('orders.description') }}</p>
    </div>

    <LoadingState v-if="loading" />
    <ErrorState v-else-if="error" :message="t('orders.loadError')" :detail="error" @retry="retryLoad" />
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card success">
          <div class="stat-label">{{ t('status.delivered') }}</div>
          <div class="stat-value">{{ statusCounts.Delivered }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('status.shipped') }}</div>
          <div class="stat-value">{{ statusCounts.Shipped }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('status.processing') }}</div>
          <div class="stat-value">{{ statusCounts.Processing }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">{{ t('status.backordered') }}</div>
          <div class="stat-value">{{ statusCounts.Backordered }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h2 class="card-title">{{ t('orders.allOrders') }} ({{ orders.length }})</h2>
        </div>
        <div class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">{{ t('orders.table.orderNumber') }}</th>
                <th class="col-customer">{{ t('orders.table.customer') }}</th>
                <th class="col-items">{{ t('orders.table.items') }}</th>
                <th class="col-status">{{ t('orders.table.status') }}</th>
                <th class="col-date">{{ t('orders.table.orderDate') }}</th>
                <th class="col-date">{{ t('orders.table.expectedDelivery') }}</th>
                <th class="col-value">{{ t('orders.table.totalValue') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orderRows" :key="order.id">
                <td class="col-order-number"><strong>{{ order.order_number }}</strong></td>
                <td class="col-customer">{{ translateCustomerName(order.customer) }}</td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{ t('orders.itemsCount', { count: order.items.length }) }}
                    </summary>
                    <div class="items-dropdown">
                      <!-- sku can repeat within one order, so pair it with the line position -->
                      <div v-for="(item, idx) in order.items" :key="`${item.sku}-${idx}`" class="item-entry">
                        <span class="item-name">{{ translateProductName(item.name) }}</span>
                        <span class="item-meta">{{ t('orders.quantity') }}: {{ item.quantity }} @ {{ currencySymbol }}{{ item.unit_price }}</span>
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-status">
                  <span :class="['badge', getOrderStatusClass(order.status)]">
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </span>
                </td>
                <td class="col-date">{{ order.orderDateLabel }}</td>
                <td class="col-date">{{ order.expectedDeliveryLabel }}</td>
                <td class="col-value"><strong>{{ currencySymbol }}{{ order.total_value.toLocaleString() }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Restocking orders: loaded once on mount, independent of the filters above -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">{{ t('orders.submittedOrders') }} ({{ submittedOrders.length }})</h2>
        </div>
        <ErrorState
          v-if="submittedError"
          :message="t('orders.submittedError')"
          :detail="submittedError"
          @retry="retrySubmitted"
        />
        <LoadingState v-else-if="submittedLoading" />
        <div v-else-if="submittedOrders.length === 0" class="empty-state">
          {{ t('orders.noSubmittedOrders') }}
        </div>
        <div v-else class="table-container">
          <table class="submitted-table">
            <thead>
              <tr>
                <th>{{ t('orders.submitted.orderId') }}</th>
                <th>{{ t('orders.submitted.orderDate') }}</th>
                <th>{{ t('orders.submitted.items') }}</th>
                <th class="num">{{ t('orders.submitted.total') }}</th>
                <th class="num">{{ t('orders.submitted.leadTime') }}</th>
                <th>{{ t('orders.submitted.expectedDelivery') }}</th>
                <th>{{ t('orders.submitted.status') }}</th>
              </tr>
            </thead>
            <tbody>
              <!-- Each order renders as a summary row plus an optional detail row, so use a keyed template -->
              <template v-for="order in submittedOrders" :key="order.id">
                <tr>
                  <td><strong>{{ order.id }}</strong></td>
                  <td>{{ formatDate(order.order_date) }}</td>
                  <td>
                    <button
                      type="button"
                      class="expand-btn"
                      :aria-expanded="isExpanded(order.id)"
                      :title="t('orders.perItemLeadTimes')"
                      @click="toggleExpanded(order.id)"
                    >
                      <span :class="['expand-icon', { open: isExpanded(order.id) }]">&#9654;</span>
                      {{ t('orders.itemsCount', { count: order.items.length }) }}
                    </button>
                    <div class="sku-list">{{ order.items.map(i => i.sku).join(', ') }}</div>
                  </td>
                  <td class="num"><strong>{{ formatCurrency(order.total_cost) }}</strong></td>
                  <td class="num">{{ order.overall_lead_time_days }}</td>
                  <td>{{ formatDate(order.expected_delivery) }}</td>
                  <td><span class="badge info">{{ order.status }}</span></td>
                </tr>
                <tr v-if="isExpanded(order.id)" class="detail-row">
                  <td colspan="7">
                    <table class="detail-table">
                      <thead>
                        <tr>
                          <th>{{ t('orders.submitted.sku') }}</th>
                          <th class="num">{{ t('orders.submitted.quantity') }}</th>
                          <th>{{ t('orders.submitted.supplier') }}</th>
                          <th class="num">{{ t('orders.submitted.leadTime') }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="item in order.items" :key="item.sku">
                          <td>{{ item.sku }}</td>
                          <td class="num">{{ item.quantity.toLocaleString() }}</td>
                          <td>{{ item.supplier }}</td>
                          <td class="num">{{ item.lead_time_days }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, shallowRef, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useLatestRequest } from '../composables/useLatestRequest'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import LoadingState from '../components/LoadingState.vue'
import ErrorState from '../components/ErrorState.vue'
import { getOrders } from '../composables/useOrdersStore'
import { formatDate as formatDateUtil, currencyFormatter } from '../utils/format'

export default {
  name: 'Orders',
  components: { LoadingState, ErrorState },
  setup() {
    const { t, currentLocale, currentCurrency, translateProductName, translateCustomerName } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })
    const loading = ref(true)
    const error = ref(null)
    // Replaced wholesale on each load, never mutated: shallowRef skips deep proxying
    const orders = shallowRef([])

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    // Only the newest request may apply data / loading / error; filter changes are debounced
    const { run: loadOrders, trigger: scheduleLoad } = useLatestRequest(
      () => getOrders(getCurrentFilters()),
      {
        loading,
        error,
        onData: (fetchedOrders) => {
          // Sort orders by order_date (earliest first). The array is shared (and frozen) by the
          // orders store, so sort a copy; ISO dates compare correctly as strings.
          orders.value = [...fetchedOrders].sort((a, b) =>
            a.order_date < b.order_date ? -1 : a.order_date > b.order_date ? 1 : 0
          )
        },
        onError: (err) => {
          // Keep the raw message as secondary detail only; the headline is localized in the template
          console.error(err)
          error.value = err?.message || 'Error'
        }
      }
    )

    // Watch for filter changes and reload data
    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], scheduleLoad)

    // One pass for all four stat cards (was one .filter per card per render)
    const statusCounts = computed(() => {
      const counts = { Delivered: 0, Shipped: 0, Processing: 0, Backordered: 0 }
      for (const order of orders.value) {
        if (counts[order.status] !== undefined) counts[order.status]++
      }
      return counts
    })

    // Rows with dates formatted once per data/locale change instead of per cell per render
    const orderRows = computed(() =>
      orders.value.map(order => ({
        ...order,
        orderDateLabel: formatDate(order.order_date),
        expectedDeliveryLabel: formatDate(order.expected_delivery)
      }))
    )

    const getOrderStatusClass = (status) => {
      const statusMap = {
        'Delivered': 'success',
        'Shipped': 'info',
        'Processing': 'warning',
        'Backordered': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const formatDate = (dateString) => formatDateUtil(dateString, { locale: currentLocale.value })

    // Submitted restocking orders (independent of the filters)
    const submittedOrders = shallowRef([])
    const submittedLoading = ref(true)
    const submittedError = ref(null)
    // Set of order ids whose per-item detail row is open
    const expandedIds = ref(new Set())

    // Latest-wins guard: a stale or duplicate (Retry spam) response never overwrites a newer one
    let submittedSeq = 0
    const loadSubmittedOrders = async () => {
      const id = ++submittedSeq
      submittedLoading.value = true
      submittedError.value = null
      try {
        const data = await api.getSubmittedOrders()
        if (id !== submittedSeq) return
        submittedOrders.value = data
      } catch (err) {
        if (id !== submittedSeq) return
        console.error(err)
        submittedError.value = err?.message || 'Error'
      } finally {
        if (id === submittedSeq) submittedLoading.value = false
      }
    }

    const isExpanded = (id) => expandedIds.value.has(id)
    const toggleExpanded = (id) => {
      // Replace the Set so the ref triggers a re-render
      const next = new Set(expandedIds.value)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      expandedIds.value = next
    }

    // Server amounts are USD; convert for display
    const formatCurrency = currencyFormatter(currentCurrency)

    onMounted(() => {
      loadOrders()
      loadSubmittedOrders()
    })

    return {
      t,
      loading,
      error,
      // run() restarts the request and supersedes any in-flight one, so repeated clicks cannot race
      retryLoad: loadOrders,
      orders,
      orderRows,
      statusCounts,
      getOrderStatusClass,
      formatDate,
      formatCurrency,
      submittedOrders,
      submittedLoading,
      submittedError,
      retrySubmitted: loadSubmittedOrders,
      isExpanded,
      toggleExpanded,
      currencySymbol,
      translateProductName,
      translateCustomerName
    }
  }
}
</script>

<style scoped>
/* Submitted orders */
.empty-state {
  padding: 2.5rem 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.submitted-table th.num,
.submitted-table td.num,
.detail-table th.num,
.detail-table td.num {
  text-align: right;
}

.expand-btn {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: var(--color-info-text);
  font-weight: 500;
  font-size: inherit;
}

.expand-btn:hover {
  color: var(--color-info-text);
  text-decoration: underline;
}

.expand-icon {
  display: inline-block;
  margin-right: 0.375rem;
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.expand-icon.open {
  transform: rotate(90deg);
}

.sku-list {
  margin-top: 0.25rem;
  font-size: 0.813rem;
  color: #64748b;
}

.detail-row > td {
  background: #f8fafc;
}

.detail-table {
  width: 100%;
}

/* Fixed table layout to prevent column shifting */
.orders-table {
  table-layout: fixed;
  width: 100%;
}

/* Column widths */
.col-order-number {
  width: 130px;
}

.col-customer {
  width: 180px;
}

.col-items {
  width: 200px;
}

.col-status {
  width: 130px;
}

.col-date {
  width: 140px;
}

.col-value {
  width: 120px;
}

/* Items details styling */
.items-details {
  position: relative;
}

.items-summary {
  cursor: pointer;
  color: var(--color-info-text);
  font-weight: 500;
  list-style: none;
  user-select: none;
  display: inline-block;
}

.items-summary::-webkit-details-marker {
  display: none;
}

.items-summary::before {
  content: '▶';
  display: inline-block;
  margin-right: 0.375rem;
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.items-details[open] .items-summary::before {
  transform: rotate(90deg);
}

.items-summary:hover {
  color: var(--color-info-text);
  text-decoration: underline;
}

/* Dropdown container */
.items-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 0.75rem;
  z-index: 10;
  min-width: 300px;
  max-width: 400px;
}

.item-entry {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.item-entry:last-child {
  border-bottom: none;
}

.item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0f172a;
}

.item-meta {
  font-size: 0.813rem;
  color: #64748b;
}
</style>
