---
name: cardora-backend
description: Coding standards enforcer for Cardora's FastAPI backend. Use this skill whenever writing, editing, or reviewing any Python backend code in this project — new features, bug fixes, router changes, model changes, schema changes, service logic, or Alembic migrations. Make sure to invoke this skill for any backend work even if the user doesn't explicitly ask for a review, so every change meets Cardora's standards before it lands.
---

# cardora-backend

You are implementing or reviewing backend code for **Cardora** — a FastAPI + PostgreSQL + Gemini AI application. Every change you make must pass the checklist at the end of this document before being considered complete.

The patterns here were established through a full code review of this codebase. Follow them without deviation.

---

## 1. Feature module structure

Every feature lives in `app/features/<name>/` with exactly these files:

```
app/features/<name>/
  __init__.py    ← exports router(s), models, and key schemas
  models.py      ← SQLAlchemy ORM classes only
  schemas.py     ← Pydantic DTOs only
  router.py      ← FastAPI endpoints only (HTTP concerns)
  service.py     ← business logic (add this when router logic exceeds ~50 lines)
```

`router.py` handles: auth, request parsing, calling service, returning responses, HTTP status codes, HTTPException.  
`service.py` handles: DB queries, validation logic, external calls, complex orchestration.

If a file is approaching 150 lines of logic, it needs a `service.py`. A 600-line router is a red flag — it means business logic leaked in.

---

## 2. SQLAlchemy models

```python
import uuid
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MyModel(Base):
    __tablename__ = "my_models"
    __table_args__ = (
        Index("ix_my_models_user_id", "user_id"),
        {"schema": "cardora"},                    # ALL tables in cardora schema
    )

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id    = Column(UUID(as_uuid=True), ForeignKey("cardora.users.id"), nullable=False)
    amount     = Column(Numeric(10, 2), nullable=False)       # money: Numeric(10,2) ONLY
    name       = Column(String(255), nullable=False)           # strings: always include length
    count      = Column(Integer, nullable=False, default=0)    # integers: explicit Integer type
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

**Non-negotiable rules:**
- `{"schema": "cardora"}` in every `__table_args__` — missing this breaks queries silently
- Money → `Numeric(10, 2)`, never `Float` (floats lose precision on financial data)
- Every `Column()` must have a type argument — bare `Column()` or `Column(nullable=False)` with no type is a bug
- `String` columns must have a length: `String(255)`, `String(10)`, etc.
- UUIDs as PKs everywhere, never integer IDs
- Index FK columns that appear in WHERE clauses

---

## 3. Pydantic schemas

```python
from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class MyModelCreate(BaseModel):      # POST input
    name: str
    amount: Decimal

class MyModelUpdate(BaseModel):      # PATCH input — all fields Optional
    name: Optional[str] = None
    amount: Optional[Decimal] = None

class MyModelResponse(BaseModel):    # GET output
    id: UUID
    name: str
    amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True       # Required for ORM → Pydantic — never omit this
```

- `*Create` for POST bodies, `*Update` for PATCH bodies, `*Response` for all outputs
- `from_attributes = True` on every response schema — missing it causes a 500 on any ORM object
- Money fields in schemas: `Decimal`, not `float`
- UUIDs in schemas: `UUID` type (Python), serializes to string in JSON automatically

---

## 4. Router pattern

```python
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.features.auth.jwt import get_current_user
from app.features.auth.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.get("", response_model=list[MyModelResponse])
async def list_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(MyModel).filter(MyModel.user_id == current_user.id).all()

@router.post("", response_model=MyModelResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    payload: MyModelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = my_service.create(db, current_user.id, payload)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

**Security rules:**
- `Depends(get_current_user)` on every protected endpoint — never skip it
- Every DB query filters by `current_user.id` — never return another user's data
- Categories query: `(Category.user_id == user_id) | (Category.user_id.is_(None))` — returns user + system categories
- Register the router in `app/main.py` with `app.include_router(...)`

**Error handling:**
- `ValueError` from service layer → `HTTP 400` with `detail=str(e)` (user-facing message)
- Unexpected exceptions → let the global handler in `app/main.py` catch them (returns `HTTP 500` with a safe message, never a raw traceback)
- Log errors with `logger.error(...)` before re-raising

---

## 5. Service pattern

When router logic grows beyond simple CRUD, extract to `service.py`:

```python
import logging
from uuid import UUID
from sqlalchemy.orm import Session
from app.features.my_feature.models import MyModel
from app.features.my_feature.schemas import MyModelCreate

logger = logging.getLogger(__name__)

def create(db: Session, user_id: UUID, payload: MyModelCreate) -> MyModel:
    if db.query(MyModel).filter(
        MyModel.user_id == user_id,
        MyModel.name == payload.name,
    ).first():
        raise ValueError(f"Item '{payload.name}' already exists")   # caught by router → 400

    item = MyModel(user_id=user_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
```

Services raise `ValueError` for user-facing errors (bad input, duplicates, business rule violations). They don't raise `HTTPException` — that's the router's job.

---

## 6. Logging

```python
import logging
logger = logging.getLogger(__name__)

# Use these levels:
logger.debug("processing transaction %s", transaction_id)   # verbose dev info
logger.info("statement %s processed: %d transactions", stmt_id, count)  # normal events
logger.warning("could not detect payment for card %s", card_id)         # recoverable issue
logger.error("failed to save transactions: %s", e, exc_info=True)       # unexpected failure
```

Never use `print()` for logging. Every module that has meaningful events should have a module-level logger.

---

## 7. Gemini / AI integration

All Gemini calls live exclusively in `app/core/gemini_service.py`.

```python
# WRONG — never do this in a router or service:
import google.generativeai as genai
model = genai.GenerativeModel(...)

# RIGHT — add a function to gemini_service.py and call it:
from app.core.gemini_service import extract_transactions_from_pdf
```

New AI prompts → new function in `gemini_service.py`. Always wrap Gemini calls in try/except — the API is unreliable and returns unpredictable output.

---

## 8. Database migrations

Every model change (add column, change type, add table, drop column) → new Alembic migration:

```powershell
venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe_what_changed"
venv\Scripts\python.exe -m alembic upgrade head
```

Never edit existing migration files. If you need to fix a past migration, create a new one that applies the correction.

---

## 9. `__init__.py` as public API

Each feature's `__init__.py` exports only what other features need:

```python
# app/features/my_feature/__init__.py
from app.features.my_feature.router import router as my_feature_router
from app.features.my_feature.models import MyModel

__all__ = ["my_feature_router", "MyModel"]
```

Internal helpers, service functions, and query utilities should not be exported — they're an implementation detail.

---

## Pre-flight checklist

Before marking any backend change as done, verify each item:

**Security**
- [ ] Every protected endpoint has `Depends(get_current_user)`
- [ ] Every DB query filters by `current_user.id` (or `user_id == current_user.id`)
- [ ] No raw exception tracebacks returned to the client

**Models**
- [ ] `{"schema": "cardora"}` in `__table_args__`
- [ ] Every `Column()` has an explicit type (`String(n)`, `Integer`, `Numeric(10,2)`, etc.)
- [ ] Money fields use `Numeric(10, 2)` — not `Float`, not `int`
- [ ] UUID primary keys on all new tables
- [ ] Alembic migration created and run for any schema change

**Schemas**
- [ ] `from_attributes = True` on every `*Response` schema
- [ ] Naming follows `*Create` / `*Update` / `*Response` convention
- [ ] Money fields are `Decimal` in Pydantic schemas

**Code quality**
- [ ] Business logic in `service.py`, HTTP concerns in `router.py`
- [ ] `logger = logging.getLogger(__name__)` used — no `print()` statements
- [ ] No direct `genai.*` calls outside `gemini_service.py`
- [ ] `__init__.py` updated to export new public symbols
- [ ] Router registered in `app/main.py` if it's new
