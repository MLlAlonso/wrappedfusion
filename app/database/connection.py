from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG_MODE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Proporciona una sesión de base de datos para las dependencias de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_tables():
    """
    Crea todas las tablas definidas en los modelos.
    """
    Base.metadata.create_all(bind=engine)
    print("Tablas de la base de datos creadas o actualizadas.")