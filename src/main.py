from typing import Union
from src.api.pdf_routes import router as pdf_router

from fastapi import FastAPI

app = FastAPI(title="PDF Converter API", version="0.0.1")
app.include_router(pdf_router, prefix="/pdf", tags=["PDF"])


@app.get("/")
def read_root():
    return {"root": "converter API"}
