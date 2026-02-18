from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import init_db
from app.endpoints import router as api_router

app = FastAPI(title="Salud Control API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    from app.migrate import migrate
    migrate()
    init_db()

app.include_router(api_router)

# Mount uploads directory to serve files
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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
