# Production Implementation Checklist

This document describes what this project must implement before it is honestly production-ready. It also marks the work that will make the project strong enough to discuss in a backend interview.

## Honest Current Assessment

The project is a solid beginner MVP. You have already learned and used:

- FastAPI routes and response models
- Dependency-injected database sessions
- PostgreSQL configuration through environment variables
- SQLModel models and foreign keys
- Async SQLAlchemy sessions
- Alembic migrations
- Generated and custom shortcodes
- Redirects and click persistence

Current gaps are normal for this stage: the API contract and production
hardening are unfinished. The core migration and automated tests are now
verified locally, but this remains an early MVP.

Do not describe unfinished README features as completed. Mark them as planned until the code and tests exist.

## Phase 0: Make The Documentation Truthful

- [ ] Change the README route names from `/shorten` and `/{code}` to the routes the app actually exposes, or change the app to match the README.
- [ ] Document the current request and response JSON using the actual Pydantic schemas.
- [ ] Remove or label Redis, rate limiting, logging, analytics, auth, and expiration as planned until implemented.
- [ ] Add a real `.env.example` containing variable names only, never passwords.
- [ ] Add the missing `TRADEOFFS.md`, or remove its link from the README.
- [ ] Document the local database setup and migration commands.

## Phase 1: Finish The Core URL Shortener

### Database and migrations

- [x] Generate one clean initial migration containing both `url` and `clicks` tables.
- [x] Verify a fresh empty database can run `alembic upgrade head` successfully.
- [ ] Keep `SQLModel.metadata` assigned to Alembic `target_metadata`.
- [x] Use Alembic as the production schema owner instead of `create_all()` at startup.
- [ ] Add an index on `clicks.url_id` for analytics queries.
- [x] Cascade-delete clicks when their URL is deleted.

Commands to verify the migration workflow:

```bash
.venv/bin/alembic revision --autogenerate -m "create urls and clicks tables"
.venv/bin/alembic upgrade head
.venv/bin/alembic check
```

Review generated migrations before applying them. A clean database must create the `url` table before the `clicks` table because `clicks.url_id` references it.

### URL behavior

- [x] Enforce `expires_at` during redirects and return `410 Gone` for expired links.
- [ ] Decide whether clients can choose expiration or whether every URL always expires after 30 days.
- [ ] Validate shortcode length and allowed characters.
- [ ] Add a maximum URL length.
- [x] Reject reserved shortcodes such as `docs`, `health`, and `urls`.
- [ ] Keep the database unique constraint as the final protection against duplicate shortcodes.
- [ ] Catch uniqueness errors and retry generated shortcodes after rolling back the session.

### CRUD endpoints

- [ ] Fix the update route to use `PATCH /urls/{id}`.
- [ ] Pass a `UrlUpdate` request body into the update service.
- [x] Map `custom_shortcode` to the model field `shortcode` explicitly.
- [x] Check shortcode uniqueness when updating.
- [x] Add response models to update and delete endpoints.
- [x] Validate `skip` and `limit`, including a maximum page size.
- [ ] Use consistent error messages and status codes.

### Analytics

- [ ] Implement `GET /urls/{id}/analytics`.
- [ ] Return total clicks for the URL.
- [ ] Return `404` when the URL does not exist.
- [ ] Add daily click counts as a second analytics query.
- [ ] Test that a successful redirect records exactly one click.

## Phase 2: Add Automated Tests

Create real API or service tests before adding infrastructure. At minimum, test:

- [ ] Create a URL with a generated shortcode.
- [ ] Create a URL with a custom shortcode.
- [ ] Reject a duplicate custom shortcode with `409 Conflict`.
- [ ] Reject invalid URL input.
- [ ] Redirect an existing shortcode.
- [ ] Record one click for a successful redirect.
- [ ] Return `404` for an unknown shortcode.
- [ ] Return `410` for an expired shortcode.
- [ ] Update a URL and its shortcode.
- [ ] Delete a URL.
- [ ] Return analytics totals.
- [ ] Run migrations against a clean test database.

Useful checks:

```bash
.venv/bin/python -m py_compile app/*.py
.venv/bin/pytest
.venv/bin/alembic check
```

Add Ruff and a type checker after the behavior tests are passing:

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

## Phase 3: Make It Safe To Expose Publicly

- [ ] Add authentication before allowing users to update, delete, or inspect analytics.
- [ ] Add ownership so one user cannot manage another user's URLs.
- [ ] Add rate limiting to URL creation and other abuse-prone endpoints.
- [ ] Use Redis for shared rate-limit state when running multiple workers.
- [ ] Add abuse reporting or a disable flag for malicious destinations.
- [ ] Configure CORS for known frontend origins only.
- [ ] Add security headers at the application or reverse-proxy layer.
- [ ] Set request and response size limits.
- [ ] Never log database passwords, tokens, or unnecessary sensitive URL data.

## Phase 4: Production Operations

- [ ] Add structured application logging.
- [ ] Add `GET /health` for process health.
- [ ] Add `GET /ready` that verifies database readiness.
- [ ] Add centralized exception handling.
- [ ] Configure database pool size, timeouts, and connection recycling.
- [ ] Store production secrets in the hosting provider's secret manager.
- [ ] Run migrations as a deployment release step before starting new workers.
- [ ] Use HTTPS behind a reverse proxy.
- [ ] Add metrics for request latency, redirects, errors, clicks, and database failures.
- [ ] Configure automated database backups and test restoring one.
- [ ] Define a rollback plan for both application and migration changes.

## Phase 5: Deployment Gate

Do not call the service production-ready until all of these are true:

- [ ] A clean database is created only through Alembic.
- [ ] CI passes tests, linting, formatting, and migration checks.
- [ ] The deployed service passes health and readiness checks.
- [ ] Create, redirect, expiration, update, delete, and analytics flows work in staging.
- [ ] Authentication and ownership prevent unauthorized management actions.
- [ ] Rate limiting works across application workers.
- [ ] Logs and error monitoring are visible.
- [ ] Backups and restoration have been verified.
- [ ] A rollback procedure has been tested.

Minimum release sequence:

```bash
.venv/bin/pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/alembic check
.venv/bin/alembic upgrade head
```

## Interview-Worthy Additions

For an interview project, the most valuable additions are not ten extra services. They are clear design decisions, tests, and evidence that the system behaves correctly under failure.

- [ ] Add authentication and URL ownership.
- [ ] Add analytics with an efficient indexed query.
- [ ] Add Redis-backed rate limiting and explain why it is shared state.
- [ ] Add Docker Compose for the API, PostgreSQL, and Redis.
- [ ] Add CI with tests, linting, formatting, and migration validation.
- [ ] Add an OpenAPI-quality README with request examples and error responses.
- [ ] Add a short `TRADEOFFS.md` explaining async database access, shortcode generation, redirect status codes, expiration, and rate limiting.
- [ ] Add a load-test result for redirect traffic and explain the bottleneck.
- [ ] Add observability: structured logs, health checks, and basic metrics.
- [ ] Add a small architecture diagram showing API, PostgreSQL, Redis, and deployment flow.

Be ready to explain these interview questions:

1. Why does the database unique constraint matter if the service checks for duplicates first?
2. What happens if two requests generate the same shortcode at the same time?
3. Why is Redis useful for rate limiting across multiple workers?
4. Why should migrations run before application startup?
5. Why should expired links return `410` instead of `404`?
6. How would the redirect path behave with millions of clicks?
7. What would you monitor and how would you debug a slow redirect?

## Recommended Learning Order

Implement one phase at a time:

1. Correct the README and add `.env.example`.
2. Create and test the clean Alembic migration.
3. Fix update behavior and enforce expiration.
4. Implement analytics.
5. Add tests for every endpoint.
6. Add logging, health checks, and configuration validation.
7. Add authentication and ownership.
8. Add Redis rate limiting.
9. Add Docker, CI, deployment, monitoring, and backups.

Finishing the checklist makes the project stronger, but production readiness means the implemented behavior, tests, deployment, and operations all pass the deployment gate.
