# WrappedFusion: Spotify Service

## Descripción del Proyecto

**WrappedFusion** es una plataforma personal diseñada para unificar y visualizar las estadísticas de consumo de música del usuario de diferentes servicios de streaming. Este repositorio (`wrapped-fusion-spotify-service`) es el primer microservicio implementado de una arquitectura más grande, dedicado exclusivamente a la integración con Spotify.

Este servicio expone una API para la gestión de datos de Spotify e incluye su propia interfaz de usuario (UI) para la visualización individual de las estadísticas del usuario. Puede funcionar como aplicación independiente y como componente para una futura aplicación agregadora que combinará datos de Spotify y YouTube.

---

## Características Implementadas (Spotify Service)

- **Autenticación de Usuario:**  
    Flujo OAuth 2.0 (con PKCE) con la API de Spotify. Permite a cualquier usuario de Spotify autenticarse y gestionar sus propios datos.

- **Gestión de Datos:**  
    Sincronización y persistencia de datos del usuario de Spotify en una base de datos MySQL, incluyendo:
    - Historial de reproducción reciente (últimas 50 canciones)
    - Canciones marcadas como "Me gusta"
    - Listas de reproducción (playlists)

- **Cálculo de Estadísticas:**  
    Procesamiento de los datos sincronizados para generar:
    - Minutos totales escuchados
    - Top 10 canciones más reproducidas
    - Top 5 artistas más reproducidos

- **Interfaz de Usuario (UI) Propia:**  
    - Visualización de estadísticas en un diseño oscuro y atractivo
    - Imágenes de portada para canciones y fotos para artistas (imagen arriba, texto debajo)
    - Visualización de nombres de playlists (con marcadores de posición para imágenes si no están disponibles)
    - Botones para "Autenticar con Spotify", "Sincronizar Datos" y "Cerrar Sesión"

- **Base de Datos Relacional:**  
    Utiliza MySQL para la persistencia de datos, con un esquema diseñado para la multi-tenencia (cada usuario ve sus propios datos).
---

## Stack Tecnológico

- **Backend:** Python 3.10+ (`FastAPI`, `SQLAlchemy`, `httpx`, `pymysql`)
- **Frontend:** HTML5, SASS (compilado a CSS), JavaScript (Vanilla JS, Chart.js para gráficas)
- **Base de Datos:** MySQL
- **Control de Versiones:** Git

---

## Ejecución del Proyecto en Local

### Prerrequisitos

Asegúrate de tener instalado lo siguiente:
- Python 3.10+: [Descargar Python](https://www.python.org/downloads/)
- MySQL Server
- Git: [Descargar Git](https://git-scm.com/downloads)
- Visual Studio Code (Recomendado) con la extensión "Live Sass Compiler"
---

### Pasos de Configuración

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/wrapped-fusion-spotify-service.git
cd wrapped-fusion-spotify-service
```

#### 2. Configurar el Entorno Virtual

```bash
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

#### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```
Si el archivo `requirements.txt` no está actualizado o falta:

```bash
pip install "fastapi[all]" uvicorn python-dotenv sqlalchemy pymysql httpx
pip freeze > requirements.txt
```

#### 4. Configurar el Archivo de Variables de Entorno (`.env`)

Crea un archivo llamado `.env` en la raíz del proyecto.  
Ejemplo de contenido:

```env
# .env para wrapped-fusion-spotify-service (LOCAL)

# --- Configuración General del Proyecto ---
PROJECT_NAME="Spotify Fusion Service"
PROJECT_VERSION="0.1.0"
DEBUG_MODE=True

# --- Configuración de la Base de Datos MySQL Local ---
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=spotify_fusion_db

# --- Credenciales de Spotify API (OAuth 2.0) ---
SPOTIFY_CLIENT_ID=tu_spotify_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_spotify_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/static/callback/spotify.html

# --- Clave Secreta para JWT/Cifrado ---
SECRET_KEY=tu_clave_secreta_generada_aqui_para_spotify_service

# --- Opcional: Clave para comunicación interna ---
INTERNAL_API_KEY=tu_clave_interna_segura_para_comunicacion
```

> **Importante:** Asegúrate de que `SPOTIFY_REDIRECT_URI` esté configurado también en tu Dashboard de Spotify.

---

#### 5. Configurar la Base de Datos MySQL

- Abre tu cliente MySQL.
- Crea la base de datos:

```sql
CREATE DATABASE spotify_fusion_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

- Ejecuta el script para crear las tablas del proyecto:

```bash
python create_db.py
```

- Comandos útiles para mantenimiento (¡borrarán todos los datos!):

```sql
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE spotify_playlist_tracks;
TRUNCATE TABLE spotify_liked_tracks;
TRUNCATE TABLE spotify_play_history;
TRUNCATE TABLE track_artists;
TRUNCATE TABLE spotify_playlists;
TRUNCATE TABLE tracks;
TRUNCATE TABLE artists;
TRUNCATE TABLE user_spotify_history_summary;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

ALTER TABLE users AUTO_INCREMENT = 1;
ALTER TABLE artists AUTO_INCREMENT = 1;
ALTER TABLE tracks AUTO_INCREMENT = 1;
ALTER TABLE spotify_playlists AUTO_INCREMENT = 1;
ALTER TABLE spotify_play_history AUTO_INCREMENT = 1;
ALTER TABLE spotify_liked_tracks AUTO_INCREMENT = 1;
```

- Para añadir columnas de imagen sin borrar datos:

```sql
ALTER TABLE artists ADD COLUMN image_url VARCHAR(512) NULL;
ALTER TABLE tracks ADD COLUMN album_image_url VARCHAR(512) NULL;
ALTER TABLE spotify_playlists ADD COLUMN image_url VARCHAR(512) NULL;
```

---

#### 6. Compilar SASS a CSS

- Instala la extensión "Live Sass Compiler" en VS Code.
- Abre `public/src/styles/main.scss`.
- Haz clic en "Watch Sass" en la barra de estado inferior de VS Code.

---

## Ejecutar el Servicio

Con el entorno virtual activo:

```bash
uvicorn app.main:app --reload
```

- Accede a la aplicación en: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### Flujo de Uso

1. Haz clic en "Autenticar con Spotify".
2. Completa la autorización en Spotify.
3. Serás redirigido de nuevo a la aplicación.
4. Haz clic en "Sincronizar Datos" para poblar tus estadísticas.

---

## Nota sobre Despliegue en Producción (PythonAnywhere)

Se intentó desplegar este proyecto en PythonAnywhere, pero se encontraron desafíos con la configuración del servidor web y la base de datos. Por ahora, el proyecto está optimizado para ejecución local.

---

## Próximos Pasos

Una vez que el `wrapped-fusion-spotify-service` funcione perfectamente en local, el siguiente paso será desarrollar el microservicio de YouTube (`wrapped-fusion-youtube-service`) y, finalmente, el proyecto agregador (`wrapped-fusion-aggregator-frontend`) para combinar ambas experiencias.