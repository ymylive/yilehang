# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Added RBAC role capability in backend models and APIs, including role/permission/menu relationship support.
- Added new API modules: notifications, upload, chat, energy system, merchants, and leaderboard.
- Added static file mount for uploaded assets at `/uploads` in FastAPI app.
- Added merchant miniapp workspace (`apps/merchant`) and root scripts `dev:merchant` / `build:merchant`.
- Added unified multi-role miniapp workspace (`apps/unified-miniapp`) and role-page mapping doc (`docs/role_pages_mapping.md`).
- Added new client/coach pages for chat, energy center, leaderboard, merchant workspace, and extended growth pages.
- Login page adds dual mode: WeChat login and account login (`username/phone/email + password`).
- Login page adds direct entry to email-code registration.
- Backend supports nickname (username) as account credential during password login.
- Added username uniqueness checks in register and profile update flows.
- `.env.example` adds WeChat and SMTP related config examples.
- Added object-level authorization integration tests for students/bookings/growth/training/schedule enrollment flows.
- Added chat websocket security tests for one-time ticket auth and query-token rejection.
- Added unified miniapp runtime safety modules: `PageErrorBoundary`, `safeNavigate`, and telemetry event storage.
- Added fallback static assets (`default-avatar`, `empty`) and pre-build static asset reference checker.

### Changed
- Expanded API router registration to include role, notification, upload, chat, energy, merchant, and leaderboard routes.
- Updated default config behavior for WeChat credential setup to require explicit environment configuration.
- Refreshed README to document merchant/unified apps, new scripts, and new backend module coverage.
- WeChat login now requires real user profile authorization; rejects non-authorized login attempts.
- Existing WeChat users now refresh nickname and avatar on each authorized login.
- Disabled WeChat dev fallback by default (`ALLOW_WECHAT_LOGIN_WITHOUT_SECRET=false`).
- Improved email-code send error response to expose concrete backend failure message.
- Home strategy cards now use deterministic sequence numbers to avoid duplicate labels.
- Standardized project/app naming and production domain references to `rl.cornna.xyz` across docs and deployment templates.

### Fixed
- **[SECURITY]** Removed hardcoded server passwords from 14 deployment scripts (now use environment variables)
- **[SECURITY]** Fixed weak JWT secret key (now requires environment variable with validation)
- **[SECURITY]** Reduced JWT token expiration from 7 days to 2 hours
- **[SECURITY]** Added password complexity validation (min 8 chars, letter + number required)
- **[SECURITY]** Added rate limiting to password reset endpoint (5 attempts per hour)
- **[SECURITY]** Removed plaintext verification codes from logs
- **[PERFORMANCE]** Fixed leaderboard N+1 query (100+ queries → 3 queries, 97% improvement)
- **[PERFORMANCE]** Fixed dashboard recent bookings N+1 query (21 queries → 3 queries, 85% improvement)
- **[PERFORMANCE]** Fixed dashboard booking stats N+1 query (15 queries → 1 query, 93% improvement)
- **[API]** Added missing coach endpoint: `GET /coaches/me/bookings/{booking_id}`
- **[API]** Added missing coach endpoint: `GET /reviews/coach/my`
- **[API]** Added missing coach endpoint: `GET /reviews/feedbacks`
- **[CODE QUALITY]** Extracted magic numbers to config (commission rate, cancellation hours)
- **[CODE QUALITY]** Refactored registration logic to eliminate 80 lines of duplicate code
- **[SECURITY]** Hardened object-level authorization checks to block cross-account data access.
- **[SECURITY]** Hardened chat websocket auth by enforcing short-lived, one-time connection tickets.
- Fixed garbled arrow text in user menu (`>` rendering issue in mini program view).
- Fixed button text vertical alignment issue for user logout and login action buttons.
- Fixed partial garbled comments/text fragments in homepage style section.

### Operations
- Re-deployed production services after server reboot on `82.158.88.34`.
- Renewed and installed SSL for `rl.cornna.xyz` via `acme.sh` (Cloudflare DNS).
- Updated miniapp production API/WebSocket/upload endpoints in `deploy/miniapp/env.example` to `rl.cornna.xyz`.
