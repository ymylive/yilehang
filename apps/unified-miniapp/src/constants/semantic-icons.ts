export const SEMANTIC_ICON_FALLBACK_KEY = 'fallback-empty'

export const SEMANTIC_ICON_MAP: Record<string, string> = {
  'fallback-empty': '/static/illustrations/common/common-generic-empty.svg',
  'chat-empty': '/static/illustrations/social/social-chat-empty.svg',
  'messages-empty': '/static/illustrations/social/social-chat-empty.svg',
  'growth-history-empty': '/static/illustrations/growth/growth-record-empty.svg',
  'membership-empty': '/static/illustrations/membership/membership-card-empty.svg',
  'membership-transactions-empty': '/static/illustrations/membership/membership-card-empty.svg',
  'booking-empty': '/static/illustrations/training/training-course-empty.svg',
  'schedule-empty': '/static/illustrations/training/training-course-empty.svg',
  'coach-workbench-empty': '/static/illustrations/coach/coach-workbench-empty.svg',
  'growth-empty': '/static/illustrations/growth/growth-record-empty.svg',
  'admin-notices-empty': '/static/illustrations/admin/admin-analytics-empty.svg',
  'admin-coaches-empty': '/static/illustrations/admin/admin-analytics-empty.svg',
  'home-schedule-empty': '/static/illustrations/training/training-course-empty.svg',
  'user-student-empty': '/static/illustrations/common/common-generic-empty.svg',
  'coach-income-empty': '/static/illustrations/coach/coach-workbench-empty.svg',
  'energy-empty': '/static/illustrations/energy/energy-reward-empty.svg',
  'energy-redeem-empty': '/static/illustrations/energy/energy-reward-empty.svg',
  'energy-orders-empty': '/static/illustrations/energy/energy-reward-empty.svg',
  'icon-energy-bolt': '/static/illustrations/energy/energy-bolt-icon.svg',
  'icon-arrow-up': '/static/illustrations/common/common-arrow-up-icon.svg',
  'icon-arrow-down': '/static/illustrations/common/common-arrow-down-icon.svg',
  'icon-chevron-down': '/static/illustrations/common/common-chevron-down-icon.svg',
  'icon-chevron-right': '/static/illustrations/common/common-chevron-right-icon.svg',
  'icon-growth-chevron-right': '/static/illustrations/growth/growth-chevron-right-icon.svg',
  'icon-star-filled': '/static/illustrations/common/common-star-filled-icon.svg',
  'icon-star-outline': '/static/illustrations/common/common-star-outline-icon.svg',
  'icon-play-filled': '/static/illustrations/media/media-play-filled-icon.svg',
  'moments-empty': '/static/illustrations/media/media-moments-empty.svg',
  'leaderboard-empty': '/static/illustrations/ranking/ranking-leaderboard-empty.svg',
  'admin-analytics-users-empty': '/static/illustrations/admin/admin-analytics-empty.svg',
  'admin-analytics-bookings-empty': '/static/illustrations/admin/admin-analytics-empty.svg',
}

export function getSemanticIcon(key: string): string {
  return SEMANTIC_ICON_MAP[key] ?? SEMANTIC_ICON_MAP[SEMANTIC_ICON_FALLBACK_KEY]
}
