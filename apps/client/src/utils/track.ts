/**
 * Lightweight tracking utility: console + WeChat analytics
 */
export type TrackPayload = Record<string, any>

export function trackEvent(event: string, payload: TrackPayload = {}) {
  try {
    // WeChat Mini Program analytics (requires event config in console)
    // @ts-ignore
    if (typeof uni !== 'undefined' && uni.reportAnalytics) {
      // @ts-ignore
      uni.reportAnalytics(event, payload)
    }
  } catch (e) {
    // ignore tracking errors
  }

  // H5/dev logs
  // eslint-disable-next-line no-console
  console.log(`[track] ${event}`, payload)
}
