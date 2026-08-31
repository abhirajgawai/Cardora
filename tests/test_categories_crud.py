"""
Categories CRUD Tests (POST / PATCH / DELETE)

Exercises the real FastAPI app in-process via TestClient, with the DB session
dependency overridden to a transaction-wrapped session (rollback per test).

Uses a dedicated test schema (`dev`) inside the cardora_dev database because
the shared `cardora` schema may not be writable by the app role on every
dev machine. Tables are created from the models on first run.

Compare to .NET: WebApplicationFactory integration tests.
"""
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

TEST_SCHEMA = os.environ.get("CARDORA_TEST_SCHEMA", "dev")
TEST_DB_URL = os.environ.get(
    "CARDORA_TEST_DB_URL",
    "postgresql://cardora_user:cardora_secure_pass_2025@localhost:5433/cardora_dev",
)

engine = create_engine(
    TEST_DB_URL.replace("postgresql://", "postgresql+psycopg://", 1),
    connect_args={"options": f"-csearch_path={TEST_SCHEMA},public"},
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _ensure_schema_and_tables():
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}"))

    from app.core.database import Base
    import app.features.auth.models  # noqa: F401
    import app.features.categories.models  # noqa: F401
    import app.features.cards.models  # noqa: F401
    import app.features.transactions.models  # noqa: F401
    import app.features.statements.models  # noqa: F401
    import app.features.insights.models  # noqa: F401

    for t in Base.metadata.sorted_tables:
        if t.schema != "cardora":
            continue
        ddl = str(CreateTable(t).compile(engine)).replace("cardora.", f"{TEST_SCHEMA}.")
        try:
            with engine.begin() as conn:
                conn.execute(text(ddl))
                for idx in t.indexes:
                    conn.execute(text(str(CreateIndex(idx).compile(engine)).replace("cardora.", f"{TEST_SCHEMA}.")))
        except Exception as e:
            if "DuplicateTable" not in str(e) and "already exists" not in str(e):
                raise


_ensure_schema_and_tables()

# Route every `cardora.` reference to the test-owned schema at the DDL level —
# SQLAlchemy model __table_args__ hardcode the schema name, and per-session
# search_path doesn't affect schema-qualified statements.
from sqlalchemy import event  # noqa: E402


def _rewrite(cursor, statement, parameters, context, executemany=None):
    if "cardora." in statement:
        statement = statement.replace("cardora.", f"{TEST_SCHEMA}.")
        cursor.execute(statement, parameters)
        return True
    return None


event.listen(engine, "do_execute", _rewrite)

# The app's own engine must be rewritten too, so TestClient requests (which
# use the app's engine through get_db) land in the test-owned schema.
from app.core.database import engine as app_engine  # noqa: E402

event.listen(app_engine, "do_execute", _rewrite)

from app.main import app  # noqa: E402
from app.core.database import get_db  # noqa: E402
from app.features.auth.models import User  # noqa: E402
from app.features.categories.models import Category  # noqa: E402
from app.features.auth.jwt import create_access_token  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _seed_system_categories():
    with engine.begin() as conn:
        count = conn.execute(text(f"SELECT count(*) FROM {TEST_SCHEMA}.categories WHERE user_id IS NULL")).scalar()
        if count == 0:
            names = ["Groceries", "Dining", "Transport", "Shopping", "Entertainment", "Bills", "Health", "Other"]
            for i, name in enumerate(names):
                conn.execute(
                    text(f"INSERT INTO {TEST_SCHEMA}.categories (id, user_id, name, icon, color, is_custom, created_at) "
                         "VALUES (:id, NULL, :name, :icon, NULL, FALSE, now())"),
                    {"id": str(uuid.uuid4()), "name": name, "icon": "\U0001F6D2"},
                )


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    # app models are hard-bound to the `cardora` schema; route them to the
    # test-owned mirror schema for this session
    session.execute(text(f"SET search_path TO {TEST_SCHEMA}, public"))
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)


def make_user(db_session, email=None) -> User:
    user = User(
        email=email or f"cat-test-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="not-a-real-hash",
        timezone="Asia/Singapore",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


def auth_headers(user: User) -> dict:
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return {"Authorization": f"Bearer {token}"}


def make_system_category(db_session, name=None) -> Category:
    cat = Category(
        name=name or f"System-{uuid.uuid4().hex[:6]}",
        icon="\U0001F6D2",
        is_custom=False,
        user_id=None,
    )
    db_session.add(cat)
    db_session.flush()
    return cat


def make_custom_category(db_session, user: User, name=None) -> Category:
    cat = Category(
        user_id=user.id,
        name=name or f"Custom-{uuid.uuid4().hex[:6]}",
        icon="\u2615",
        is_custom=True,
    )
    db_session.add(cat)
    db_session.flush()
    return cat


# -- POST -----------------------------------------------------------


def test_create_category_returns_201(db_session, client):
    user = make_user(db_session)
    response = client.post(
        "/categories",
        json={"name": "Coffee Shops", "icon": "\u2615", "color": "#8B4513"},
        headers=auth_headers(user),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Coffee Shops"
    assert body["icon"] == "\u2615"
    assert body["color"] == "#8B4513"
    assert body["is_custom"] is True
    assert body["id"]

    stored = db_session.query(Category).filter(Category.id == body["id"]).one()
    assert str(stored.user_id) == str(user.id)


def test_create_category_requires_auth(client):
    response = client.post("/categories", json={"name": "Nope"})
    # HTTPBearer's auto_error returns 403 for a missing header; invalid tokens
    # return 401 via verify_token. Both mean "not authenticated".
    assert response.status_code in (401, 403)


def test_create_category_rejects_duplicate_name(db_session, client):
    user = make_user(db_session)
    make_custom_category(db_session, user, name="Coffee Shops")
    response = client.post("/categories", json={"name": "Coffee Shops"}, headers=auth_headers(user))
    assert response.status_code == 409


# -- PATCH ----------------------------------------------------------


def test_update_category_succeeds(db_session, client):
    user = make_user(db_session)
    cat = make_custom_category(db_session, user)
    response = client.patch(
        f"/categories/{cat.id}",
        json={"name": "Renamed", "color": "#123456"},
        headers=auth_headers(user),
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "Renamed"
    assert body["color"] == "#123456"
    assert body["icon"] == "\u2615"

    db_session.refresh(cat)
    assert cat.name == "Renamed"


def test_update_other_users_category_returns_404(db_session, client):
    owner = make_user(db_session)
    attacker = make_user(db_session)
    cat = make_custom_category(db_session, owner)
    response = client.patch(
        f"/categories/{cat.id}",
        json={"name": "Hijacked"},
        headers=auth_headers(attacker),
    )
    assert response.status_code == 404
    db_session.refresh(cat)
    assert cat.name != "Hijacked"


def test_update_nonexistent_category_returns_404(db_session, client):
    user = make_user(db_session)
    response = client.patch(
        f"/categories/{uuid.uuid4()}",
        json={"name": "Ghost"},
        headers=auth_headers(user),
    )
    assert response.status_code == 404


def test_update_system_category_rejected(db_session, client):
    user = make_user(db_session)
    cat = make_system_category(db_session)
    response = client.patch(
        f"/categories/{cat.id}",
        json={"name": "Mutated"},
        headers=auth_headers(user),
    )
    assert response.status_code in (403, 404)
    db_session.refresh(cat)
    assert cat.name != "Mutated"


# -- DELETE ---------------------------------------------------------


def test_delete_category_returns_204(db_session, client):
    user = make_user(db_session)
    cat = make_custom_category(db_session, user)
    response = client.delete(f"/categories/{cat.id}", headers=auth_headers(user))
    assert response.status_code == 204
    assert db_session.query(Category).filter(Category.id == cat.id).first() is None


def test_delete_other_users_category_returns_404(db_session, client):
    owner = make_user(db_session)
    attacker = make_user(db_session)
    cat = make_custom_category(db_session, owner)
    response = client.delete(f"/categories/{cat.id}", headers=auth_headers(attacker))
    assert response.status_code == 404
    assert db_session.query(Category).filter(Category.id == cat.id).first() is not None


def test_delete_nonexistent_category_returns_404(db_session, client):
    user = make_user(db_session)
    response = client.delete(f"/categories/{uuid.uuid4()}", headers=auth_headers(user))
    assert response.status_code == 404


def test_delete_system_category_rejected(db_session, client):
    user = make_user(db_session)
    cat = make_system_category(db_session)
    response = client.delete(f"/categories/{cat.id}", headers=auth_headers(user))
    assert response.status_code in (403, 404)
    assert db_session.query(Category).filter(Category.id == cat.id).first() is not None


# -- GET unaffected --------------------------------------------------


def test_list_categories_includes_system_and_custom(db_session, client):
    user = make_user(db_session)
    system_cat = make_system_category(db_session)
    custom_cat = make_custom_category(db_session, user)

    response = client.get("/categories", headers=auth_headers(user))
    assert response.status_code == 200
    ids = {c["id"] for c in response.json()}
    assert str(system_cat.id) in ids
    assert str(custom_cat.id) in ids


def test_list_categories_excludes_other_users_custom(db_session, client):
    owner = make_user(db_session)
    other = make_user(db_session)
    other_cat = make_custom_category(db_session, owner)

    response = client.get("/categories", headers=auth_headers(other))
    ids = {c["id"] for c in response.json()}
    assert str(other_cat.id) not in ids
