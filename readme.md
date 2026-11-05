# URL Shortener API

A REST API built with FastAPI that creates short URLs, redirects to their
destinations, supports expiration dates, and tracks click totals.

## Features

- Create short URLs with a custom shortcode or a randomly generated shortcode.
- Set a custom expiration date, use the 30-day default, or disable expiration.
- Redirect to the destination with HTTP `302` and record each successful click.
- View click totals for a shortcode.
- List URLs with pagination, update URLs, and delete URLs.
- Reject duplicate and reserved custom shortcodes.

## Tech Stack

- **FastAPI** for the HTTP API and interactive OpenAPI documentation.
- **SQLModel** and **SQLAlchemy async** for database models and access.
- **PostgreSQL** for the application database; the automated tests use SQLite.
- **Alembic** for database migrations.
- **pytest** for automated tests.

## Run Locally

Requirements: Python 3.10+, pip, and a running PostgreSQL database.

```bash
git clone https://github.com/Ayo20xx/url-shortener-v1.git
cd url-shortener-v1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Set `DATABASE_URL` in `.env` to your PostgreSQL async SQLAlchemy database URL.
For example:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/url_shortener
```

Create the `url_shortener` database if it does not exist, then apply migrations
and start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

The API is available at <http://localhost:8000>. Interactive Swagger
documentation is available at <http://localhost:8000/docs>.

Keep real credentials out of source control.

## Run with Docker

Docker must be installed, and a PostgreSQL database must already be reachable
from the container. Set `DATABASE_URL` in `.env` to that database. If PostgreSQL
runs directly on your Mac or Windows host, use `host.docker.internal` instead
of `localhost` as the hostname.

Build the image and start the API in one command:

```bash
docker build -t url-shortener . && docker run --rm --name url-shortener \
  -p 8000:8000 --env-file .env url-shortener
```

The container applies Alembic migrations before starting the API. Visit
<http://localhost:8000/docs> when the container is running.

## Quick Start

Create a URL that uses the default 30-day expiration:

```bash
curl -X POST 'http://localhost:8000/urls' \
  -H 'Content-Type: application/json' \
  -d '{
    "custom_shortcode": "mygithub",
    "url": "https://github.com/Ayo20xx/url-shortener-v1/"
  }'
```

Example response:

```json
{
  "id": 1,
  "url": "https://github.com/Ayo20xx/url-shortener-v1/",
  "shortcode": "mygithub",
  "created_at": "2026-11-01T12:00:00Z",
  "expires_at": "2026-12-01T12:00:00Z"
}
```

Follow the redirect:

```bash
curl -i 'http://localhost:8000/urls/mygithub'
```

The response is HTTP `302` with a `Location` header pointing to the destination.
Each successful redirect records one click.

Get the click total:

```bash
curl 'http://localhost:8000/analytics?shortcode=mygithub'
```

Example response:

```json
{
  "shortcode": "mygithub",
  "clicks": 1
}
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/urls` | Create a short URL |
| `GET` | `/urls` | List URLs; accepts `skip` and `limit` query parameters |
| `GET` | `/urls/{shortcode}` | Redirect to the destination and record a click |
| `PATCH` | `/urls/{shortcode}` | Update the destination, shortcode, or expiration |
| `DELETE` | `/urls/{shortcode}` | Delete a URL and its click records |
| `GET` | `/analytics?shortcode={shortcode}` | Return the click total |

### Create request fields

| Field | Required | Behavior |
|-------|----------|----------|
| `url` | Yes | HTTP or HTTPS destination URL |
| `custom_shortcode` | No | Unique, alphanumeric shortcode of up to 10 characters; generated if omitted |
| `expires_at` | No | ISO 8601 datetime; omitted defaults to 30 days, while `null` means no expiration |

Generated shortcodes use a URL-safe random token. Custom shortcodes cannot be
`docs`, `health`, or `urls`.

For `PATCH`, send any fields to change. Omitted fields are left unchanged;
setting `expires_at` to `null` makes the URL non-expiring.

### Responses and errors

- Duplicate or reserved custom shortcode: `409 Conflict`.
- Invalid request data or URL: `422 Unprocessable Entity`.
- Unknown shortcode: `404 Not Found`.
- Expired URL on redirect: `410 Gone`.
- Successful redirect: `302 Found`.

The list endpoint defaults to `skip=0` and `limit=10`. `skip` must be
non-negative and `limit` must be between 1 and 100.

## Architecture

```mermaid
flowchart LR
    Client -->|HTTP request| API[FastAPI routes]
    API --> Services[URL and analytics services]
    Services --> Session[SQLAlchemy async session]
    Session --> DB[(PostgreSQL)]
    DB -->|URLs and click records| Session
    Session --> Services
    Services -->|JSON, errors, or redirect| API
    API --> Client
```

## Tradeoffs

- PostgreSQL enforces shortcode uniqueness and stores URL and click records
  durably, at the cost of requiring a database to run the service.
- Each successful redirect writes a click record, keeping totals current but
  adding a database write and storage growth to the redirect path.
- Random shortcodes are simple and compact; collision checks and retries help
  avoid duplicates, but this design is not intended for very high-volume
  multi-region use.

## Tests

Run the test suite from the activated virtual environment with:

```bash
python -m pytest
```

Tests cover shortcode uniqueness and collision handling, default and
non-expiring URLs, redirects and click analytics, expiration, updates, delete
cascades, pagination validation, configuration errors, and clean migrations.

## What I Would Add Next

- **Authentication and ownership:** Require users to sign in and only allow
  them to update or delete their own URLs. This would prevent anyone with a
  shortcode from managing another user's links.
- **Caching:** Cache frequently requested URL destination and expiration data
  to make redirects faster. Clicks would still need to be recorded on every
  successful redirect so analytics remain accurate.
- **Rate limiting:** Limit URL creation and other abuse-prone requests. A
  shared store such as Redis would keep limits consistent across multiple
  application instances.

## Current Limitations

- The API has no authentication or ownership checks; anyone who can reach the
  service can manage URLs by shortcode.
- Click totals count successful redirects and are not deduplicated by visitor.
- There is no live deployment link; run the API locally using the instructions
  above.
