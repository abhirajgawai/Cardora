# Cardora

Credit card statement analyzer for the Singapore market. Users upload PDF statements; Gemini AI extracts transactions, categorizes spending, and surfaces payment health insights.

**Stack:** FastAPI (Python) · PostgreSQL (port 5433) · Next.js 16 App Router · TypeScript · SQLAlchemy · Alembic · shadcn/ui · Tailwind CSS  
**Ports:** Backend `8000` · Frontend `3000` · DB `5433`  
**Currency:** SGD. All amounts are positive decimals.  
**Architecture:** Feature-based monolith — `app/features/<name>/` backend, `frontend/src/features/<name>/` frontend.

For detailed patterns, naming conventions, and feature planning → run `/plan-cardora`

---

## Hard Rules

- **Scope all data to `current_user.id`** — never return another user's data
- **All tables in `cardora` schema** — `{"schema": "cardora"}` in every `__table_args__`
- **Money = `Numeric(10, 2)`** — never `Float`
- **Gemini calls only through `app/core/gemini_service.py`** — never call `genai` directly from a router
- **Every protected endpoint uses `Depends(get_current_user)`** — never skip auth
- **Every model change → new Alembic migration** — never edit existing migration files
- **UUID primary keys everywhere** — no integer IDs
- **JWT in `localStorage`** — backend is stateless, no server-side sessions

---

## Architecture Constraints

- Monolith only — no microservices proposals without being asked
- PostgreSQL only — no Redis or additional datastores without explicit approval
- Gemini for all AI — no OpenAI or Anthropic
- No Docker yet — manual dev setup
- No soft deletes — hard delete only (add `is_deleted` only if explicitly requested)
- No task queue — use FastAPI `BackgroundTasks`; Celery requires explicit approval

---

## Code Placement

| What | Where |
|---|---|
| New backend feature | `app/features/<name>/` with `models.py`, `schemas.py`, `router.py` |
| New frontend feature | `frontend/src/features/<name>/` with `api/`, `components/`, `types/`, `index.ts` |
| New page | `frontend/src/app/<route>/page.tsx` + add entry to `Sidebar.tsx` |
| New Gemini prompt | New function in `app/core/gemini_service.py` |
| Register new router | `app/main.py` via `app.include_router(...)` |

---

## Anti-Patterns

- Returning data without filtering by `current_user.id`
- Using `Float` for monetary values
- Calling `genai.*` directly from a router or feature file
- Adding a new page without a Sidebar entry
- Adding npm/pip packages without noting them in the conversation
- Modifying existing Alembic migration files — always create a new one
- Omitting `from_attributes = True` in Pydantic response schemas
- Using `fetch()` directly in the frontend — always use the shared Axios client at `@/shared/lib/api/client`
- Comments that explain what code does — only add them for non-obvious constraints or workarounds
- Proposing microservices, Docker, Redis, or alternative AI providers unprompted

---

## Preferences

- Edit existing files before creating new ones
- Explicit imports over star imports in Python
- `const` arrow functions for React components
- `async/await` over `.then()` chains in TypeScript
- Pydantic schema naming: `*Create` for POST input, `*Update` for PATCH input, `*Response` for output

---

## Success Criteria

A good implementation:
- Scopes every DB query to `current_user.id`
- Follows the feature-module folder structure without exception
- Passes `tsc --noEmit` (TypeScript) with no new errors
- Is self-explanatory from file and function names alone
- Has a corresponding Alembic migration for any schema change
- Uses the shared Axios client — never raw `fetch()`
