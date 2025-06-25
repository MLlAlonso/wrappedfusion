import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.database.connection import create_db_tables
from app.database.models.user import User 

if __name__ == "__main__":
    print("Intentando crear tablas de la base de datos...")
    create_db_tables()
    print("Proceso de creación de tablas finalizado.")