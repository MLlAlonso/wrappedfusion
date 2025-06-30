from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.v1.endpoints import health
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import spotify_data

# Inicializa la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Backend para WrappedFusion: Tu Wrapped personal de Spotify y YouTube.",
    debug=settings.DEBUG_MODE
)

# Configuración de CORS
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar la carpeta 'public' para servir archivos estáticos (frontend)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent / "public"),
    name="static"
)

app.include_router(health.router, prefix="/api/v1", tags=["Health Check"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(spotify_data.router, prefix="/api/v1", tags=["Spotify Data"])

@app.get("/", response_class=HTMLResponse, summary="Servir la página principal del frontend")
async def read_root():
    html_file_path = Path(__file__).parent.parent / "public" / "index.html"
    if not html_file_path.is_file():
        return HTMLResponse("<h1>Frontend (index.html) no encontrado!</h1>", status_code=404)
    with open(html_file_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())