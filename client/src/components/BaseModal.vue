<template>
  <Teleport to="body">
    <Transition name="modal">
      <!-- v-if: nothing is mounted (and no listeners are attached) while closed -->
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <div
          ref="dialogRef"
          class="modal-container"
          :class="`size-${size}`"
          :style="width ? { maxWidth: width } : null"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          tabindex="-1"
        >
          <div class="modal-header">
            <slot name="header" :title-id="titleId">
              <h3 :id="titleId" class="modal-title">{{ title }}</h3>
            </slot>
            <button
              class="close-button"
              type="button"
              :aria-label="t('common.close')"
              @click="close"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div ref="bodyRef" class="modal-body">
            <slot />
          </div>

          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
// Module-level state shared by all instances
let uid = 0
let scrollLocks = 0
let savedOverflow = ''

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), ' +
  'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
</script>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useI18n } from '../composables/useI18n'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  title: { type: String, default: '' },
  // sm = 600px, md = 700px, lg = 900px; `width` (any CSS length) overrides
  size: { type: String, default: 'md', validator: (v) => ['sm', 'md', 'lg'].includes(v) },
  width: { type: String, default: '' }
})

const emit = defineEmits(['close'])

const { t } = useI18n()
const titleId = `base-modal-title-${++uid}`
const dialogRef = ref(null)
const bodyRef = ref(null)

let previouslyFocused = null
let active = false

const close = () => emit('close')

// Visible, enabled focusable elements inside the dialog
const getFocusable = () => {
  if (!dialogRef.value) return []
  return Array.from(dialogRef.value.querySelectorAll(FOCUSABLE)).filter(
    (el) => el.getClientRects().length > 0
  )
}

const onKeydown = (e) => {
  if (e.key === 'Escape') {
    e.preventDefault()
    close()
    return
  }
  if (e.key !== 'Tab') return

  const items = getFocusable()
  if (items.length === 0) {
    e.preventDefault()
    dialogRef.value?.focus()
    return
  }
  const first = items[0]
  const last = items[items.length - 1]
  const current = document.activeElement
  const inside = dialogRef.value?.contains(current)

  // Wrap at the edges, and pull focus back in if it somehow escaped
  if (e.shiftKey && (current === first || current === dialogRef.value || !inside)) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && (current === last || !inside)) {
    e.preventDefault()
    first.focus()
  }
}

const lockScroll = () => {
  if (scrollLocks++ === 0) {
    savedOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
  }
}

const unlockScroll = () => {
  if (scrollLocks > 0 && --scrollLocks === 0) {
    document.body.style.overflow = savedOverflow
  }
}

const activate = async () => {
  if (active) return
  active = true
  previouslyFocused = document.activeElement
  lockScroll()
  document.addEventListener('keydown', onKeydown)
  await nextTick()
  if (!active) return
  // Prefer the first control in the content; fall back to close button, then the container
  const target =
    Array.from(bodyRef.value?.querySelectorAll(FOCUSABLE) ?? []).find(
      (el) => el.getClientRects().length > 0
    ) || getFocusable()[0] || dialogRef.value
  target?.focus()
}

const deactivate = () => {
  if (!active) return
  active = false
  document.removeEventListener('keydown', onKeydown)
  unlockScroll()
  const el = previouslyFocused
  previouslyFocused = null
  if (el && typeof el.focus === 'function' && document.contains(el)) el.focus()
}

watch(() => props.isOpen, (open) => (open ? activate() : deactivate()), { immediate: true })

onBeforeUnmount(deactivate)
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
  max-width: 700px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-container:focus {
  outline: none;
}

.modal-container.size-sm {
  max-width: 600px;
}

.modal-container.size-lg {
  max-width: 900px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border, #e2e8f0);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text, #0f172a);
  letter-spacing: -0.025em;
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: var(--color-text-muted, #64748b);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.close-button:hover {
  background: #f1f5f9;
  color: var(--color-text, #0f172a);
}

.close-button:focus-visible {
  outline: 2px solid var(--color-accent, #2563eb);
  outline-offset: 2px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.size-sm .modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border, #e2e8f0);
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.size-sm .modal-footer {
  padding: 1.25rem 1.5rem;
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
