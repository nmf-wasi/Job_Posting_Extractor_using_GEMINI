from fastapi import FastAPI
from app import llm
from app.routers import extract

app = FastAPI(title="Job Posting Extractor")

app.include_router(extract.router, prefix="/llm", tags=["llm"])


@app.get("/")
def home():
    return {"author": "nmf_wasi"}

@app.get("/health")
def health():
    return {"status": "ok"}