from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Estilo(Base):
    __tablename__ = "estilos"
    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, unique=True, index=True, nullable=False)
    descripcion = Column(String, nullable=False)
    tecnicas    = Column(String, nullable=False)
    
    # Relación con history
    history_entries = relationship("History", back_populates="estilo")

class History(Base):
    __tablename__ = "history"
    id               = Column(Integer, primary_key=True, index=True)
    estilo_id        = Column(Integer, ForeignKey("estilos.id"), nullable=False)
    image_path       = Column(Text)
    confidence_score = Column(DECIMAL(5,4))
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    client_ip        = Column(Text)
    user_agent       = Column(Text)
    device_uuid      = Column(UUID, nullable=False)
    device_type      = Column(String)
    
    # Relación con estilo
    estilo = relationship("Estilo", back_populates="history_entries")
