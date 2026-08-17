import os

from dotenv import load_dotenv

load_dotenv()

postgres_url= os.getenv("DATABASE_URL")

