const zh = {
  // Header
  "app.title": "出行决策 Agent",
  "app.subtitle": "位置 + 品牌偏好 → 附近商场推荐 · 运行在 EdgeOne Makers",

  // Empty state
  "empty.title": "出行决策 Agent",
  "empty.hint": "告诉我你在哪儿、想逛哪些品牌或门店，我会用地图检索附近的商场，核对门店匹配情况、比较距离，再给你带数据依据的推荐。地点与距离均以地图工具返回为准。",
  "empty.features": "高德地图检索 · 会话记忆 · Agent Tools",

  // Chat input
  "chat.placeholder": "说说你的位置和想找的品牌…  ⏎ 发送 · Shift+⏎ 换行",
  "chat.hint": "由 OpenAI Agents SDK + EdgeOne Makers 驱动 · 地点与距离以地图工具返回为准",

  // Preset questions
  "preset.1": "我在红莲南路地铁站附近，我想要去一个既有倍轻松又有西厅村屋的离得近的商场，帮我推荐。",
  "preset.2": "如果不要求两个品牌同时存在，还有没有距离更近的选择？",

  // Tool indicators
  "tool.geocode": "位置解析",
  "tool.malls": "附近商场",
  "tool.brands": "品牌核对",
  "tool.distance": "距离计算",

  // Status & errors
  "status.error": "⚠️ 请求失败，请检查后端服务是否启动。",
  "status.stopped": "⏹ *已停止生成*",
  "status.backendError": "⚠️ 后端中断请求失败，服务端可能仍在运行。",

  // Debug panel
  "debug.title": "传输流",
  "debug.events": "事件",
  "debug.clear": "清除",
  "debug.empty": "等待 SSE 事件...",
  "debug.emptyHint": "发送消息后，所有原始后端数据将在此处显示。",

  // Conversation sidebar
  "sidebar.label": "会话列表",
  "sidebar.title": "会话",
  "sidebar.newChat": "新建聊天",
  "sidebar.loading": "正在加载会话...",
  "sidebar.loadMore": "加载更多",
  "sidebar.loadingMore": "加载中...",
  "sidebar.emptyTitle": "暂无会话",
  "sidebar.emptyHint": "点击「新建聊天」开始第一段对话。",
  "sidebar.delete": "删除会话",
  "sidebar.deleteConfirm": "确定要永久删除这个会话吗？此操作不可恢复。",

  // Aria labels (button hover/screen-reader)
  "aria.send": "发送",
  "aria.clearHistory": "清除历史",
  "aria.stopGeneration": "停止生成",

  // Language toggle
  "lang.switch": "English",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "一键部署",
  "floatingLink.github": "GitHub",
} as const;

export default zh;
