# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

易乐航 ITS 智慧体教云平台 - A youth sports training digital platform built around WeChat Mini Programs. The platform covers the "booking → class → lesson consumption → repurchase" workflow with role-based products:

- **Unified Mini Program** (`apps/unified-miniapp`): 🆕 Single WeChat mini program with multi-role support (admin/coach/parent/student)
- **Student App** (`apps/client`): Booking, schedule, membership cards, training records, messaging
- **Coach App** (`apps/coach`): Workbench, scheduling, student management, feedback, income, reviews
- **Admin Dashboard** (`apps/admin`): Business analytics, user management, operations dashboard
- **Backend API** (`apps/api`): FastAPI + PostgreSQL unified API

## Development Commands

### Root-level (pnpm monorepo)
```bash
pnpm install                    # Install all dependencies
pnpm dev:client                 # Student app H5 dev server
pnpm dev:coach                  # Coach app H5 dev server
pnpm dev:admin                  # Admin dashboard dev server
pnpm dev:api                    # FastAPI server (port 8000)
```

### Mini Program builds
```bash
pnpm -C apps/client build:mp-weixin        # Build student WeChat mini program
pnpm -C apps/coach build:mp-weixin         # Build coach WeChat mini program
pnpm -C apps/unified-miniapp build:mp-weixin  # Build unified multi-role mini program
```
Output directories: `apps/*/dist/build/mp-weixin`

### Backend (apps/api)
```bash
cd apps/api
pip install -e .                       # Install with editable mode
pip install -e ".[dev]"                # Include dev dependencies (pytest, black, ruff)
python -m scripts.init_db              # Initialize database tables
python -m scripts.seed_data            # Create test data
python -m scripts.seed_role_permissions  # 🆕 Initialize RBAC roles/permissions/menus
alembic upgrade head                   # Run database migrations
uvicorn app.main:app --reload          # Start dev server
```

### Linting/Formatting (Python)
```bash
black --line-length 100 apps/api
ruff check apps/api --fix
```

## Architecture

### Frontend Apps (UniApp + Vue3)
- **Framework**: UniApp 3.x with Vue 3 Composition API
- **UI Library**: Wot Design Uni (orange/yellow theme)
- **State**: Pinia stores in `src/stores/`
- **API Client**: `src/api/index.ts` - centralized request wrapper with token handling
- **Pages**: Defined in `src/pages.json`, components in `src/pages/`
- **Platform detection**: Auto-switches API base URL for H5 vs WeChat Mini Program

### Backend API (FastAPI)
- **Entry**: `app/main.py` - FastAPI app with lifespan management
- **Router**: `app/api/v1/router.py` - all endpoint modules registered here
- **Models**: `app/models/` - SQLAlchemy async models organized by domain:
  - `user.py`: User, Student, Coach, ParentStudentRelation
  - `rbac.py`: 🆕 Role, Permission, Menu, user_roles, role_permissions, role_menus
  - `booking.py`: MembershipCard, Booking, Transaction, Review, CoachFeedback
  - `course.py`: Course, Venue, Schedule, Attendance
  - `growth.py`: FitnessTest, FitnessMetric, TrainingSession
  - `notification.py`, `chat.py`: Messaging features
- **Middleware**: `app/middleware/role_auth.py` - 🆕 RBAC middleware with `require_role()`, `require_permission()` decorators
- **Schemas**: `app/schemas/` - Pydantic models for request/response
- **Services**: `app/services/` - Business logic (booking_service, auth_service)
- **Config**: `app/core/config.py` - Settings via pydantic-settings

### API Endpoints (prefix: `/api/v1`)
Core: `/auth`, `/students`, `/schedules`, `/training`, `/growth`
Booking: `/bookings`, `/memberships`, `/coaches`, `/reviews`
Admin: `/dashboard`
Features: `/ai`, `/notifications`, `/upload`, `/chat`
RBAC: `/user/roles`, `/user/permissions`, `/user/menus`, `/user/switch-role` 🆕

### Admin Dashboard (Vue3 + Element Plus)
- Standard Vite + Vue3 setup
- Views in `src/views/`, layouts in `src/layouts/`
- Uses ECharts for analytics

## Key Patterns

### Authentication Flow
- Phone/email + password login, email verification codes, WeChat OAuth
- JWT tokens stored in `uni.getStorageSync('token')`
- Token auto-attached via `src/api/index.ts` request wrapper
- 401 responses trigger automatic redirect to login

### Booking System
- Students book coaches via available time slots
- `BookingService` handles conflict detection and lesson deduction
- Transactions track lesson consumption

### Role-based Access
- Roles: `parent`, `student`, `coach`, `admin`, `merchant`
- Coach-specific endpoints under `/coaches/me/*`
- Parent can manage multiple student accounts

### Multi-Role System (RBAC) 🆕
- **Database Tables**: `roles`, `permissions`, `menus` + association tables
- **Backend Middleware**: `app/middleware/role_auth.py`
  - `require_role(['admin', 'coach'])` - Role-based access control
  - `require_permission(['booking:create'])` - Permission-based access control
- **Frontend Components** (`apps/unified-miniapp`):
  - `src/utils/role-guard.ts` - Route guard by role
  - `src/components/RoleSwitcher.vue` - Role switching UI
  - `src/components/DynamicTabBar.vue` - Role-based TabBar
  - `src/directives/permission.ts` - `v-permission` directive
  - `src/stores/permission.ts` - Permission state management
- **Role-Page Mapping**:
  - Admin: `/pages/admin/*` (dashboard, users, analytics)
  - Coach: `/pages/coach/*` (workbench, schedule, students)
  - Parent: `/pages/booking/*`, `/pages/membership/*`, `/pages/growth/*`
  - Student: `/pages/training/*`, `/pages/growth/*`, `/pages/energy/*`

## Deployment

Docker Compose production setup in `docker/`:
- PostgreSQL 15
- FastAPI (port 8001 internal)
- Nginx reverse proxy (80/443)
- SSL via acme.sh with Cloudflare DNS

Deploy script: `scripts/deploy_full.py`

## Test Accounts (seed data)
| Role | Phone/Email | Password |
|------|-------------|----------|
| Admin | 13800000000 / admin@test.com | admin123 |
| Coach | 13800000001 / coach@test.com | coach123 |
| Parent | - / parent@test.com | parent123 |
| Student | 13900000001 / student@test.com | student123 |

## Testing

### Backend Tests
```bash
cd apps/api
pytest tests/                              # Run all tests
pytest tests/test_role_api.py              # RBAC unit tests
pytest tests/integration/test_role_flow.py # RBAC integration tests (40 cases)
pytest --cov=app --cov-report=html         # Generate coverage report
```

### Frontend Tests
```bash
cd apps/unified-miniapp
npm run test:ui                            # UI automation tests
```

### Test Reports
Test reports are generated in `reports/` directory:
- `test_report.html` - HTML test results with pass/fail status
- `performance_report.md` - API response times and load testing results
- `bugs.md` - Bug tracking and known issues

### Test Coverage
Target coverage: >80% for RBAC modules
- `app/api/v1/endpoints/roles.py`: 92%
- `app/middleware/role_auth.py`: 88%
- `app/models/rbac.py`: 100%
- `app/schemas/role.py`: 100%
