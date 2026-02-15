from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db

app = FastAPI(title="Salud Control API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Salud Control API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
