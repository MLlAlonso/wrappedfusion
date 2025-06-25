from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    # Configuración general del proyecto
    PROJECT_NAME: str = "WrappedFusion API"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG_MODE: bool = True # Cambiar a False en producción

    # Configuración de la base de datos MySQL
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "wrapped_fusion_db"

    DATABASE_URL: str = "" 

    # Configuración para las APIs de Spotify y Google (OAuth 2.0)
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/spotify/callback"

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_API_KEY: str 

    # SECRET_KEY: str = "super_secreta_clave_de_desarrollo" # ¡CAMBIAR EN PRODUCCION!

    # Configuraciones después de  inicializaciónla
    def model_post_init(self, __context):
        self.DATABASE_URL = (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()