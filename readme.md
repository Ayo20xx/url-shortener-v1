# URL Shortener

This project is a small FastAPI service for creating short codes that redirect to longer URLs. The current implementation stores URL records in PostgreSQL and tracks redirect counts in a `clicks` table.

## Current status

This repo is a working MVP for:

- Creating URL records with generated or custom short codes
- Listing saved URLs
- Redirecting a shortcode to its destination URL
- Updating and deleting URL entries
- Counting total clicks for a shortcode

The app does not currently implement authentication, Redis-backed rate limiting, or production hardening. See [production.md](./production.md) for the current checklist and remaining work.

## Tech stack

- Python
- FastAPI
- SQLModel + SQLAlchemy
- PostgreSQL
- Alembic
- Python dotenv

## Local setup

1. Clone the repository and enter the project directory.

   ```bash
   git clone <repo-url>
   cd url-shortener
   ```

2. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the app dependencies.

   Install the runtime dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a local PostgreSQL database.

   Example:

   ```bash
   createdb url_shortener
   ```

5. Copy the example environment file and set the database URL.

   ```bash
   cp .env.example .env
   ```

6. Run the database migrations.

   ```bash
   alembic upgrade head
   ```

7. Start the API.

   ```bash
   uvicorn app.main:app --reload
   ```

For development and tests, install the additional test dependencies and run:

```bash
pip install -r requirements-dev.txt
python -m pytest
```

The app will be available at `http://localhost:8000`, and the interactive docs are at `http://localhost:8000/docs`.

## Environment variables

The app reads `DATABASE_URL` from a `.env` file through `config.py`.

Example value:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/url_shortener
```

The repository includes a safe template at [.env.example](./.env.example).

## API overview

The routes in the current app are:

### Create a URL

`POST /urls`

Request body:

```json
{
  "url": "https://example.com/very/long/path",
  "custom_shortcode": "example",
  "expires_at": "2026-10-01T12:00:00"
}
```

`custom_shortcode` and `expires_at` are optional. New URLs default to a
30-day expiration; an updated URL with `expires_at: null` does not expire.

Response:

```json
{
  "id": 1,
  "url": "https://example.com/very/long/path",
  "shortcode": "example",
  "expires_at": "2026-10-01T12:00:00",
  "created_at": "2026-09-21T12:00:00"
}
```

### List URLs

`GET /urls?skip=0&limit=10`

### Redirect to a URL

`GET /urls/{shortcode}`

This endpoint responds with an HTTP redirect to the original URL.

### Update a URL

`PATCH /urls/{shortcode}`

Request body may include any subset of `url`, `custom_shortcode`, and
`expires_at`.

### Delete a URL

`DELETE /urls/{shortcode}`

Deleting a URL also deletes its click records.

### Basic analytics

`GET /analytics?shortcode={shortcode}`

This returns the total click count for the shortcode.

## Planned work

The following items are documented in [production.md](./production.md) but are not implemented in the current app yet:

- Authentication and authorization
- Redis-backed rate limiting
- Production security and hardening
- Docker and deployment setup
- Automated tests and CI
- A separate `TRADEOFFS.md` document

## Status

🚧 In progress
