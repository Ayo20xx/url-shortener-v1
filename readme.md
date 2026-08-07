# URL Shortener

A backend service that takes a long URL and returns a short, unique code that redirects to the original URL.

## Features (MVP)
- `POST /shorten` — accepts a long URL, returns a short code
- `GET /{code}` — redirects to the original URL
- Collision handling for generated short codes
- Persistent storage (database, not in-memory)
- Rate limiting (stop abuse)
- Logging
- Analytics (click tracking)
- Custom aliases
- Expiration dates

## Tech Stack
- **Language/Framework:** Python (FastAPI)
- **Database:** PostgreSQL, Redis

## How to Run Locally

1. Clone the repo
   ```bash
   git clone <repo-url>
   cd url-shortener
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables (see `.env.example`)

4. Run the server
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## API Example

**Shorten a URL**
```
POST /shorten
Body: { "url": "https://example.com/very/long/path" }
Response: { "short_code": "abc123" }
```

**Redirect**
```
GET /abc123
→ redirects to https://example.com/very/long/path
```

## Design Decisions
See [TRADEOFFS.md](./TRADEOFFS.md) for reasoning behind key technical choices.

## Status
🚧 In progress