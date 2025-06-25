# WrappedFusion 🎧📺

**WrappedFusion** es una plataforma interactiva que unifica y visualiza tus estadísticas musicales de **Spotify** y **YouTube Music**. Inspirado en los "Wrapped" de fin de año, pero disponible todo el tiempo.

---

## 🧠 Características

- Autenticación vía OAuth 2.0 (Spotify & YouTube)
- Visualización de minutos escuchados por plataforma
- Top 10 canciones y Top 5 artistas
- Listado de playlists y canciones favoritas
- Fusión de datos de ambas plataformas
- Visualizaciones interactivas con Chart.js
- Actualizaciones automáticas mediante tareas programadas
- Arquitectura desacoplada Frontend/Backend

---

## 🚀 Stack Tecnológico

| Componente        | Tecnología                                         |
|-------------------|---------------------------------------------------|
| **Backend**       | Python + FastAPI                                  |
| **Frontend**      | HTML5 + SASS + Vanilla JS                         |
| **Base de Datos** | MySQL                                             |
| **OAuth 2.0**     | Spotify API, Google OAuth + YouTube Data API v3   |
| **Gráficas**      | Chart.js                                          |
| **ORM**           | SQLAlchemy                                        |
| **Tareas**        | APScheduler / Cron                                |
| **Logs**          | Python `logging` module                           |

---

## 📦 Instalación (Desarrollo)

1. Clona el repositorio:
    ```bash
    git clone https://github.com/tu_usuario/wrappedfusion.git
    cd wrappedfusion
    ```

2. Instala dependencias del backend:
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. Configura variables de entorno (`.env`):
    ```
    SPOTIFY_CLIENT_ID=...
    SPOTIFY_CLIENT_SECRET=...
    YOUTUBE_CLIENT_ID=...
    YOUTUBE_CLIENT_SECRET=...
    DATABASE_URL=mysql+mysqlconnector://user:pass@localhost/dbname
    ```

4. Corre el backend:
    ```bash
    uvicorn main:app --reload
    ```

---

---

## 🔒 Licencia

Este proyecto se distribuye bajo la Licencia MIT.  
Solo para uso personal y educativo. No se permite reproducción ni monetización.

---

## 👨‍💻 Autor

**Mikkel Alonso**  
Desarrollador Full Stack, apasionado por la música, la tecnología y los proyectos personales con impacto.

---

## 🧠 Estado del Proyecto

- MVP planeado ✔️
- Exploración de APIs completada 🧪
- En desarrollo 🚧
- Próximos pasos: Visualización avanzada 📅