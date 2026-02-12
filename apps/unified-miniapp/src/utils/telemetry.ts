type TelemetryLevel = 'info' | 'warn' | 'error'

interface TelemetryEvent {
  id: string
  type: string
  level: TelemetryLevel
  ts: string
  route: string
  payload: Record<string, any>
}

const STORAGE_KEY = '__rl_telemetry_events__'
const MAX_EVENTS = 120
let cache: TelemetryEvent[] | null = null

function buildId() {
  return `evt_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
}

function currentRoute(): string {
  try {
    const pages = getCurrentPages()
    const current = pages[pages.length - 1] as any
    return current?.route ? `/${current.route}` : ''
  } catch (_) {
    return ''
  }
}

function clipText(input: any, max = 300): string {
  const text = typeof input === 'string' ? input : JSON.stringify(input ?? '')
  return text.length > max ? `${text.slice(0, max)}...` : text
}

function sanitizeValue(value: any, depth = 0): any {
  if (depth > 2) return '[depth-limit]'
  if (value === null || value === undefined) return value
  if (typeof value === 'string') return clipText(value)
  if (typeof value === 'number' || typeof value === 'boolean') return value
  if (Array.isArray(value)) return value.slice(0, 10).map(item => sanitizeValue(item, depth + 1))
  if (typeof value === 'object') {
    const obj: Record<string, any> = {}
    Object.entries(value).slice(0, 20).forEach(([k, v]) => {
      obj[k] = sanitizeValue(v, depth + 1)
    })
    return obj
  }
  return clipText(String(value))
}

function readEvents(): TelemetryEvent[] {
  if (cache) return cache
  try {
    const raw = uni.getStorageSync(STORAGE_KEY)
    cache = Array.isArray(raw) ? raw : []
    return cache
  } catch (_) {
    cache = []
    return cache
  }
}

function writeEvents(next: TelemetryEvent[]) {
  cache = next
  try {
    uni.setStorageSync(STORAGE_KEY, next)
  } catch (_) {
    // Ignore storage failures to avoid affecting user path
  }
}

export function trackEvent(
  type: string,
  payload: Record<string, any> = {},
  level: TelemetryLevel = 'info'
): TelemetryEvent {
  const event: TelemetryEvent = {
    id: buildId(),
    type,
    level,
    ts: new Date().toISOString(),
    route: currentRoute(),
    payload: sanitizeValue(payload)
  }

  const events = readEvents()
  events.push(event)
  if (events.length > MAX_EVENTS) {
    events.splice(0, events.length - MAX_EVENTS)
  }
  writeEvents(events)

  if (level === 'error') {
    console.error('[telemetry]', event.type, event)
  } else if (level === 'warn') {
    console.warn('[telemetry]', event.type, event)
  } else {
    console.info('[telemetry]', event.type, event)
  }

  return event
}

export function trackError(type: string, error: unknown, payload: Record<string, any> = {}) {
  const err = error as any
  trackEvent(
    type,
    {
      ...payload,
      message: err?.message || String(error || ''),
      stack: clipText(err?.stack || '')
    },
    'error'
  )
}

export function getTelemetryEvents() {
  return [...readEvents()]
}

export function clearTelemetryEvents() {
  writeEvents([])
}

