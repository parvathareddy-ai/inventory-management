export default {
  // Navigation
  nav: {
    operations: 'Operations',
    financeInsights: 'Finance & Insights',
    reports: 'Reports',
    primary: 'Primary',
    collapse: 'Collapse',
    overview: 'Overview',
    inventory: 'Inventory',
    orders: 'Orders',
    finance: 'Finance',
    demandForecast: 'Demand Forecast',
    restocking: 'Restocking',
    companyName: 'Catalyst Components',
    subtitle: 'Inventory Management System'
  },

  // Dashboard
  dashboard: {
    loadError: 'Failed to load dashboard data',
    title: 'Overview',
    kpi: {
      title: 'Key Performance Indicators',
      inventoryTurnover: 'Inventory Turnover Rate',
      ordersFulfilled: 'Orders Fulfilled',
      orderFillRate: 'Order Fill Rate',
      revenue: 'Revenue (Orders)',
      revenueYTD: 'Revenue (Orders) YTD',
      revenueMTD: 'Revenue (Orders) MTD',
      avgProcessingTime: 'Avg Processing Time (Days)',
      goal: 'Goal'
    },
    summary: {
      title: 'Summary'
    },
    orderHealth: {
      title: 'Order Health',
      totalOrders: 'Total Orders',
      revenue: 'Revenue',
      avgOrderValue: 'Avg Order Value',
      onTimeRate: 'On-Time Rate',
      avgFulfillmentDays: 'Avg Fulfillment (Days)',
      total: 'Total'
    },
    ordersByMonth: {
      title: 'Orders by Month'
    },
    inventoryValue: {
      title: 'Inventory Value by Category'
    },
    inventoryShortages: {
      title: 'Inventory Shortages',
      noShortages: 'No inventory shortages - all orders can be fulfilled!',
      noData: 'No inventory data for selected filters',
      orderId: 'Order ID',
      sku: 'SKU',
      itemName: 'Item Name',
      quantityNeeded: 'Quantity Needed',
      quantityAvailable: 'Quantity Available',
      shortage: 'Shortage',
      daysDelayed: 'Days Delayed',
      priority: 'Priority',
      actions: 'Actions',
      unitsShort: 'units short',
      days: 'days'
    },
    purchaseOrder: {
      create: 'Create PO',
      view: 'View PO',
      createTitle: 'Create Purchase Order',
      viewTitle: 'Purchase Order Details',
      item: 'Backlog Item',
      order: 'Order',
      shortage: 'Shortage',
      supplier: 'Supplier Name',
      quantity: 'Quantity',
      unitCost: 'Unit Cost',
      expectedDelivery: 'Expected Delivery Date',
      notes: 'Notes (optional)',
      totalCost: 'Total Cost',
      submit: 'Create Purchase Order',
      submitting: 'Creating...',
      cancel: 'Cancel',
      close: 'Close',
      poId: 'PO ID',
      status: 'Status',
      createdDate: 'Created Date',
      none: 'No purchase order found for this item.',
      error: 'Failed to create purchase order',
      created: 'Purchase order {id} created'
    },
    topProducts: {
      title: 'Top Products by Revenue',
      sku: 'SKU',
      product: 'Product',
      category: 'Category',
      warehouse: 'Warehouse',
      stockStatus: 'Stock Status',
      revenue: 'Revenue',
      unitsOrdered: 'Units Ordered',
      firstOrder: 'First Order',
      inStock: 'In Stock',
      lowStock: 'Low Stock'
    }
  },

  // Inventory
  inventory: {
    loadError: 'Failed to load inventory',
    title: 'Inventory',
    description: 'Track and manage all inventory items',
    stockLevels: 'Stock Levels',
    skus: 'SKUs',
    searchPlaceholder: 'Search by item name...',
    clearSearch: 'Clear search',
    exportCsv: 'Export CSV',
    exportCsvTooltip: 'Download the rows currently shown as a CSV file',
    totalItems: 'Total Items',
    totalValue: 'Total Value',
    lowStockItems: 'Low Stock Items',
    warehouses: 'Warehouses',
    table: {
      sku: 'SKU',
      itemName: 'Item Name',
      name: 'Name',
      category: 'Category',
      warehouse: 'Warehouse',
      quantity: 'Quantity',
      quantityOnHand: 'Quantity on Hand',
      reorderPoint: 'Reorder Point',
      unitCost: 'Unit Cost',
      unitPrice: 'Unit Price',
      totalValue: 'Total Value',
      location: 'Location',
      status: 'Status'
    }
  },

  // Orders
  orders: {
    loadError: 'Failed to load orders',
    title: 'Orders',
    description: 'View and manage customer orders',
    allOrders: 'All Orders',
    submittedOrders: 'Submitted Orders',
    noSubmittedOrders: 'No restocking orders have been submitted yet.',
    submittedError: 'Failed to load submitted orders',
    perItemLeadTimes: 'Per-item lead times',
    leadTimeDays: '{days} days',
    submitted: {
      orderId: 'Order ID',
      orderDate: 'Order Date',
      items: 'Items',
      total: 'Total',
      leadTime: 'Lead Time (days)',
      expectedDelivery: 'Expected Delivery',
      status: 'Status',
      sku: 'SKU',
      quantity: 'Qty',
      supplier: 'Supplier'
    },
    totalOrders: 'Total Orders',
    totalRevenue: 'Total Revenue',
    avgOrderValue: 'Avg Order Value',
    onTimeDelivery: 'On-Time Delivery',
    itemsCount: '{count} items',
    quantity: 'Qty',
    table: {
      orderNumber: 'Order Number',
      orderId: 'Order ID',
      orderDate: 'Order Date',
      date: 'Date',
      customer: 'Customer',
      category: 'Category',
      warehouse: 'Warehouse',
      items: 'Items',
      value: 'Value',
      totalValue: 'Total Value',
      status: 'Status',
      expectedDelivery: 'Expected Delivery',
      actualDelivery: 'Actual Delivery'
    }
  },

  // Restocking
  restocking: {
    title: 'Restocking',
    description: 'Plan a restocking order within your budget based on demand trends and stock shortfalls',
    budget: 'Budget',
    budgetSlider: 'Restocking budget',
    plannedSpend: 'Planned Spend',
    remainingBudget: 'Remaining Budget',
    itemsPlanned: '{count} items planned',
    recommendations: 'Recommended Items',
    placeOrder: 'Place Order',
    placingOrder: 'Placing Order...',
    emptyState: 'This budget does not cover any recommended items. Increase the budget to see recommendations.',
    loadError: 'Failed to load recommendations',
    orderError: 'Failed to place order',
    orderPlaced: 'Order placed',
    orderConfirmation: 'Order {id} was placed. Expected delivery: {date}.',
    viewOrders: 'View submitted orders',
    table: {
      sku: 'SKU',
      item: 'Item',
      trend: 'Trend',
      supplier: 'Supplier',
      quantity: 'Quantity',
      unitCost: 'Unit Cost',
      lineTotal: 'Line Total',
      leadTime: 'Lead Time (days)'
    }
  },

  // Finance/Spending
  finance: {
    loadError: 'Failed to load financial data',
    transactionDetails: 'Transaction Details',
    title: 'Finance Dashboard',
    description: 'Track revenue, costs, and financial performance',
    totalRevenue: 'Total Revenue',
    totalCosts: 'Total Costs',
    netProfit: 'Net Profit',
    avgOrderValue: 'Avg Order Value',
    fromOrders: 'From {count} orders',
    costBreakdown: 'Procurement + Operational + Labor + Overhead',
    margin: 'margin',
    perOrderRevenue: 'Per order revenue',
    revenueVsCosts: {
      title: 'Monthly Revenue vs Costs',
      revenue: 'Revenue',
      costs: 'Total Costs'
    },
    monthlyCostFlow: {
      title: 'Monthly Cost Flow',
      procurement: 'Procurement',
      operational: 'Operational',
      labor: 'Labor',
      overhead: 'Overhead'
    },
    categorySpending: {
      title: 'Spending by Category',
      ofTotal: 'of total'
    },
    transactions: {
      title: 'Recent Transactions',
      id: 'ID',
      description: 'Description',
      vendor: 'Vendor',
      date: 'Date',
      amount: 'Amount'
    }
  },

  // Demand Forecast
  demand: {
    loadError: 'Failed to load demand forecasts',
    title: 'Demand Forecast',
    description: 'Analyze demand trends and forecasts',
    increasingDemand: 'Increasing Demand',
    stableDemand: 'Stable Demand',
    decreasingDemand: 'Decreasing Demand',
    itemsCount: '{count} items',
    more: 'more...',
    demandForecasts: 'Demand Forecasts',
    table: {
      sku: 'SKU',
      itemName: 'Item Name',
      currentDemand: 'Current Demand',
      forecastedDemand: 'Forecasted Demand',
      change: 'Change',
      trend: 'Trend',
      period: 'Period'
    }
  },

  // Filters
  filters: {
    resetFilters: 'Reset all filters',
    timePeriod: 'Time Period',
    location: 'Location',
    category: 'Category',
    orderStatus: 'Order Status',
    all: 'All',
    allMonths: 'All Months'
  },

  // Statuses
  status: {
    delivered: 'Delivered',
    shipped: 'Shipped',
    processing: 'Processing',
    backordered: 'Backordered',
    inStock: 'In Stock',
    lowStock: 'Low Stock',
    adequate: 'Adequate'
  },

  // Trends
  trends: {
    increasing: 'increasing',
    stable: 'stable',
    decreasing: 'decreasing'
  },

  // Priority
  priority: {
    high: 'High',
    medium: 'Medium',
    low: 'Low'
  },

  // Categories
  categories: {
    circuitBoards: 'Circuit Boards',
    sensors: 'Sensors',
    actuators: 'Actuators',
    controllers: 'Controllers',
    powerSupplies: 'Power Supplies'
  },

  // Spending Categories
  spendingCategories: {
    rawMaterials: 'Raw Materials',
    components: 'Components',
    equipment: 'Equipment',
    consumables: 'Consumables'
  },

  // Warehouses
  warehouses: {
    sanFrancisco: 'San Francisco',
    london: 'London',
    tokyo: 'Tokyo'
  },

  // Months
  months: {
    jan: 'Jan',
    feb: 'Feb',
    mar: 'Mar',
    apr: 'Apr',
    may: 'May',
    jun: 'Jun',
    jul: 'Jul',
    aug: 'Aug',
    sep: 'Sep',
    oct: 'Oct',
    nov: 'Nov',
    dec: 'Dec',
    january: 'January',
    february: 'February',
    march: 'March',
    april: 'April',
    june: 'June',
    july: 'July',
    august: 'August',
    september: 'September',
    october: 'October',
    november: 'November',
    december: 'December'
  },

  // Profile Menu
  profile: {
    profileDetails: 'Profile Details',
    myTasks: 'My Tasks',
    logout: 'Logout',
    logoutNotice: 'Logout is not available in this demo; no session is active.'
  },

  // Profile Details Modal
  profileDetails: {
    title: 'Profile Details',
    email: 'Email',
    department: 'Department',
    location: 'Location',
    phone: 'Phone',
    joinDate: 'Join Date',
    employeeId: 'Employee ID',
    close: 'Close'
  },

  // Tasks Modal
  tasks: {
    title: 'My Tasks',
    taskTitle: 'Task Title',
    taskTitlePlaceholder: 'Enter task title...',
    priority: 'Priority',
    dueDate: 'Due Date',
    addTask: 'Add Task',
    noTasks: 'No tasks yet. Add your first task above!'
  },

  // Language
  language: {
    english: 'English',
    japanese: 'Japanese',
    selectLanguage: 'Select Language'
  },

  // Reports
  reports: {
    title: 'Performance Reports',
    description: 'View quarterly performance metrics and monthly trends',
    loadError: 'Failed to load reports',
    quarterly: {
      title: 'Quarterly Performance',
      quarter: 'Quarter',
      totalOrders: 'Total Orders',
      totalRevenue: 'Total Revenue',
      avgOrderValue: 'Avg Order Value',
      fulfillmentRate: 'Fulfillment Rate'
    },
    trend: {
      title: 'Monthly Revenue Trend',
      barLabel: 'Revenue for {month}: {amount}'
    },
    monthOverMonth: {
      title: 'Month-over-Month Analysis',
      month: 'Month',
      orders: 'Orders',
      revenue: 'Revenue',
      change: 'Change',
      growthRate: 'Growth Rate'
    },
    stats: {
      totalRevenueYtd: 'Total Revenue (YTD)',
      avgMonthlyRevenue: 'Avg Monthly Revenue',
      totalOrdersYtd: 'Total Orders (YTD)',
      bestQuarter: 'Best Performing Quarter'
    },
    notAvailable: 'N/A'
  },

  // Detail modals
  modals: {
    sku: 'SKU',
    unitsCount: '{count} units',
    daysCount: '{count} days',
    percentOfTotal: '{percent}% of total',
    notAvailable: 'N/A',
    cost: {
      title: '{month} Cost Breakdown',
      totalCosts: 'Total Costs'
    },
    backlog: {
      title: 'Inventory Shortage Details',
      priority: '{priority} Priority',
      shortageAmount: 'Shortage Amount',
      daysDelayed: 'Days Delayed',
      orderId: 'Order ID',
      itemSku: 'Item SKU',
      quantityNeeded: 'Quantity Needed',
      quantityAvailable: 'Quantity Available',
      expectedDate: 'Expected Date',
      status: 'Status'
    },
    product: {
      title: 'Product Details',
      category: 'Category',
      warehouse: 'Warehouse',
      unitsOrdered: 'Units Ordered',
      totalRevenue: 'Total Revenue',
      currentStock: 'Current Stock',
      reorderPoint: 'Reorder Point',
      firstOrderDate: 'First Order Date',
      stockStatus: 'Stock Status'
    },
    inventory: {
      title: 'Inventory Item Details',
      quantityOnHand: 'Quantity on Hand',
      stockLevel: 'Stock Level',
      vsReorderPoint: 'vs. reorder point',
      category: 'Category',
      location: 'Location',
      reorderPoint: 'Reorder Point',
      unitsRemaining: 'Units Remaining',
      unitCost: 'Unit Cost',
      totalValue: 'Total Value',
      warehouse: 'Warehouse',
      status: 'Status'
    }
  },

  // Common
  common: {
    loading: 'Loading...',
    skipToContent: 'Skip to main content',
    loadError: 'Something went wrong while loading this page.',
    retry: 'Retry',
    error: 'Error',
    noData: 'No data available',
    viewDetails: 'View Details',
    viewDetailsFor: 'View details for {name}',
    close: 'Close',
    save: 'Save',
    cancel: 'Cancel',
    search: 'Search',
    filter: 'Filter',
    export: 'Export',
    items: 'items'
  }
}
