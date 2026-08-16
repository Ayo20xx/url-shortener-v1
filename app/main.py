from fastapi import FastAPI
from schema import UrlCreate
app= FastAPI()

@app.post("/shorten")
def create_url(url):
    UrlCreate.model_dump()