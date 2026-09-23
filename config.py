import os

from dotenv import load_dotenv

load_dotenv()

postgres_url = os.getenv("DATABASE_URL", "").strip()
if not postgres_url:
    raise RuntimeError("DATABASE_URL must be set before starting the application.")
