import { onBeforeUnmount } from 'vue'

/**
 * Wraps an async loader so only the most recent request may touch state.
 *
 * - run():     starts a request immediately (use for the initial load on mount).
 * - trigger(): debounced run() for filter changes. It also invalidates any in-flight
 *              request right away so an older response can never overwrite newer filters.
 * - loading/error refs (optional) belong to the latest request only.
 *
 * Staleness uses a sequence number rather than AbortController because api.js does not
 * thread an axios `signal` through; stale responses are simply ignored.
 *
 * @param {() => Promise<any>} fetcher  returns the data (receives no args; read filters inside)
 * @param {object} options
 * @param {(data: any) => void} options.onData   applies the result (latest request only)
 * @param {(err: Error) => void} [options.onError] called for the latest request's failure
 * @param {import('vue').Ref<boolean>} [options.loading]
 * @param {import('vue').Ref<any>} [options.error]
 * @param {number} [options.delay=250] debounce in ms for trigger()
 */
export function useLatestRequest(fetcher, { onData, onError, loading, error, delay = 250 } = {}) {
  let seq = 0
  let timer = null

  const cancelTimer = () => {
    clearTimeout(timer)
    timer = null
  }

  const run = async () => {
    cancelTimer()
    const id = ++seq
    if (loading) loading.value = true
    if (error) error.value = null
    try {
      const data = await fetcher()
      if (id !== seq) return // a newer request superseded this one
      onData?.(data)
    } catch (err) {
      if (id !== seq) return
      if (onError) onError(err)
      else if (error) error.value = err.message
    } finally {
      if (id === seq && loading) loading.value = false
    }
  }

  const trigger = () => {
    cancelTimer()
    seq++ // discard any in-flight response immediately
    if (loading) loading.value = true
    timer = setTimeout(run, delay)
  }

  onBeforeUnmount(() => {
    cancelTimer()
    seq++ // ignore responses arriving after unmount
  })

  return { run, trigger }
}
