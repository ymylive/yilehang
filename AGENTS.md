# AGENTS.md
Operational guide for coding agents working in this repository.

## 1) Scope and Source of Truth
- Repository root: `E:/project/rl/rl`
- Active apps in this checkout:
  - `apps/api` (FastAPI + SQLAlchemy async backend)
  - `apps/unified-miniapp` (UniApp + Vue 3 + TypeScript)
- Read these first:
  - `CLAUDE.md`
  - `README.md`
  - `apps/api/pyproject.toml`
  - `apps/api/pytest.ini`
  - `apps/unified-miniapp/tsconfig.json`

## 2) Cursor / Copilot Rules Status
Checked project-local rule files:
- `.cursor/rules/` -> not present
- `.cursorrules` -> not present
- `.github/copilot-instructions.md` -> not present
If any are added later, they override this file.

## 3) Setup and Core Commands
Run from repository root unless noted.

### Install
```bash
pnpm install
cd apps/api
pip install -e .
pip install -e ".[dev]"
```

### Dev
```bash
pnpm dev          # unified-miniapp H5
pnpm dev:mp       # unified-miniapp WeChat mini program
pnpm dev:api      # FastAPI on :8000
```

Direct app commands:
```bash
pnpm -C apps/unified-miniapp dev:h5
pnpm -C apps/unified-miniapp dev:mp-weixin
cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Build
```bash
pnpm build
pnpm build:mp
pnpm -C apps/unified-miniapp build:h5
pnpm -C apps/unified-miniapp build:mp-weixin
```

### DB and Seed (API)
```bash
cd apps/api
python -m scripts.init_db
python -m scripts.seed_data
python -m scripts.seed_role_permissions
alembic upgrade head
```

## 4) Lint, Format, Type Check

### Python (`apps/api`)
```bash
cd apps/api
python -m ruff check app tests
python -m ruff check app tests --fix
python -m ruff format app tests
python -m black --line-length 100 app tests
```

### TypeScript/Vue (`apps/unified-miniapp`)
```bash
cd apps/unified-miniapp
npx vue-tsc --noEmit
```

## 5) Testing (Single-Test First)

### Backend quick patterns
```bash
cd apps/api
python -m pytest
python -m pytest tests/test_auth_login.py -q
python -m pytest tests/test_auth_login.py::TestPublicRegistrationHardening::test_register_rejects_admin_role -q
python -m pytest tests/integration/test_data_authz.py::test_parent_can_enroll_own_student -q
python -m pytest -k "register and admin" -q
python -m pytest --cov=app --cov-report=html
```

### Miniapp UI automation note
- `apps/unified-miniapp/tests/test_ui.js` exists.
- No dedicated package script is wired.
- Requires `@dcloudio/uni-automator` and local WeChat DevTools CLI path.

## 6) Code Style Guidelines

### Python (FastAPI + SQLAlchemy)
- Ruff import sorting (`I`) + Black formatting.
- Import order: stdlib -> third-party -> app-local.
- Explicit type hints on public functions.
- Prefer `dict[str, object]` over bare `dict`.
- Keep `Optional[T]` / `T | None` style consistent in touched files.
- Use async ORM patterns (`await db.execute(select(...))`).
- Do not build SQL via string interpolation.
- Keep endpoint handlers thin; put business logic in `app/services/*`.
- Keep API contracts in Pydantic schemas.
- Line length target: 100.

### TypeScript/Vue (UniApp)
- Prefer Composition API (`script setup`) for Vue edits.
- Keep existing style: 2-space indent, single quotes, minimal semicolons.
- Use `@/` alias for app-local imports.
- Avoid `any`; add narrow interfaces/types for API and stores.
- Keep role/page constants centralized (route guards, tab mapping).
- `strict` mode is enabled; do not introduce loose typing.

### Naming conventions
- Python: `snake_case` for vars/functions, `PascalCase` for classes.
- TypeScript: `camelCase` for vars/functions, `PascalCase` for types/components.
- API paths: stable REST style under `/api/v1/*`.

### Error handling and validation
- Raise `HTTPException` with explicit `status_code` and clear `detail`.
- Do not use empty `except` blocks.
- Validate authorization before mutation/sensitive reads.
- Preserve error message semantics that frontend relies on.
- Keep frontend 401 flow: clear token/user and reLaunch login.

### Security and secrets
- Never commit secrets from `.env` or token dump files.
- Do not log plaintext passwords/tokens/sensitive identifiers.
- Preserve public registration hardening and role restrictions.

## 7) Agent Workflow Expectations
- Keep patches minimal and focused; avoid unrelated refactors.
- Respect architecture boundaries:
  - `endpoints/*` -> HTTP/transport concerns
  - `services/*` -> domain logic
  - `schemas/*` -> API contracts
- Add regression tests for bug fixes when practical.
- Validate with targeted tests first, then broaden.
- Ignore unrelated directories like `.tmp_research/` unless asked.

## 8) Definition of Done
- Changed files are linted/formatted with project tools.
- At least one targeted test for changed behavior passes.
- No new type/lint/test regressions introduced.
- Update docs/comments when behavior contracts change.
- Follow commit style used in repo:
  - `feat: ...`
  - `fix: ...`
  - `docs: ...`
  - `chore: ...`
