from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/estilos", tags=["estilos"])

@router.post("/", response_model=schemas.Estilo)
def create_estilo(estilo: schemas.EstiloCreate, db: Session = Depends(get_db)):
    return crud.create_estilo(db, estilo)

@router.get("/", response_model=List[schemas.Estilo])
def read_estilos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_estilos(db)[skip: skip + limit]

@router.get("/{id}", response_model=schemas.Estilo)
def read_estilo(id: int, db: Session = Depends(get_db)):
    e = crud.get_estilo_by_id(db, id)
    if not e:
        raise HTTPException(404, "Estilo no encontrado")
    return e
