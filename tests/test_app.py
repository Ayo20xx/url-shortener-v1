import asyncio
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite://")

from app.main import app
from app.model import Clicks, Url
from app.schema import UrlCreate, UrlUpdate
from app.services import (
    analytics,
    create_url_service,
    delete_url,
    get_url_service,
    update_url_service,
)


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.fixture
def session_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
    )

    async def setup():
        async with engine.begin() as connection:
            await connection.execute(text("PRAGMA foreign_keys=ON"))
            await connection.run_sync(SQLModel.metadata.create_all)

    run(setup())
    factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield factory
    run(engine.dispose())


def test_create_and_duplicate_shortcode(session_factory):
    async def scenario():
        async with session_factory() as session:
            created = await create_url_service(
                UrlCreate(
                    url="https://example.com",
                    custom_shortcode="example",
                ),
                session,
            )
            assert created.shortcode == "example"

            with pytest.raises(HTTPException) as error:
                await create_url_service(
                    UrlCreate(
                        url="https://example.org",
                        custom_shortcode="example",
                    ),
                    session,
                )
            assert error.value.status_code == 409

    run(scenario())


def test_create_distinguishes_omitted_and_explicit_null_expiration(session_factory):
    async def scenario():
        async with session_factory() as session:
            omitted = await create_url_service(
                UrlCreate(url="https://example.com", custom_shortcode="default"),
                session,
            )
            explicit_null = await create_url_service(
                UrlCreate(
                    url="https://example.org",
                    custom_shortcode="never",
                    expires_at=None,
                ),
                session,
            )

            assert omitted.expires_at is not None
            assert explicit_null.expires_at is None

    run(scenario())


def test_redirect_records_click_and_analytics_counts(session_factory):
    async def scenario():
        async with session_factory() as session:
            created = await create_url_service(
                UrlCreate(url="https://example.com", custom_shortcode="go"),
                session,
            )
            response = await get_url_service(created.shortcode, session)
            result = await analytics(created.shortcode, session)

            assert response.status_code == 302
            assert response.headers["location"] == "https://example.com/"
            assert result == {"shortcode": "go", "clicks": 1}

    run(scenario())


def test_expired_url_is_rejected_and_null_expiration_does_not_expire(
    session_factory,
):
    async def scenario():
        async with session_factory() as session:
            expired = await create_url_service(
                UrlCreate(
                    url="https://example.com",
                    custom_shortcode="expired",
                ),
                session,
            )
            expired.expires_at = expired.created_at
            session.add(expired)
            await session.commit()

            with pytest.raises(HTTPException) as error:
                await get_url_service("expired", session)
            assert error.value.status_code == 410

            never_expires = Url(
                url="https://example.org",
                shortcode="forever",
                expires_at=None,
            )
            session.add(never_expires)
            await session.commit()
            response = await get_url_service("forever", session)
            assert response.status_code == 302

    run(scenario())


def test_update_url_and_shortcode_and_reject_duplicate_shortcode(session_factory):
    async def scenario():
        async with session_factory() as session:
            first = await create_url_service(
                UrlCreate(url="https://example.com", custom_shortcode="first"),
                session,
            )
            second = await create_url_service(
                UrlCreate(url="https://example.org", custom_shortcode="second"),
                session,
            )

            updated = await update_url_service(
                "first",
                session,
                UrlUpdate(url="https://example.net"),
            )
            assert updated.shortcode == "first"
            assert updated.url == "https://example.net/"

            updated = await update_url_service(
                "first",
                session,
                UrlUpdate(custom_shortcode="renamed"),
            )
            assert updated.shortcode == "renamed"

            with pytest.raises(HTTPException) as error:
                await update_url_service(
                    "renamed",
                    session,
                    UrlUpdate(custom_shortcode=second.shortcode),
                )
            assert error.value.status_code == 409

            same_shortcode = await update_url_service(
                "renamed",
                session,
                UrlUpdate(custom_shortcode="renamed"),
            )
            assert same_shortcode.shortcode == "renamed"
            assert first.id == same_shortcode.id

    run(scenario())


def test_delete_cascades_clicks(session_factory):
    async def scenario():
        async with session_factory() as session:
            created = await create_url_service(
                UrlCreate(url="https://example.com", custom_shortcode="remove"),
                session,
            )
            await get_url_service(created.shortcode, session)
            await delete_url(created.shortcode, session)

            url_count = await session.scalar(
                select(func.count(Url.id)).where(Url.id == created.id)
            )
            click_count = await session.scalar(
                select(func.count(Clicks.id)).where(Clicks.url_id == created.id)
            )
            assert url_count == 0
            assert click_count == 0

    run(scenario())


def test_pagination_rejects_invalid_bounds():
    with TestClient(app) as client:
        assert client.get("/urls?skip=-1").status_code == 422
        assert client.get("/urls?limit=0").status_code == 422
        assert client.get("/urls?limit=101").status_code == 422


def test_missing_database_url_fails_clearly():
    result = subprocess.run(
        [sys.executable, "-c", "import config"],
        cwd=Path(__file__).parents[1],
        env={key: value for key, value in os.environ.items() if key != "DATABASE_URL"},
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "DATABASE_URL must be set" in result.stderr


def test_clean_alembic_migration_creates_both_tables(tmp_path):
    database_path = tmp_path / "migration.db"
    environment = os.environ | {"DATABASE_URL": f"sqlite:///{database_path}"}
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).parents[1],
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )

    with sqlite3.connect(database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
    assert {"url", "clicks", "alembic_version"} <= tables
