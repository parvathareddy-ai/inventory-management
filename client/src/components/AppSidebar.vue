<!--
  Template sidebar. Adapt before use:
  - Replace `sections` with the app's real routes and its real label source (i18n keys, not literals).
  - Move the old header's controls (profile menu, language switcher, ...) into the footer slot.
  - Keep the icons as inline SVG using currentColor; no icon library, no emoji.
-->
<template>
  <aside class="sidebar" :class="{ collapsed }" :aria-label="navLabel">
    <div class="sidebar-brand">
      <span class="brand-mark" aria-hidden="true">{{ brandInitial }}</span>
      <span class="brand-text">
        <strong>{{ brandName }}</strong>
        <small v-if="brandSubtitle">{{ brandSubtitle }}</small>
      </span>
    </div>

    <nav class="sidebar-nav">
      <div v-for="section in sections" :key="section.label" class="nav-section">
        <p class="nav-section-label">{{ section.label }}</p>
        <router-link
          v-for="item in section.items"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :title="collapsed ? item.label : null"
          :aria-label="collapsed ? item.label : null"
        >
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path :d="item.icon" />
          </svg>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" />
      <!-- Hidden on narrow screens, where icons-only mode is forced and the toggle would do nothing -->
      <button v-if="!isNarrow" type="button" class="collapse-toggle" :aria-pressed="collapsed" @click="toggle">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M15 6l-6 6 6 6" />
        </svg>
        <span class="nav-label">{{ collapseLabel }}</span>
      </button>
    </div>
  </aside>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'
// At or below this width the sidebar is always icons-only; a full-width sidebar would
// leave too little room for the page content
const NARROW_QUERY = '(max-width: 900px)'

export default {
  name: 'AppSidebar',
  props: {
    brandName: { type: String, required: true },
    brandSubtitle: { type: String, default: '' },
    // [{ label: 'Operations', items: [{ to: '/', label: 'Overview', icon: 'M3 12l9-9 9 9...' }] }]
    sections: { type: Array, required: true },
    collapseLabel: { type: String, default: 'Collapse' },
    navLabel: { type: String, default: 'Primary' }
  },
  emits: ['update:collapsed'],
  setup(props, { emit }) {
    // localStorage can throw (private mode, blocked storage), so the sidebar must work without it
    const readStored = () => {
      try { return localStorage.getItem(STORAGE_KEY) === '1' } catch { return false }
    }
    // The user's own choice is stored separately from the screen-size override, so shrinking
    // the window never overwrites their preference for wide screens
    const userCollapsed = ref(readStored())
    const isNarrow = ref(false)
    const collapsed = computed(() => isNarrow.value || userCollapsed.value)

    watch(userCollapsed, (value) => {
      try { localStorage.setItem(STORAGE_KEY, value ? '1' : '0') } catch { /* ignore */ }
    })
    watch(collapsed, (value) => emit('update:collapsed', value), { immediate: true })

    let mediaQuery = null
    const syncNarrow = (event) => { isNarrow.value = event.matches }
    onMounted(() => {
      mediaQuery = window.matchMedia(NARROW_QUERY)
      isNarrow.value = mediaQuery.matches
      mediaQuery.addEventListener('change', syncNarrow)
    })
    onBeforeUnmount(() => mediaQuery?.removeEventListener('change', syncNarrow))

    const toggle = () => { userCollapsed.value = !userCollapsed.value }
    const brandInitial = computed(() => props.brandName.trim().charAt(0).toUpperCase())

    return { collapsed, isNarrow, toggle, brandInitial }
  }
}
</script>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  border-right: 1px solid var(--sidebar-border);
  transition: width var(--transition);
  /* No overflow:hidden here: footer popovers (profile, language) open outside the sidebar.
     z-index sits above the sticky filter bar (90) so those popovers are not covered. */
  overflow: visible;
  z-index: 100;
}
.sidebar.collapsed { width: var(--sidebar-width-collapsed); }

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-5) var(--space-4);
  border-bottom: 1px solid var(--sidebar-border);
  min-height: 72px;
  overflow: hidden;
}
.brand-mark {
  flex: none;
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: #fff;
  font-weight: 700;
}
.brand-text { display: flex; flex-direction: column; min-width: 0; line-height: 1.2; }
/* Long product names or subtitles are truncated instead of running into the sidebar edge */
.brand-text strong,
.brand-text small { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.brand-text strong { color: var(--sidebar-text-active); font-size: var(--text-sm); }
.brand-text small { color: var(--sidebar-text-subtle); font-size: var(--text-xs); }

.sidebar-nav { flex: 1; overflow-y: auto; overflow-x: hidden; padding: var(--space-4) var(--space-3); }
.nav-section + .nav-section { margin-top: var(--space-5); }
.nav-section-label {
  margin: 0 0 var(--space-2);
  padding: 0 var(--space-3);
  font-size: var(--text-xs);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--sidebar-text-subtle);
  white-space: nowrap;
}

.nav-link,
.collapse-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: inherit;
  font: inherit;
  font-size: var(--text-sm);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: background var(--transition), color var(--transition);
}
.nav-link + .nav-link { margin-top: var(--space-1); }
.nav-link { position: relative; }
.nav-link.router-link-active::before,
.nav-link[href="/"].router-link-exact-active::before {
  content: '';
  position: absolute;
  left: calc(-1 * var(--space-3));
  top: var(--space-2);
  bottom: var(--space-2);
  width: 3px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  background: var(--color-accent);
}
.nav-link[href="/"]:not(.router-link-exact-active)::before { display: none; }
.nav-link:hover,
.collapse-toggle:hover { background: var(--sidebar-item-hover); color: var(--sidebar-text-active); }
.nav-link:focus-visible,
/* Lighter blue than the page accent: #2563eb is only ~3.6:1 on the dark sidebar */
.collapse-toggle:focus-visible { outline: 2px solid #93c5fd; outline-offset: 2px; }
.nav-link.router-link-active { background: var(--sidebar-item-active); color: var(--sidebar-text-active); }
/* The exact-match check stops "/" from staying active on every route */
.nav-link[href="/"]:not(.router-link-exact-active) { background: transparent; color: inherit; }
.nav-link[href="/"].router-link-exact-active { background: var(--sidebar-item-active); color: var(--sidebar-text-active); }

.nav-icon { flex: none; width: 20px; height: 20px; }
.nav-label { white-space: nowrap; }

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-border);
}
.collapse-toggle .nav-icon { transition: transform var(--transition); }

.sidebar.collapsed .brand-text,
.sidebar.collapsed .nav-label,
.sidebar.collapsed .nav-section-label { display: none; }
.sidebar.collapsed .nav-link,
.sidebar.collapsed .collapse-toggle { justify-content: center; padding-inline: 0; }
.sidebar.collapsed .collapse-toggle .nav-icon { transform: rotate(180deg); }
</style>
