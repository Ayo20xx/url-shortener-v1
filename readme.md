# URL Shortener API

Create short URLs, redirect to their destinations, and view click totals.

- **Live API:** [https://url-shortener-v1-l0ld.onrender.com](https://url-shortener-v1-l0ld.onrender.com/)
- **Swagger docs:** [https://url-shortener-v1-l0ld.onrender.com/docs](https://url-shortener-v1-l0ld.onrender.com/docs)

## Create a shortened URL

Send a `POST` request to `/urls`. `custom_shortcode` is optional. If supplied, it must be unique and determines the code in the shortened URL. If omitted, the API generates a shortcode automatically.

`expires_at` is optional and accepts an ISO 8601 datetime. The date below is illustrative only; use an appropriate future date and time when testing. If `expires_at` is omitted, the URL expires after 30 days. Set it to `null` for a URL that does not expire.

```bash
curl -X POST 'https://url-shortener-v1-l0ld.onrender.com/urls' \
  -H 'Content-Type: application/json' \
  -d '{
    "custom_shortcode": "my-github",
    "url": "https://github.com/Ayo20xx/url-shortener-v1/",
    "expires_at": "2026-10-01T12:00:00"
  }'
```

Example response:

```json
{
  "id": 1,
  "url": "https://github.com/Ayo20xx/url-shortener-v1/",
  "shortcode": "my-github",
  "created_at": "2026-09-28T12:00:00Z",
  "expires_at": "2026-10-01T12:00:00Z"
}
```

The shortened URL is:

`https://url-shortener-v1-l0ld.onrender.com/urls/my-github`

Open that URL in a browser to test the redirect. The endpoint responds with HTTP `302` and redirects to the original URL. In this deployed API, the redirect path includes `/urls/`.

## Endpoints

- `POST /urls` — create a URL.
- `GET /urls` — list URLs. Supports `skip` and `limit` query parameters.
- `GET /urls/{shortcode}` — redirect to the destination and record a click.
- `PATCH /urls/{shortcode}` — update a URL by shortcode.
- `DELETE /urls/{shortcode}` — delete a URL by shortcode.
- `GET /analytics?shortcode={shortcode}` — return the click total for a shortcode.