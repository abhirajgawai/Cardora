---
name: plan-cardora
description: Plan, architect, design, or review features for the Cardora application. Use before implementing any non-trivial feature to get Cardora-specific placement, file names, patterns, and data model decisions. Covers backend (FastAPI + SQLAlchemy), frontend (Next.js + TypeScript), AI pipeline (Gemini), and database (PostgreSQL).
---

# plan-cardora

You are the architecture advisor for **Cardora** — a credit card statement analyzer that extracts transactions from PDF statements using Gemini AI, categorizes spending, and surfaces insights.

When a developer asks "where does X go?" or "how should I build Y?", answer with the specific files, patterns, and conventions already established in this codebase — not generic advice.

---

## Codebase at a glance

```
E:\Cardora\
├── app/                        ← FastAPI backend (Python)
│   ├── core/                   ← Infrastructure (DB, config, email, Gemini)
│   ├── features/               ← Feature modules (one folder per domain)
│   │   ├── auth/               ← Users, JWT, password reset
│   │   ├── cards/              ← Credit card CRUD
│   │   ├── categories/         ← Transaction categories (21 system + custom)
│   │   ├── statements/         ← PDF upload, Gemini extraction pipeline
│   │   ├── transactions/       ← Transaction CRUD + editing
│   │   ├── analytics/          ← Aggregation queries, trends, charts
│   │   ├── insights/           ← Rule-based + AI spending insights
│   │   │   └── generators/     ← One file per insight type
│   │   └── payments/           ← Payment detection, debt alerts
│   ├── shared/                 ← Cross-feature configs (merchant categories, insight configs)
│   └── main.py                 ← App entry point, router registration
│
└── frontend/                   ← Next.js 16 (App Router, TypeScript)
    └── src/
        ├── app/                ← Pages (one folder per route)
        ├── features/           ← Feature modules mirror the backend
        │   ├── <feature>/
        │   │   ├── api/        ← API calls (axiosClient wrappers)
        │   │   ├── components/ ← React components for this feature
        │   │   ├── types/      ← TypeScript interfaces
        │   │   └── index.ts    ← Public barrel export
        └── shared/
            ├── components/     ← Reusable UI (layout, common, ui)
            ├── contexts/       ← React Context (Auth, theme)
            └── lib/api/        ← Axios client (client.ts)
```

---

## Backend patterns — follow these exactly

### 1. Feature module structure

Every feature is a folder under `app/features/` with:

```
app/features/<name>/
  __init__.py     ← exports router(s)
  models.py       ← SQLAlchemy ORM class
  schemas.py      ← Pydantic request/response DTOs
  router.py       ← FastAPI APIRouter with endpoints
```

Extra files are allowed (e.g., `services.py`, `calculations.py`) when logic is complex enough to warrant it (see `payments/`). Add them inside the feature folder, not in `app/shared/`.

### 2. Model conventions (SQLAlchemy)

```python
import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

class MyModel(Base):
    __tablename__ = "my_models"
    __table_args__ = (
        Index("ix_my_models_user", "user_id"),  # Always index FK lookups
        {"schema": "cardora"},                   # All tables in cardora schema
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("cardora.users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

Key rules:
- **All tables live in the `cardora` schema** — always `{"schema": "cardora"}` in `__table_args__`
- **Money fields use `Numeric(10, 2)`**, never `Float` — floats lose precision
- **Dates (not datetimes) for transaction dates** — credit card statements have no time component
- **Denormalize `statement_month` / `statement_year` onto transactions** — avoids joins on the hottest query path
- **All FKs get an index** — composite where relevant (`user_id + transaction_date`, `user_id + category_id`)
- **UUIDs as PKs** everywhere

### 3. Schema conventions (Pydantic)

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class MyModelCreate(BaseModel):
    name: str

class MyModelResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True   # Required for ORM → Pydantic conversion
```

- `*Create` — input schema for POST
- `*Update` — partial input for PATCH (all fields `Optional`)
- `*Response` — output schema; always include `id` and `created_at`
- Always set `from_attributes = True` (formerly `orm_mode`)

### 4. Router conventions (FastAPI)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.auth.jwt import get_current_user
from app.features.auth.models import User

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("", response_model=list[MyModelResponse])
async def list_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ...
```

- `get_current_user` dependency on every protected endpoint — never skip it
- Resource scoping: **always filter by `current_user.id`** — never return another user's data
- Register in `app/main.py` with `app.include_router(my_router)`

### 5. AI / Gemini integration

All Gemini calls live in `app/core/gemini_service.py`. Do **not** call `genai` directly from feature code.

- New extraction prompts → add a function to `gemini_service.py`
- Background/heavy AI work → trigger via `BackgroundTasks` (see `statements/router.py`)
- Model name: `'gemini-pro-latest'` (current working alias — verify if deprecated)
- Always wrap in try/except and return structured errors; Gemini responses are unpredictable

### 6. Database migrations

Every model change → new Alembic migration:

```powershell
venv\Scripts\python.exe -m alembic revision --autogenerate -m "add_my_feature"
venv\Scripts\python.exe -m alembic upgrade head
```

Never modify existing migrations. New state → new migration file.

---

## Frontend patterns — follow these exactly

### 1. Feature module structure

Mirror the backend feature name in `frontend/src/features/<name>/`:

```
frontend/src/features/<name>/
  api/
    <name>Api.ts     ← all API calls for this feature
  components/
    <Component>.tsx  ← feature-specific React components
  types/
    index.ts         ← TypeScript interfaces (mirrors backend schemas)
  index.ts           ← barrel export: export * from './api/...'; export * from './types';
```

### 2. API client pattern

All API calls use the shared Axios client from `@/shared/lib/api/client`:

```typescript
import apiClient from '@/shared/lib/api/client';
import { MyModel, CreateMyModelData } from '../types';

export const getMyModels = async (): Promise<MyModel[]> => {
  const response = await apiClient.get('/my-feature');
  return response.data;
};

export const createMyModel = async (data: CreateMyModelData): Promise<MyModel> => {
  const response = await apiClient.post('/my-feature', data);
  return response.data;
};
```

- The client automatically attaches JWT from `localStorage` and handles 401 redirects
- For file uploads, pass `FormData` — the client strips `Content-Type` so axios sets the multipart boundary automatically

### 3. TypeScript types

Types mirror the backend Pydantic schemas exactly:

```typescript
// frontend/src/features/<name>/types/index.ts
export interface MyModel {
  id: string;          // UUIDs are strings in TypeScript
  user_id: string;
  name: string;
  created_at: string;  // ISO datetime string
}

export interface CreateMyModelData {
  name: string;
}
```

### 4. Page routing

Pages live in `frontend/src/app/<route>/page.tsx`. Use the Next.js App Router — every folder is a route segment. Protected pages redirect to `/login` if no token in localStorage.

### 5. Shared components

- Layout components (Sidebar, Header) → `src/shared/components/layout/`
- Generic UI primitives (Button, Card, Dialog) → `src/shared/components/ui/` (shadcn/ui)
- Feature-specific components stay inside the feature folder

---

## How to plan a new feature

When asked to design a feature, answer these questions:

### Q1: Does this need a new DB table?
- **Yes** → New model in `app/features/<name>/models.py`, add Alembic migration
- **No** → Extend an existing model or compute from existing data

### Q2: Does this extend an existing feature or need its own folder?
- Extends existing (e.g., new analytics endpoint) → add to that feature's router/schemas
- New domain (e.g., budgets, notifications) → new folder under `app/features/`

### Q3: Does it call Gemini?
- Bulk extraction at upload time → add to `gemini_service.py`, call from `statements/router.py` background task
- On-demand per-user request → add function to `gemini_service.py`, call from feature router
- Never call `genai` directly from a router

### Q4: Where does the frontend component live?
- Feature-specific → `src/features/<name>/components/`
- Reused across features → `src/shared/components/common/`
- Page layout/shell → `src/shared/components/layout/`

### Q5: Does this need a new page?
- Yes → `src/app/<route>/page.tsx` + add link to Sidebar (`src/shared/components/layout/Sidebar.tsx`)

---

## Current feature inventory

| Feature | Backend prefix | Frontend feature folder | Has DB table? |
|---|---|---|---|
| Auth / Users | `/auth`, `/users` | `auth` | `users` |
| Credit Cards | `/credit-cards` | `cards` | `credit_cards` |
| Categories | `/categories` | — (read-only) | `categories` |
| Statements | `/statements` | `statements` | `statements` |
| Transactions | `/transactions` | `transactions` | `transactions` |
| Analytics | `/analytics` | `analytics` | — (queries only) |
| Insights | `/insights` | `insights` | `insights`, `insight_transactions` |
| Payments | — (service only, not routed) | — | — |

**Note:** The payments feature has a router in `main.py` that is currently commented out. It exists as internal services called from `statements/router.py`.

---

## Architectural constraints and decisions already made

- **Monolith, not microservices** — everything is one FastAPI app. Do not propose splitting into services unless the user explicitly asks.
- **JWT in localStorage** — authentication state is managed client-side. Backend is stateless.
- **No Redis / no task queue** — background work uses FastAPI `BackgroundTasks` (in-process). For anything heavier, propose adding Celery + Redis and ask the user first.
- **PostgreSQL only** — no other datastores. Don't propose adding Redis for caching without asking.
- **Gemini for all AI** — the project is committed to Google Gemini. Don't suggest OpenAI or Anthropic.
- **No Docker yet** — deployment is manual. Don't propose Dockerizing unless asked.
- **SGD currency** — the demo data and prompts are tuned for Singapore dollar credit card statements. Amounts are always positive decimals.
- **Single-user scoping** — all data is scoped to `user_id`. There is no multi-tenancy or shared data between users.
- **No soft deletes** — records are hard-deleted. If soft delete is needed, it requires a new migration + `is_deleted` column pattern.

---

## Common planning scenarios

### "Add a new insight type"
1. Create `app/features/insights/generators/<insight_name>.py`
2. Implement a function matching the signature of existing generators (takes transactions + user context, returns `InsightCreate` dict)
3. Register it in `app/features/insights/ai_insights.py`
4. No new DB table — insights write to the existing `insights` table
5. Frontend picks it up automatically (insights are rendered generically by type)

### "Add a budget feature"
1. New folder: `app/features/budgets/`
2. Files: `models.py` (Budget table with `user_id`, `category_id`, `amount`, `period`), `schemas.py`, `router.py`
3. Alembic migration
4. Frontend: `src/features/budgets/` with `api/budgetsApi.ts`, `types/index.ts`
5. New page: `src/app/budgets/page.tsx`
6. Add "Budgets" to Sidebar

### "Add a notification/alert system"
1. New folder: `app/features/notifications/`
2. Model: `notifications` table (`user_id`, `type`, `message`, `is_read`, `created_at`)
3. Trigger notifications from other features (e.g., after statement upload, from payment detection)
4. Frontend: polling endpoint or later upgrade to WebSocket
5. Bell icon in Sidebar with unread count

### "Add a new analytics endpoint"
1. Add to `app/features/analytics/router.py` + `schemas.py` — no new feature folder needed
2. Mirror in `frontend/src/features/analytics/api/analyticsApi.ts`
3. Add TypeScript types to `frontend/src/features/analytics/types/index.ts`

### "Store user preferences / settings"
1. Add columns to the existing `users` table (e.g., `currency`, `timezone`, `notification_prefs`)
2. Alembic migration
3. Expose via `PATCH /users/me` in `app/features/auth/router.py`
4. Frontend: `src/features/settings/` already exists — add to it

---

## When to ask the user before proceeding

- Any schema change (adds/removes columns on existing tables) — confirm the migration plan
- Adding a new external dependency (a new pip package or npm package)
- Anything that changes the Gemini prompt structure — can affect extraction quality across all statements
- Any change to the CORS allowlist in `app/main.py`
- Removing or renaming an existing API endpoint — could break the frontend
