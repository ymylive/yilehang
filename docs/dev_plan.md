# Yilehang Development Plan

Last updated: 2026-02-06

## 1. Planning Assumptions

- Product focus remains WeChat mini program first (student + coach), admin web second.
- Current production baseline exists (Docker + HTTPS + domain already online).
- Team priority is delivery speed with controlled technical debt.

## 2. Product Milestones

## Milestone M1: Internal Operations Stable (Week 1-3)

Scope:

- Student booking / cancel / reschedule end-to-end
- Coach availability, schedule completion, feedback write-back
- Membership consumption consistency

Deliverables:

- Unified API contract document (request/response/error)
- Booking conflict and quota checks fully covered
- Baseline regression checklist for student/coach critical paths

Acceptance criteria:

- Booking lifecycle succeeds with >= 98% success in internal test runs
- No manual database intervention needed for lesson consumption fixes

## Milestone M2: External Growth Entry (Week 4-6)

Scope:

- Mini program marketing homepage
- Trial signup + one-click consultation
- Basic campaign tooling (coupon, referral code)
- Conversion analytics events

Deliverables:

- Funnel dashboard: visit -> signup -> booked -> paid
- Marketing config table for banners / CTA / campaign windows

Acceptance criteria:

- Trial conversion funnel is measurable in dashboard
- Event loss rate < 3% on core funnel events

## Milestone M3: Ops Intelligence (Week 7-9)

Scope:

- Owner/ops dashboard for attendance, renewal, revenue, coach utilization
- Risk warnings for low attendance/churn/schedule anomalies
- Ops follow-up workflow fields

Deliverables:

- Daily, weekly, monthly KPI cards + trend charts
- Risk queue with reason tags and follow-up status

Acceptance criteria:

- Weekly ops meeting can rely on dashboard without manual spreadsheet merge
- Risk queue supports assignment and closure tracking

## Milestone M4: AI Sports MVP (Week 10-12)

Scope:

- Jump-rope action recognition service integration
- AI training and diet advice endpoint
- AI analysis history linked to student profile

Deliverables:

- `POST /api/v1/ai/jump-rope/analyze` with structured output
- Mini program UI for upload, result display, and history
- Coach-facing recommendation view

Acceptance criteria:

- Median AI response time <= 8s (clip length cap applied)
- AI result persistence and retrieval validated in production-like env

## 3. Engineering Workstreams (Parallel)

### A. Backend Reliability

- Add idempotency for booking-related writes
- Add stricter domain validations and error codes
- Add integration tests for booking/membership/review flows

### B. Frontend Consistency

- Keep student/coach design tokens aligned
- Standardize API error handling and empty/loading states
- Remove remaining legacy/mocked branches

### C. Data & Observability

- Structured logging with request IDs
- Core metrics: booking success, payment success, retention, churn risk count
- Alerting thresholds and on-call handover notes

### D. Security & Compliance

- Privacy consent text and audit fields
- Permission boundary tests (role isolation)
- Data retention and export/delete policy draft

## 4. Risks and Mitigations

- Risk: API schema drift between backend and mini programs
  - Mitigation: lock response schema and add contract checks in CI

- Risk: AI module latency/cost spikes
  - Mitigation: clip duration limits, async job option, fallback responses

- Risk: growth features create noisy leads
  - Mitigation: lead quality tags and ops filtering workflow

## 5. Suggested Sprint Rhythm

- Sprint length: 1 week
- Cadence:
  - Monday: plan and acceptance criteria freeze
  - Wednesday: integration checkpoint
  - Friday: demo + release + rollback verification

## 6. Definition of Done (DoD)

A feature is "done" only when:

1. Business logic and UI are both completed
2. Error handling and empty/loading states are implemented
3. Logs/metrics are added for key events
4. Test checklist is executed and recorded
5. Documentation (`README.md` / this plan / API docs) is updated
