# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine, SessionLocal
from app.config import settings
from app import models
from app.crud import get_estilos
from app.ml_model import init_model
import os
import gdown

MODEL_PATH = "ViTImproved_trained.pth"
GDRIVE_ID = "1vYDBecyjRa5-Z9uJVXmkNmjKec0gOlry"

def ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("Descargando modelo desde Google Drive...")
        url = f"https://drive.google.com/uc?id={GDRIVE_ID}"
        gdown.download(url, MODEL_PATH, quiet=False)
        print("Modelo descargado.")
# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clasificador de Estilos de Arte",
    version="2.0.0",
    description="API para gestionar estilos de arte y predecir el estilo a partir de una imagen.",
)

# Montar archivos estáticos para servir las imágenes subidas
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
from app.routers.estilos import router as estilos_router
from app.routers.prediction import router as prediction_router

app.include_router(estilos_router)
app.include_router(prediction_router)


@app.on_event("startup")
def load_model():

    """
    Al iniciar la aplicación, leer todos los estilos de la BD
    y darles `num_classes` al modelo antes de cargar los pesos.
    """
    ensure_model()
    db = SessionLocal()
    try:
        estilos = get_estilos(db)
        init_model(num_classes=len(estilos))
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
