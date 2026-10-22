"""
Central test configuration.

Important: DATABASE_URL is set HERE, right at the start, BEFORE any app
import. Python caches module imports -- if app.database (and thus the
engine/session) was already imported once with the production URL,
every later import would reuse that same (wrong) connection. Since we
set os.environ first and only import the app AFTERWARDS, the app's own
internal mechanisms (middleware, startup logic) automatically use the
test database too -- without us having to override every single spot
individually.

Tests deliberately run against real PostgreSQL, not SQLite: several
past bugs in this project only occurred with PostgreSQL (e.g. enum
value casing) -- SQLite would have made these bugs invisible instead of
catching them.
"""
import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://parcella:test@db_test:5432/parcella_test",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests-only")
os.environ.setdefault("ENVIRONMENT", "development")

# The session fixture below drops and recreates every table. setdefault()
# keeps a DATABASE_URL that's already set -- inside the dev `web`
# container that's the real dev database, and running pytest there wiped
# it (2026-07-23 and again 2026-10-23). So refuse anything that isn't a
# test database: use ./run_tests.sh, which points at db_test.
_test_db_name = os.environ["DATABASE_URL"].rsplit("/", 1)[-1].split("?", 1)[0]
if not _test_db_name.endswith("_test"):
    raise RuntimeError(
        f"Refusing to run the tests against database {_test_db_name!r}: they drop every table. "
        "Run ./run_tests.sh, or set DATABASE_URL to a database whose name ends in _test."
    )

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.database import Base, engine, AsyncSessionLocal
from app.main import app
from app.models import User, UserRole
from app.auth import hash_password


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _tabellen_erstellen():
    """Creates all tables fresh once per test run (from the current
    models, not via Alembic -- the current model state is enough for tests)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _frische_verbindung():
    """
    Discards the connection pool BEFORE each individual test.

    Necessary because pytest-asyncio gives each test function its own
    event loop, but our database engine (app.database.engine) is a
    singleton. Without this, the engine would try to reuse a connection
    from an already-closed loop (from the previous test) -- which shows
    up as an "attached to a different loop" error. Discarding causes
    new connections to be created automatically in the currently
    running loop the next time they're needed.

    This approach is deliberately independent of pytest-asyncio's own
    loop-scope configuration -- that has changed multiple times between
    versions (see docs/testing.md) and wasn't a reliable foundation.
    """
    await engine.dispose()
    yield


@pytest_asyncio.fixture(autouse=True)
async def _tabellen_leeren(_frische_verbindung):
    """
    Empties all tables before EVERY individual test. Simpler and more
    robust than nested transactions/savepoints -- works reliably even
    where the application itself commits partway through (which
    otherwise causes problems with nested test transactions).
    """
    async with AsyncSessionLocal() as session:
        for tabelle in reversed(Base.metadata.sorted_tables):
            await session.execute(tabelle.delete())
        await session.commit()
    yield


class CsrfAwareClient(AsyncClient):
    """Behaves like a browser that actually loaded the form it submits:
    it holds the CSRF cookie and mirrors the token back on every unsafe
    request (see app/csrf.py).

    Without this, adding CSRF protection would have meant editing every
    POST in the whole test suite to fetch a token first -- which tests
    the plumbing, not the behaviour each test is about. The rejection
    path itself is covered explicitly in tests/test_security.py using
    `raw_client` below, which does none of this.
    """

    _UNSAFE = {"POST", "PUT", "PATCH", "DELETE"}

    async def request(self, method, url, **kwargs):
        if method.upper() in self._UNSAFE and not str(url).startswith("/api/"):
            token = self.cookies.get("csrf")
            if token is None:
                # Any GET mints one; the login page needs no auth.
                await super().request("GET", "/auth/login")
                token = self.cookies.get("csrf")
            headers = dict(kwargs.get("headers") or {})
            headers.setdefault("X-CSRF-Token", token or "")
            kwargs["headers"] = headers
        return await super().request(method, url, **kwargs)


@pytest_asyncio.fixture
async def client():
    """HTTP client that talks directly to the FastAPI app (no real server needed)."""
    transport = ASGITransport(app=app)
    async with CsrfAwareClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def raw_client():
    """Like `client`, but without the automatic CSRF token -- for tests
    that check what happens to a request that doesn't carry one."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_user():
    """Creates an admin user and returns it."""
    async with AsyncSessionLocal() as session:
        user = User(
            email="admin@example.com",
            name="Test-Admin",
            password_hash=hash_password("testpasswort123"),
            role=UserRole.ADMIN,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def board_user():
    """A second user with the board role (for four-eyes-principle tests)."""
    async with AsyncSessionLocal() as session:
        user = User(
            email="vorstand@example.com",
            name="Test-Vorstand",
            password_hash=hash_password("testpasswort123"),
            role=UserRole.BOARD,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def second_board_user():
    """A third user with the board role (for tests that need 2 different approvers)."""
    async with AsyncSessionLocal() as session:
        user = User(
            email="vorstand2@example.com",
            name="Test-Vorstand Zwei",
            password_hash=hash_password("testpasswort123"),
            role=UserRole.BOARD,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def login(client: AsyncClient, email: str, password: str = "testpasswort123") -> str:
    """Helper function: logs a user in and returns the JWT access token."""
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
