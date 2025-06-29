from sqlalchemy.orm import Session
from uuid import UUID
from app.models import Estilo, History
from app.schemas import EstiloCreate, HistoryCreate

def get_estilos(db: Session) -> list[Estilo]:
    return db.query(Estilo).all()

def get_estilo_by_id(db: Session, estilo_id: int):
    return db.query(Estilo).filter(Estilo.id == estilo_id).first()

def get_estilo_by_nombre(db: Session, nombre: str):
    return db.query(Estilo).filter(Estilo.nombre == nombre).first()

def create_estilo(db: Session, estilo_in: EstiloCreate):
    db_estilo = Estilo(**estilo_in.model_dump())
    db.add(db_estilo)
    db.commit()
    db.refresh(db_estilo)
    return db_estilo

# Funciones para History
def create_history_entry(db: Session, history_in: HistoryCreate):
    db_history = History(**history_in.model_dump())
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_history_entries(db: Session, device_uuid: str = None, skip: int = 0, limit: int = 100):
    query = db.query(History)
    if device_uuid:
        # Convert string to UUID for filtering
        device_uuid_obj = UUID(device_uuid)
        query = query.filter(History.device_uuid == device_uuid_obj)
    return query.offset(skip).limit(limit).all()

def get_history_by_estilo(db: Session, estilo_id: int, skip: int = 0, limit: int = 100):
    return db.query(History).filter(History.estilo_id == estilo_id).offset(skip).limit(limit).all()

def get_history_stats(db: Session):
    """Obtiene estadísticas del historial"""
    total_predictions = db.query(History).count()
    # Aquí puedes agregar más estadísticas según necesites
    return {"total_predictions": total_predictions}
