# app/routers/prediction.py

import os
import io
import tempfile
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from PIL import Image
from decimal import Decimal
from typing import List

from app.database import get_db
from app.crud import get_estilo_by_nombre, create_history_entry, get_history_entries, get_history_by_estilo, get_history_stats
from app.schemas import Estilo, HistoryCreate, History, HistoryWithEstilo, PredictionWithImageResponse
from app.ml_model import predict_style_from_path

router = APIRouter(tags=["predict"], prefix="")

# Configurar carpeta de uploads
UPLOADS_DIR = "uploads/predictions"
os.makedirs(UPLOADS_DIR, exist_ok=True)

def save_uploaded_image(file_content: bytes, original_filename: str) -> str:
    """
    Guarda la imagen subida y devuelve la ruta relativa
    """
    # Generar nombre único para evitar conflictos
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    file_extension = os.path.splitext(original_filename)[1] or ".jpg"
    
    # Crear nombre de archivo único
    filename = f"{timestamp}_{unique_id}{file_extension}"
    file_path = os.path.join(UPLOADS_DIR, filename)
    
    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Devolver ruta relativa para la BD
    return f"uploads/predictions/{filename}"

def get_image_url(image_path: str, request: Request) -> str:
    """
    Genera la URL completa para una imagen
    """
    if not image_path:
        return None
    
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/{image_path}"

@router.post(
    "/predict/",
    response_model=PredictionWithImageResponse,
    summary="Sube una imagen y devuelve el estilo más probable junto con la información de la imagen"
)
async def predict_upload(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validar tipo de archivo
    # if not image.content_type.startswith('image/'):
    #     raise HTTPException(400, "El archivo debe ser una imagen")
    
    # 1) Leer imagen en memoria
    contents = await image.read()
    
    # 2) Guardar imagen permanentemente
    saved_image_path = save_uploaded_image(contents, image.filename)
    
    # 3) Crear archivo temporal para predicción (el modelo necesita un archivo)
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(image.filename)[1] or ".jpg", delete=False) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # 4) Predecir el nombre del estilo
        style_name = predict_style_from_path(tmp_path)
    finally:
        os.remove(tmp_path)  # Limpiar archivo temporal

    # 5) Recuperar de la BD
    estilo = get_estilo_by_nombre(db, style_name)
    if not estilo:
        raise HTTPException(404, f"Estilo '{style_name}' no encontrado en la base de datos")

    # 6) Guardar en el historial con la ruta de la imagen
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    history_data = HistoryCreate(
        estilo_id=estilo.id,
        image_path=saved_image_path,  # Guardamos la ruta real de la imagen
        confidence_score=None,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    create_history_entry(db, history_data)

    # 7) Generar URL completa para la respuesta
    image_url = get_image_url(saved_image_path, request)

    # 8) Devolver respuesta completa
    return PredictionWithImageResponse(
        estilo=estilo,
        image_path=saved_image_path,
        image_url=image_url
    )

@router.get(
    "/predict/by-path",
    response_model=PredictionWithImageResponse,
    summary="Predice a partir de una ruta de archivo"
)
def predict_by_path(
    request: Request,
    image_path: str = Query(..., description="Ruta absoluta o relativa a la imagen"),
    db: Session = Depends(get_db)
):
    if not os.path.isfile(image_path):
        raise HTTPException(404, f"Imagen no encontrada: {image_path}")

    # 1) Predecir el nombre del estilo
    style_name = predict_style_from_path(image_path)

    # 2) Recuperar de la BD
    estilo = get_estilo_by_nombre(db, style_name)
    if not estilo:
        raise HTTPException(404, f"Estilo '{style_name}' no encontrado en la base de datos")

    # 3) Guardar en el historial
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    history_data = HistoryCreate(
        estilo_id=estilo.id,
        image_path=image_path,
        confidence_score=None,
        client_ip=client_ip,
        user_agent=user_agent
    )
    
    create_history_entry(db, history_data)

    # 4) Generar URL completa para la respuesta
    image_url = get_image_url(image_path, request)

    # 5) Devolver respuesta completa
    return PredictionWithImageResponse(
        estilo=estilo,
        image_path=image_path,
        image_url=image_url
    )

# Endpoints para consultar historial
@router.get(
    "/history/",
    response_model=List[HistoryWithEstilo],
    summary="Obtiene el historial de predicciones"
)
def get_history(
    request: Request,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de predicciones con paginación"""
    history_entries = get_history_entries(db, skip=skip, limit=limit)
    
    # Agregar URL completa a cada entrada
    for entry in history_entries:
        if hasattr(entry, 'image_path'):
            entry.image_url = get_image_url(entry.image_path, request)
    history_entries.reverse()
    return history_entries

@router.get(
    "/history/estilo/{estilo_id}",
    response_model=List[HistoryWithEstilo],
    summary="Obtiene el historial de predicciones por estilo"
)
def get_history_by_estilo_id(
    request: Request,
    estilo_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    db: Session = Depends(get_db)
):
    """Obtiene el historial de predicciones filtrado por estilo"""
    history_entries = get_history_by_estilo(db, estilo_id, skip=skip, limit=limit)
    
    # Agregar URL completa a cada entrada
    for entry in history_entries:
        if hasattr(entry, 'image_url'):
            entry.image_url = get_image_url(entry.image_path, request)
    
    return history_entries

@router.get(
    "/history/stats",
    summary="Obtiene estadísticas del historial"
)
def get_history_statistics(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales del historial"""
    return get_history_stats(db)

@router.get(
    "/image/{image_path:path}",
    summary="Obtiene la URL completa de una imagen"
)
def get_image_url_endpoint(
    request: Request,
    image_path: str
):
    """Genera la URL completa para una imagen del historial"""
    full_path = f"uploads/predictions/{image_path}"
    if not os.path.exists(full_path):
        raise HTTPException(404, "Imagen no encontrada")
    
    return {"image_url": get_image_url(full_path, request)}



