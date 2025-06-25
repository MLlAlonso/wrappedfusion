from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db

router = APIRouter()

@router.get("/health", summary="Verificar el estado de la API")
async def health_check(db: Session = Depends(get_db)):
    """
    Endpoint para verificar el estado de salud de la aplicación.
    """
    try:
        db.execute(text("SELECT 1"))
        db.commit()
        db_status = "ok"
    except Exception as e:
        db.rollback()
        db_status = f"error: {e}"

    return {
        "status": "ok",
        "database": db_status,
        "message": "API de WrappedFusion funcionando correctamente!"
    }