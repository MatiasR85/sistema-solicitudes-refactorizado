from fastapi import FastAPI
from src.routers.router import router as solicitudes_router

app = FastAPI(title="Gestión de Solicitudes Académicas", version="1.0.0")

app.include_router(solicitudes_router)

@app.get("/")
def inicio():
    return {"mensaje": "API de Gestión de Solicitudes Académicas", "documentacion": "/docs"}

