<template>
  <div class="app">
    <AppSidebar
      :brand-name="t('nav.companyName')"
      :brand-subtitle="t('nav.subtitle')"
      :sections="navSections"
      collapse-label="Collapse"
    >
      <template #footer>
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
      </template>
    </AppSidebar>
    <div class="app-main">
      <FilterBar />
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AppSidebar from './components/AppSidebar.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher,
    AppSidebar
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    // Same routes and labels as the old top nav; icons are 24px stroke paths
    const navSections = computed(() => [
      {
        label: 'Operations',
        items: [
          { to: '/', label: t('nav.overview'), icon: 'M3 10.5L12 3l9 7.5V20a1 1 0 01-1 1h-5v-6H9v6H4a1 1 0 01-1-1z' },
          { to: '/inventory', label: t('nav.inventory'), icon: 'M21 8l-9-5-9 5v8l9 5 9-5zM3 8l9 5 9-5M12 13v8' },
          { to: '/orders', label: t('nav.orders'), icon: 'M6 2L3 6v14a1 1 0 001 1h16a1 1 0 001-1V6l-3-4zM3 6h18M16 10a4 4 0 01-8 0' },
          { to: '/restocking', label: t('nav.restocking'), icon: 'M21 12a9 9 0 11-3-6.7M21 4v5h-5' }
        ]
      },
      {
        label: 'Finance & Insights',
        items: [
          { to: '/spending', label: t('nav.finance'), icon: 'M12 2v20M17 6H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6' },
          { to: '/demand', label: t('nav.demandForecast'), icon: 'M3 17l6-6 4 4 8-8M14 7h7v7' },
          { to: '/reports', label: 'Reports', icon: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6M8 13h8M8 17h8' }
        ]
      }
    ])

    onMounted(loadTasks)

    return {
      t,
      navSections,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', var(--font-sans);
  font-size: var(--text-base);
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Sidebar + content shell */
.app {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  min-height: 100vh;
}

/* min-width: 0 stops wide tables from stretching the grid track past the viewport */
.app-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  margin: 0 auto;
  padding: var(--space-8);
}

/* Footer controls inside the sidebar: dark theme, full width, popovers open upward */
.sidebar-footer .language-switcher,
.sidebar-footer .profile-menu { width: 100%; }
.sidebar-footer .language-button,
.sidebar-footer .profile-button {
  width: 100%;
  background: var(--sidebar-item-hover);
  border-color: var(--sidebar-border);
  color: var(--sidebar-text);
}
.sidebar-footer .language-button:hover,
.sidebar-footer .profile-button:hover {
  background: var(--sidebar-item-active);
  border-color: var(--sidebar-border);
}
.sidebar-footer .profile-name,
.sidebar-footer .language-label { color: var(--sidebar-text-active); min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sidebar-footer .chevron { margin-left: auto; }
.sidebar-footer .globe-icon,
.sidebar-footer .chevron { color: var(--sidebar-text); }
.sidebar .sidebar-footer .dropdown-menu {
  top: auto;
  bottom: calc(100% + var(--space-2));
  left: 0;
  right: auto;
}
.sidebar.collapsed .sidebar-footer .profile-name,
.sidebar.collapsed .sidebar-footer .language-label,
.sidebar.collapsed .sidebar-footer .chevron { display: none; }
.sidebar.collapsed .sidebar-footer .language-button,
.sidebar.collapsed .sidebar-footer .profile-button { justify-content: center; padding-inline: 0; }

.page-header { margin-bottom: var(--space-6); }
.page-header h2 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-1);
  letter-spacing: -0.025em;
}
.page-header p { color: var(--color-text-muted); font-size: var(--text-sm); }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-5);
  margin-bottom: var(--space-6);
}
.stat-card {
  background: var(--color-surface);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition), box-shadow var(--transition);
}
.stat-card:hover { border-color: var(--color-border-strong); box-shadow: var(--shadow-md); }
.stat-label {
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-2);
}
.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.025em;
}
.stat-card.warning .stat-value { color: #ea580c; }
.stat-card.success .stat-value { color: #059669; }
.stat-card.danger .stat-value { color: var(--color-danger); }
.stat-card.info .stat-value { color: var(--color-info); }

.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}
.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: -0.025em;
}

.table-container { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
thead {
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
}
th {
  text-align: left;
  padding: var(--space-3) var(--space-4);
  font-weight: 600;
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
td {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid #f1f5f9;
  color: #334155;
  font-size: var(--text-sm);
}
tbody tr { transition: background-color var(--transition); }
tbody tr:hover { background: var(--color-bg); }

.badge {
  display: inline-block;
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
/* Status colors unchanged from the original app */
.badge.success, .badge.increasing { background: #d1fae5; color: #065f46; }
.badge.warning, .badge.medium { background: #fed7aa; color: #92400e; }
.badge.danger, .badge.decreasing, .badge.high { background: #fecaca; color: #991b1b; }
.badge.info, .badge.low { background: #dbeafe; color: #1e40af; }
.badge.stable { background: #e0e7ff; color: #3730a3; }

.loading {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}
.error {
  background: var(--color-danger-soft);
  border: 1px solid #fecaca;
  color: #991b1b;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: var(--space-4) 0;
  font-size: var(--text-sm);
}
</style>
