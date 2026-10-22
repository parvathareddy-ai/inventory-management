import { api } from '../api'

// Shared, short-lived cache for GET /api/orders (~110 KB). Dashboard, Orders and Spending all
// need it, so navigating between them within the TTL must not refetch.
//
// - Keyed by the filter params that the endpoint actually accepts ('all'/empty are normalized
//   so {} and {warehouse:'all',...} share one entry).
// - Concurrent callers for the same key share one in-flight promise.
// - Failures are never cached.
// - Returned arrays are frozen (shallow): they are shared between views, so in-place mutation
//   (e.g. Array#sort) would corrupt other consumers. Copy before sorting.
// Stale-response protection stays with useLatestRequest in each view: this store only
// de-duplicates and caches, the caller still ignores superseded results.

const TTL_MS = 60_000
const FILTER_KEYS = ['warehouse', 'category', 'status', 'month']

const cache = new Map() // key -> { data, at }
const inflight = new Map() // key -> Promise
// Bumped by invalidate() so a request started before a write cannot repopulate the cache afterwards
let generation = 0

const keyFor = (filters = {}) =>
  FILTER_KEYS.map(k => (filters[k] && filters[k] !== 'all' ? filters[k] : '')).join('|')

export function getOrders(filters = {}) {
  const key = keyFor(filters)

  const hit = cache.get(key)
  if (hit && Date.now() - hit.at < TTL_MS) return Promise.resolve(hit.data)

  const pending = inflight.get(key)
  if (pending) return pending

  const startedIn = generation
  const promise = api
    .getOrders(filters)
    .then(data => {
      const frozen = Object.freeze(data)
      if (startedIn === generation) cache.set(key, { data: frozen, at: Date.now() })
      return frozen
    })
    .finally(() => {
      if (inflight.get(key) === promise) inflight.delete(key)
    })
  inflight.set(key, promise)
  return promise
}

/** Drop all cached orders (call after any write that changes orders). */
export function invalidateOrders() {
  generation++
  cache.clear()
  inflight.clear()
}

export function useOrdersStore() {
  return { getOrders, invalidate: invalidateOrders }
}
