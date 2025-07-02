from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os 

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    print(f"DEBUG: Intentando cargar .env desde: {BASE_DIR / '.env'}")
    print(f"DEBUG: Contenido de GOOGLE_API_KEY del entorno (antes de Pydantic): {os.getenv('GOOGLE_API_KEY')}")

    # Configuración general del proyecto
    PROJECT_NAME: str = "Spotify Fusion Service"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG_MODE: bool = True

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "spotify_fusion_db"

    DATABASE_URL: str = ""

    # Credenciales de Spotify API (OAuth 2.0), se cargan del .env
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str 

    SECRET_KEY: str
    INTERNAL_API_KEY: str

    def model_post_init(self, __context):
        self.DATABASE_URL = (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()