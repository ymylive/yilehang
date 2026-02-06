# Yilehang ITS Sports Platform

A WeChat mini-program-first platform for youth sports training operations.

## Product Positioning

Yilehang provides three role-based products around booking and lesson consumption:

- Student app (`apps/client`): booking, schedule, membership, growth records
- Coach app (`apps/coach`): schedule, students, feedback, income, reviews
- Admin web (`apps/admin`): operations and data dashboard

The backend (`apps/api`) is a FastAPI service with PostgreSQL.

## Current Status (2026-02)

Implemented and available now:

- Student side: booking flow, schedule view, training sessions, membership and transactions, basic review flow
- Coach side: workbench, schedule/detail, student list/detail, feedback submit, income detail, review reply, profile
- API side: auth, coaches, students, bookings, memberships, reviews, dashboard, AI placeholder routes
- Deployment: Dockerized API + PostgreSQL + Nginx with HTTPS

Recent completed refactors:

- Coach pages migrated from mock data to real APIs with defensive response normalization
- Client and coach UI refreshed to a unified orange/yellow visual style
- Copy handling standardized to reduce encoding-related text corruption issues

## Monorepo Structure

```text
yilehang/
|- apps/
|  |- client/          # Student mini program (UniApp)
|  |- coach/           # Coach mini program (UniApp)
|  |- admin/           # Admin web (Vue3 + Vite)
|  \- api/             # FastAPI backend
|- packages/
|  |- ui/
|  |- utils/
|  \- types/
|- database/
|- docker/
|- scripts/
|- docs/
\- README.md
```

## Tech Stack

- Client/Coach: UniApp + Vue 3 + TypeScript + Pinia + Wot Design Uni
- Admin: Vue 3 + TypeScript + Element Plus + ECharts
- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Deployment: Docker Compose + Nginx + acme.sh (Cloudflare DNS challenge)

## Quick Start

### 1) Prerequisites

- Node.js >= 18
- pnpm >= 8
- Python >= 3.10
- PostgreSQL >= 15

### 2) Install Dependencies

```bash
pnpm install

cd apps/api
pip install -e .
cp .env.example .env
```

### 3) Run in Development

From repository root:

```bash
pnpm dev:api      # FastAPI at :8000
pnpm dev:client   # Student H5
pnpm dev:coach    # Coach H5
pnpm dev:admin    # Admin web
```

### 4) Build WeChat Mini Program Packages

```bash
pnpm -C apps/client build:mp-weixin
pnpm -C apps/coach build:mp-weixin
```

Import generated output in WeChat DevTools:

- `apps/client/dist/build/mp-weixin`
- `apps/coach/dist/build/mp-weixin`

## API Entry Points

When backend is running:

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

Main route groups (prefix `/api/v1`):

- `/auth`
- `/students`
- `/schedules`
- `/training`
- `/growth`
- `/bookings`
- `/memberships`
- `/coaches`
- `/reviews`
- `/dashboard`
- `/ai`

## Deployment Snapshot

Production report reference: `DEPLOYMENT_REPORT.md`

- Domain: `https://yilehang.cornna.xyz`
- API docs: `https://yilehang.cornna.xyz/docs`

## Development Plan (Next 12 Weeks)

Detailed plan: `docs/dev_plan.md`

### Phase 1 (Week 1-3): Internal MVP Hardening

Goal: make student/coach/booking/lesson-card flow stable for daily internal operation.

- Complete API contract alignment (client + coach + backend)
- Add missing backend validations (booking conflict, lesson consumption consistency)
- Improve failure states and retry UX for booking/cancel/reschedule
- Add role-permission regression checks (admin/coach/student)
- Add baseline monitoring: API error rate, booking success rate

Exit criteria:

- Internal test users can complete full booking lifecycle without manual DB fixes
- P0 defects in booking and lesson consumption are cleared

### Phase 2 (Week 4-6): Public-facing Mini Program + Conversion

Goal: support external traffic and trial conversion.

- Build marketing home sections (environment/course/coach/price/reviews)
- Add free-trial signup and consultation CTA
- Add basic campaign capability (coupon/referral code)
- Add analytics events (visit, click, booking submit, conversion)

Exit criteria:

- Conversion funnel observable end-to-end
- New user can complete trial signup in under 60 seconds

### Phase 3 (Week 7-9): Ops Dashboard + Retention

Goal: provide actionable operations visibility for owner/ops.

- Daily/weekly/monthly metrics: attendance, new users, renewals, revenue, coach workload
- Alerts: low attendance students, churn-risk students, scheduling anomalies
- Add follow-up workflow fields for ops actions

Exit criteria:

- Dashboard supports weekly operations meeting decisions
- Risk list can be exported and followed up

### Phase 4 (Week 10-12): AI Sports Module (MVP)

Goal: launch first practical AI capability with measurable value.

- Integrate jump-rope detection service (video clip upload + result)
- Return structured output: count, confidence, posture issues, suggestions
- Add AI advice endpoint for training and diet Q&A
- Save AI analysis history per student for trend tracking

Exit criteria:

- At least one AI feature available in mini program with stable response SLA
- AI output can be reviewed by coach and linked to training records

## Quality and Security Baseline (Cross-phase)

- Auth: phone verification login + token expiry/refresh strategy
- Data protection: role-based data isolation, privacy policy and consent flow
- Delivery: staging before production, rollback-capable release process
- Observability: request tracing, structured logs, error alerting

## Team Workflow

Suggested commit convention:

```text
feat: new feature
fix: bug fix
refactor: non-breaking refactor
docs: documentation update
test: tests
chore: tooling/build maintenance
```

---

If you need a cloud rollout runbook (Docker + domain + SSL + CI), use:

- `scripts/deploy_full.py`
- `scripts/setup_ssl.py`

and align with `DEPLOYMENT_REPORT.md`.
