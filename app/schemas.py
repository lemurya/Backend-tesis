from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

class EstiloBase(BaseModel):
    nombre:      str
    descripcion: str
    tecnicas:    str

class EstiloCreate(EstiloBase):
    pass

class Estilo(EstiloBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PredictionResponse(BaseModel):
    predicted: Estilo
    model_config = ConfigDict(from_attributes=True)

# Schema para respuesta de predicción con imagen
class PredictionWithImageResponse(BaseModel):
    estilo: Estilo
    image_path: str
    image_url: str
    model_config = ConfigDict(from_attributes=True)

# Schemas para History
class HistoryBase(BaseModel):
    estilo_id: int
    image_path: Optional[str] = None
    confidence_score: Optional[Decimal] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

class HistoryCreate(HistoryBase):
    pass

class History(HistoryBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class HistoryWithEstilo(History):
    estilo: Estilo
    image_url: Optional[str] = None  # URL completa para acceder a la imagen
    model_config = ConfigDict(from_attributes=True)
