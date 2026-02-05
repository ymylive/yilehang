# Development Plan

## Phase 0: Foundations (done / in progress)
- Mini-program structure, core pages and navigation
- SMS login + WeChat login
- Booking, schedule, membership, review, growth modules (base)
- Deployment scripts (Docker + SSL)

## Phase 1: Internal MVP (students + coaches + booking + lesson count)
- Coach availability management
- Student booking flow with conflict checks
- Lesson card/consumption tracking
- Basic notifications (SMS + in-app)
- Role-based access control

## Phase 2: External Marketing
- Marketing homepage (mini-program)
- Free trial signup + consultation CTA
- Simple campaigns (coupons, referral codes)
- Conversion tracking dashboard (basic)

## Phase 3: Operations & Data
- Admin/ops dashboard (attendance, revenue, renewal)
- Risk alerts: low attendance, churn risk, schedule anomalies
- CRM workflows: follow-up tasks, reminders

## Phase 4: AI Modules (staged)
- Jump rope detection (video-based) – integrate CV model
- Training feedback (form correction + accuracy score)
- AI advice (training + diet suggestions)
- AI Q&A assistant (parents + students)

## Key Dependencies
- WeChat Mini Program credentials
- Aliyun SMS account + template
- Domain + SSL (acme.sh)
- Coach content & course data

## Technical Tasks (near-term)
- Finish SMS registration flow
- Add AI stub endpoints (ready for integration)
- Cleanup unused modules and legacy docs
- Update deployment scripts to support `docker compose`
