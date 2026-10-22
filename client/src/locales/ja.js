export default {
  // Navigation
  nav: {
    operations: '業務',
    financeInsights: '財務・分析',
    reports: 'レポート',
    primary: 'メインナビゲーション',
    collapse: '折りたたむ',
    overview: '概要',
    inventory: '在庫',
    orders: '注文',
    finance: '財務',
    demandForecast: '需要予測',
    restocking: '補充発注',
    companyName: '触媒コンポーネンツ',
    subtitle: '在庫管理システム'
  },

  // Dashboard
  dashboard: {
    loadError: 'ダッシュボードデータの読み込みに失敗しました',
    title: '概要',
    kpi: {
      title: '主要業績評価指標',
      inventoryTurnover: '在庫回転率',
      ordersFulfilled: '注文履行数',
      orderFillRate: '注文充足率',
      revenue: '収益（注文）',
      revenueYTD: '収益（注文）年初来',
      revenueMTD: '収益（注文）月初来',
      avgProcessingTime: '平均処理時間（日）',
      goal: '目標'
    },
    summary: {
      title: '概要'
    },
    orderHealth: {
      title: '注文状況',
      totalOrders: '総注文数',
      revenue: '収益',
      avgOrderValue: '平均注文額',
      onTimeRate: '定時配達率',
      avgFulfillmentDays: '平均履行日数',
      total: '合計'
    },
    ordersByMonth: {
      title: '月別注文数'
    },
    inventoryValue: {
      title: 'カテゴリ別在庫価値'
    },
    inventoryShortages: {
      title: '在庫不足',
      noShortages: '在庫不足なし - すべての注文を履行できます！',
      noData: '選択したフィルターのデータがありません',
      orderId: '注文ID',
      sku: 'SKU',
      itemName: '品目名',
      quantityNeeded: '必要数量',
      quantityAvailable: '在庫数量',
      shortage: '不足',
      daysDelayed: '遅延日数',
      priority: '優先度',
      actions: '操作',
      unitsShort: '単位不足',
      days: '日'
    },
    purchaseOrder: {
      create: '発注書を作成',
      view: '発注書を表示',
      createTitle: '発注書の作成',
      viewTitle: '発注書の詳細',
      item: '未処理品目',
      order: '注文',
      shortage: '不足',
      supplier: '仕入先名',
      quantity: '数量',
      unitCost: '単価',
      expectedDelivery: '納品予定日',
      notes: '備考（任意）',
      totalCost: '合計金額',
      submit: '発注書を作成',
      submitting: '作成中...',
      cancel: 'キャンセル',
      close: '閉じる',
      poId: '発注書ID',
      status: 'ステータス',
      createdDate: '作成日',
      none: 'この品目の発注書が見つかりません。',
      error: '発注書の作成に失敗しました',
      created: '発注書 {id} を作成しました'
    },
    topProducts: {
      title: '収益別トップ製品',
      sku: 'SKU',
      product: '製品',
      category: 'カテゴリ',
      warehouse: '倉庫',
      stockStatus: '在庫状況',
      revenue: '収益',
      unitsOrdered: '注文数量',
      firstOrder: '初回注文',
      inStock: '在庫あり',
      lowStock: '在庫僅少'
    }
  },

  // Inventory
  inventory: {
    loadError: '在庫の読み込みに失敗しました',
    title: '在庫',
    description: 'すべての在庫品目の追跡と管理',
    stockLevels: '在庫レベル',
    skus: 'SKU',
    searchPlaceholder: '品目名で検索...',
    clearSearch: '検索をクリア',
    exportCsv: 'CSVエクスポート',
    exportCsvTooltip: '現在表示されている行をCSVファイルとしてダウンロード',
    totalItems: '総品目数',
    totalValue: '総価値',
    lowStockItems: '在庫僅少品目',
    warehouses: '倉庫',
    table: {
      sku: 'SKU',
      itemName: '品目名',
      name: '名前',
      category: 'カテゴリ',
      warehouse: '倉庫',
      quantity: '数量',
      quantityOnHand: '手持在庫数',
      reorderPoint: '再注文点',
      unitCost: '単価',
      unitPrice: '単価',
      totalValue: '総価値',
      location: '場所',
      status: 'ステータス'
    }
  },

  // Orders
  orders: {
    loadError: '注文の読み込みに失敗しました',
    title: '注文',
    description: '顧客注文の表示と管理',
    allOrders: 'すべての注文',
    submittedOrders: '送信済み注文',
    noSubmittedOrders: '送信済みの補充発注はまだありません。',
    submittedError: '送信済み注文の読み込みに失敗しました',
    perItemLeadTimes: '品目別リードタイム',
    leadTimeDays: '{days}日',
    submitted: {
      orderId: '注文ID',
      orderDate: '注文日',
      items: '品目',
      total: '合計',
      leadTime: 'リードタイム（日）',
      expectedDelivery: '配達予定日',
      status: 'ステータス',
      sku: 'SKU',
      quantity: '数量',
      supplier: 'サプライヤー'
    },
    totalOrders: '総注文数',
    totalRevenue: '総収益',
    avgOrderValue: '平均注文額',
    onTimeDelivery: '定時配達',
    itemsCount: '{count}件',
    quantity: '数量',
    table: {
      orderNumber: '注文番号',
      orderId: '注文ID',
      orderDate: '注文日',
      date: '日付',
      customer: '顧客',
      category: 'カテゴリ',
      warehouse: '倉庫',
      items: '品目',
      value: '価格',
      totalValue: '合計金額',
      status: 'ステータス',
      expectedDelivery: '予定配達日',
      actualDelivery: '実際の配達日'
    }
  },

  // 補充発注
  restocking: {
    title: '補充発注',
    description: '需要トレンドと在庫不足に基づき、予算内で補充発注を計画します',
    budget: '予算',
    budgetSlider: '補充予算',
    plannedSpend: '計画支出額',
    remainingBudget: '残り予算',
    itemsPlanned: '{count}品目を計画',
    recommendations: '推奨品目',
    placeOrder: '発注する',
    placingOrder: '発注中...',
    emptyState: 'この予算では推奨品目を購入できません。予算を増やすと推奨が表示されます。',
    loadError: '推奨の読み込みに失敗しました',
    orderError: '発注に失敗しました',
    orderPlaced: '発注が完了しました',
    orderConfirmation: '発注 {id} を受け付けました。配達予定日: {date}',
    viewOrders: '送信済み注文を表示',
    table: {
      sku: 'SKU',
      item: '品目',
      trend: 'トレンド',
      supplier: 'サプライヤー',
      quantity: '数量',
      unitCost: '単価',
      lineTotal: '小計',
      leadTime: 'リードタイム（日）'
    }
  },

  // Finance/Spending
  finance: {
    loadError: '財務データの読み込みに失敗しました',
    transactionDetails: '取引の詳細',
    title: '財務ダッシュボード',
    description: '収益、コスト、財務パフォーマンスの追跡',
    totalRevenue: '総収益',
    totalCosts: '総コスト',
    netProfit: '純利益',
    avgOrderValue: '平均注文額',
    fromOrders: '{count}件の注文から',
    costBreakdown: '調達 + 運営 + 人件費 + 間接費',
    margin: 'マージン',
    perOrderRevenue: '注文あたりの収益',
    revenueVsCosts: {
      title: '月別収益対コスト',
      revenue: '収益',
      costs: '総コスト'
    },
    monthlyCostFlow: {
      title: '月別コストフロー',
      procurement: '調達',
      operational: '運営',
      labor: '人件費',
      overhead: '間接費'
    },
    categorySpending: {
      title: 'カテゴリ別支出',
      ofTotal: '全体の'
    },
    transactions: {
      title: '最近の取引',
      id: 'ID',
      description: '説明',
      vendor: 'ベンダー',
      date: '日付',
      amount: '金額'
    }
  },

  // Demand Forecast
  demand: {
    loadError: '需要予測の読み込みに失敗しました',
    title: '需要予測',
    description: '需要動向の分析と将来のニーズの予測',
    increasingDemand: '需要増加',
    stableDemand: '需要安定',
    decreasingDemand: '需要減少',
    itemsCount: '{count}件',
    more: 'さらに...',
    demandForecasts: '需要予測',
    table: {
      sku: 'SKU',
      itemName: '品目名',
      currentDemand: '現在の需要',
      forecastedDemand: '予測需要',
      change: '変化',
      trend: 'トレンド',
      period: '期間'
    }
  },

  // Filters
  filters: {
    resetFilters: 'すべてのフィルターをリセット',
    timePeriod: '期間',
    location: '場所',
    category: 'カテゴリ',
    orderStatus: '注文ステータス',
    all: 'すべて',
    allMonths: 'すべての月'
  },

  // Statuses
  status: {
    delivered: '配達済み',
    shipped: '出荷済み',
    processing: '処理中',
    backordered: 'バックオーダー',
    inStock: '在庫あり',
    lowStock: '在庫僅少',
    adequate: '適量'
  },

  // Trends
  trends: {
    increasing: '増加',
    stable: '安定',
    decreasing: '減少'
  },

  // Priority
  priority: {
    high: '高',
    medium: '中',
    low: '低'
  },

  // Categories
  categories: {
    circuitBoards: '回路基板',
    sensors: 'センサー',
    actuators: 'アクチュエータ',
    controllers: 'コントローラー',
    powerSupplies: '電源'
  },

  // Spending Categories
  spendingCategories: {
    rawMaterials: '原材料',
    components: '部品',
    equipment: '設備',
    consumables: '消耗品'
  },

  // Warehouses
  warehouses: {
    sanFrancisco: 'サンフランシスコ',
    london: 'ロンドン',
    tokyo: '東京'
  },

  // Months
  months: {
    jan: '1月',
    feb: '2月',
    mar: '3月',
    apr: '4月',
    may: '5月',
    jun: '6月',
    jul: '7月',
    aug: '8月',
    sep: '9月',
    oct: '10月',
    nov: '11月',
    dec: '12月',
    january: '1月',
    february: '2月',
    march: '3月',
    april: '4月',
    june: '6月',
    july: '7月',
    august: '8月',
    september: '9月',
    october: '10月',
    november: '11月',
    december: '12月'
  },

  // Profile Menu
  profile: {
    profileDetails: 'プロフィール詳細',
    myTasks: 'マイタスク',
    logout: 'ログアウト',
    logoutNotice: 'このデモではログアウトは利用できません。アクティブなセッションはありません。'
  },

  // Profile Details Modal
  profileDetails: {
    title: 'プロフィール詳細',
    email: 'メールアドレス',
    department: '部署',
    location: '勤務地',
    phone: '電話番号',
    joinDate: '入社日',
    employeeId: '社員ID',
    close: '閉じる'
  },

  // Tasks Modal
  tasks: {
    title: 'マイタスク',
    taskTitle: 'タスク名',
    taskTitlePlaceholder: 'タスク名を入力...',
    priority: '優先度',
    dueDate: '期限',
    addTask: 'タスクを追加',
    noTasks: 'タスクがありません。上記からタスクを追加してください！'
  },

  // Language
  language: {
    english: 'English',
    japanese: '日本語',
    selectLanguage: '言語を選択'
  },

  // レポート
  reports: {
    title: 'パフォーマンスレポート',
    description: '四半期ごとの業績指標と月次トレンドを確認します',
    loadError: 'レポートの読み込みに失敗しました',
    quarterly: {
      title: '四半期パフォーマンス',
      quarter: '四半期',
      totalOrders: '総注文数',
      totalRevenue: '総売上',
      avgOrderValue: '平均注文額',
      fulfillmentRate: '出荷達成率'
    },
    trend: {
      title: '月次売上推移',
      barLabel: '{month}の売上: {amount}'
    },
    monthOverMonth: {
      title: '前月比分析',
      month: '月',
      orders: '注文数',
      revenue: '売上',
      change: '増減',
      growthRate: '成長率'
    },
    stats: {
      totalRevenueYtd: '総売上（年初来）',
      avgMonthlyRevenue: '月平均売上',
      totalOrdersYtd: '総注文数（年初来）',
      bestQuarter: '最高業績の四半期'
    },
    notAvailable: '該当なし'
  },

  // 詳細モーダル
  modals: {
    sku: 'SKU',
    unitsCount: '{count}個',
    daysCount: '{count}日',
    percentOfTotal: '全体の{percent}%',
    notAvailable: '該当なし',
    cost: {
      title: '{month}のコスト内訳',
      totalCosts: '総コスト'
    },
    backlog: {
      title: '在庫不足の詳細',
      priority: '優先度: {priority}',
      shortageAmount: '不足数量',
      daysDelayed: '遅延日数',
      orderId: '注文ID',
      itemSku: '品目SKU',
      quantityNeeded: '必要数量',
      quantityAvailable: '利用可能数量',
      expectedDate: '納品予定日',
      status: 'ステータス'
    },
    product: {
      title: '製品の詳細',
      category: 'カテゴリ',
      warehouse: '倉庫',
      unitsOrdered: '注文数量',
      totalRevenue: '総売上',
      currentStock: '現在の在庫',
      reorderPoint: '再注文点',
      firstOrderDate: '初回注文日',
      stockStatus: '在庫状況'
    },
    inventory: {
      title: '在庫品目の詳細',
      quantityOnHand: '手持ち数量',
      stockLevel: '在庫レベル',
      vsReorderPoint: '再注文点との比較',
      category: 'カテゴリ',
      location: '場所',
      reorderPoint: '再注文点',
      unitsRemaining: '残り数量',
      unitCost: '単価（原価）',
      totalValue: '合計金額',
      warehouse: '倉庫',
      status: 'ステータス'
    }
  },

  // Common
  common: {
    loading: '読み込み中...',
    skipToContent: 'メインコンテンツへスキップ',
    loadError: 'このページの読み込み中に問題が発生しました。',
    retry: '再試行',
    error: 'エラー',
    noData: 'データがありません',
    viewDetails: '詳細を見る',
    viewDetailsFor: '{name} の詳細を見る',
    close: '閉じる',
    save: '保存',
    cancel: 'キャンセル',
    search: '検索',
    filter: 'フィルター',
    export: 'エクスポート',
    items: '件'
  },

  // Product Names
  productNames: {
    'Single Layer PCB Assembly': '単層PCB組立',
    'Dual Layer PCB Assembly': '二層PCB組立',
    'Multi Layer PCB Assembly': '多層PCB組立',
    'Temperature Sensor Module': '温度センサーモジュール',
    'Humidity Sensor Module': '湿度センサーモジュール',
    'Pressure Sensor Module': '圧力センサーモジュール',
    'Proximity Sensor': '近接センサー',
    'Ultrasonic Distance Sensor': '超音波距離センサー',
    'Micro Servo Motor': 'マイクロサーボモータ',
    'Standard Servo Motor': '標準サーボモータ',
    'Stepper Motor NEMA 17': 'ステッピングモータNEMA 17',
    '8-bit Microcontroller': '8ビットマイコン',
    '32-bit ARM Microcontroller': '32ビットARMマイコン',
    'Digital Signal Processor': 'デジタル信号処理装置',
    '3-Axis Accelerometer': '3軸加速度センサー',
    'Gyroscope Module': 'ジャイロスコープモジュール',
    'Light Dependent Resistor': '光依存抵抗器',
    'Coil Spring Heavy Duty': 'コイルばね(重量用)',
    'Compression Spring': '圧縮ばね',
    'PWM Motor Controller': 'PWMモータコントローラ',
    'H-Bridge Motor Driver': 'Hブリッジモータドライバ',
    'Stepper Motor NEMA 23': 'ステッピングモータNEMA 23',
    'Drive Pulley': 'ドライブプーリー',
    'LED Driver IC': 'LEDドライバIC',
    '5V 10A Switching Power Supply': '5V 10Aスイッチング電源',
    '12V 5A Power Supply Module': '12V 5A電源モジュール',
    '24V 3A Industrial Power Supply': '24V 3A産業用電源',
    'Dual Output ±15V Power Supply': 'デュアル出力±15V電源',
    '48V DC Power Supply Unit': '48V DC電源ユニット',
    'USB-C PD 100W Power Supply': 'USB-C PD 100W電源',
    'Battery Backup Power Supply': 'バッテリバックアップ電源',
    'Adjustable Bench Power Supply': '可変ベンチ電源'
  },

  // Customer Names
  customerNames: {
    'MegaCorp Industries': 'メガコープ工業',
    'Elite Systems Corp': 'エリートシステムズ',
    'Horizon Technologies': 'ホライズン技術',
    'FastAssembly Ltd': 'ファストアセンブリー',
    'TechSolutions Group': 'テックソリューションズグループ',
    'Apex Engineering': 'アペックスエンジニアリング',
    'Superior Manufacturing': 'スーペリアマニュファクチャリング',
    'Cascade Manufacturing': 'カスケードマニュファクチャリング',
    'Acme Manufacturing Corp': 'アクメ製造',
    'TechBuild Industries': 'テックビルド工業',
    'Advanced Components Inc': 'アドバンストコンポーネンツ',
    'Premier Industries': 'プレミア工業',
    'Stellar Components Ltd': 'ステラコンポーネンツ',
    'Dynamic Systems Ltd': 'ダイナミックシステムズ'
  }
}
