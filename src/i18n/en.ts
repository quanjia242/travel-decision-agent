const en = {
  // Header
  "app.title": "Travel Decision Agent",
  "app.subtitle": "Location + brand preferences → nearby mall recommendations · on EdgeOne Makers",

  // Empty state
  "empty.title": "Travel Decision Agent",
  "empty.hint": "Tell me where you are and which brands or stores you want. I'll search nearby malls, verify which stores are present, compare distances, and recommend with real data. All locations and distances come from map tools.",
  "empty.features": "AMap Search · Session Memory · Agent Tools",

  // Chat input
  "chat.placeholder": "Where are you, and what brands are you looking for...  ⏎ Send · Shift+⏎ Newline",
  "chat.hint": "Powered by OpenAI Agents SDK + EdgeOne Makers · locations & distances come from map tools",

  // Preset questions
  "preset.1": "I'm near Honglian South Road subway station. Recommend the nearest mall that has both Beqingsong and Xiting Cunwu.",
  "preset.2": "If both brands don't have to be in the same mall, is there a closer option?",

  // Tool indicators
  "tool.geocode": "Geocode",
  "tool.malls": "Nearby Malls",
  "tool.brands": "Brand Check",
  "tool.distance": "Distance",

  // Status & errors
  "status.error": "Request failed. Please check if the backend service is running.",
  "status.stopped": "⏹ *Generation stopped*",
  "status.backendError": "Backend abort request failed. The server may still be running.",

  // Debug panel
  "debug.title": "Trace",
  "debug.events": "events",
  "debug.clear": "Clear",
  "debug.empty": "Waiting for SSE events...",
  "debug.emptyHint": "After sending a message, all raw backend data will be displayed here.",

  // Conversation sidebar
  "sidebar.label": "Conversation list",
  "sidebar.title": "Chats",
  "sidebar.newChat": "New chat",
  "sidebar.loading": "Loading conversations...",
  "sidebar.loadMore": "Load more",
  "sidebar.loadingMore": "Loading...",
  "sidebar.emptyTitle": "No conversations yet",
  "sidebar.emptyHint": "Click \"New chat\" to start your first conversation.",
  "sidebar.delete": "Delete conversation",
  "sidebar.deleteConfirm": "Permanently delete this conversation? This cannot be undone.",

  // Aria labels (button hover/screen-reader)
  "aria.send": "Send",
  "aria.clearHistory": "Clear history",
  "aria.stopGeneration": "Stop generation",

  // Language toggle
  "lang.switch": "中文",

  // ─── Floating bottom-right action badges ─────────────────────────────
  "floatingLink.deploy": "Deploy",
  "floatingLink.github": "GitHub",
} as const;

export default en;
