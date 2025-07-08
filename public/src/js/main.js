document.addEventListener('DOMContentLoaded', () => {
    console.log('Spotify Fusion Service frontend principal cargado.');

    const spotifyAuthBtn = document.getElementById('spotify-auth-btn');
    const syncSpotifyBtn = document.getElementById('sync-spotify-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const authStatusMessage = document.getElementById('auth-status-message');
    const currentUserInfo = document.getElementById('current-user-info'); 
    const spotifyMinutesEl = document.getElementById('spotify-minutes');
    const spotifyTopSongsEl = document.getElementById('spotify-top-songs');
    const spotifyTopArtistsEl = document.getElementById('spotify-top-artists');
    const spotifyLikedTracksEl = document.getElementById('spotify-liked-tracks');
    const spotifyPlaylistsEl = document.getElementById('spotify-playlists');
    const minutesChartCtx = document.getElementById('minutesChart').getContext('2d');
    const BACKEND_BASE_URL = 'http://127.0.0.1:8000';
    const SPOTIFY_CLIENT_ID = "f4ceb63f51eb44be94f633d8666c26e1";
    const SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/static/callback/spotify.html";
    const SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize";
    const SPOTIFY_SCOPES = [
        "user-read-private", "user-read-email", "user-read-recently-played",
        "user-library-read", "playlist-read-private", "playlist-read-collaborative",
        "user-top-read"
    ].join(' ');

    let currentUserId = null;
    let currentSpotifyId = null;

    // --- Funciones de Utilidad para PKCE ---
    function dec2hex(dec) { return ('0' + dec.toString(16)).substr(-2); }
    function generateRandomString() {
        const arr = new Uint8Array(32);
        window.crypto.getRandomValues(arr);
        return Array.from(arr).map(dec2hex).join('');
    }
    async function sha256(plain) {
        const encoder = new TextEncoder();
        const data = encoder.encode(plain);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        return hashBuffer;
    }
    function base64urlencode(a) {
        let str = '';
        const bytes = new Uint8Array(a);
        const len = bytes.byteLength;
        for (let i = 0; i < len; i++) { str += String.fromCharCode(bytes[i]); }
        return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    }

    // --- Lógica de Autenticación (Spotify OAuth) ---
    async function initiateSpotifyAuth() {
        const code_verifier = generateRandomString();
        localStorage.setItem('spotify_code_verifier', code_verifier);

        const hashed = await sha256(code_verifier);
        const code_challenge = base64urlencode(hashed);

        const params = new URLSearchParams({
            client_id: SPOTIFY_CLIENT_ID,
            response_type: 'code',
            redirect_uri: SPOTIFY_REDIRECT_URI,
            scope: SPOTIFY_SCOPES,
            code_challenge_method: 'S256',
            code_challenge: code_challenge,
            state: 'your_random_state_string'
        });
        window.location.href = `${SPOTIFY_AUTH_URL}?${params.toString()}`;
    }

    // --- Sincronizar datos de Spotify ---
    async function syncSpotifyData() {
        if (!currentUserId) {
            authStatusMessage.style.color = 'red';
            authStatusMessage.textContent = 'Debes autenticar con Spotify primero.';
            return;
        }
        authStatusMessage.style.color = '#3498db';
        authStatusMessage.textContent = 'Sincronizando datos de Spotify... Por favor, espera.';
        try {
            const response = await fetch(`${BACKEND_BASE_URL}/api/v1/spotify/sync_data/${currentUserId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Error en el backend: ${errorData.detail || response.statusText}`);
            }

            const data = await response.json();
            console.log("Sincronización Spotify exitosa:", data);
            authStatusMessage.style.color = 'green';
            authStatusMessage.textContent = 'Datos de Spotify sincronizados con éxito!';
            
            loadSpotifyStats();

        } catch (error) {
            console.error('Error al sincronizar datos de Spotify:', error);
            authStatusMessage.style.color = 'red';
            authStatusMessage.textContent = `Error al sincronizar Spotify: ${error.message}`;
            if (error.message.includes("404 Not Found") || error.message.includes("401 Unauthorized")) {
                authStatusMessage.textContent += " Por favor, autentica con Spotify de nuevo.";
                handleLogout();
            }
        }
    }

    // --- Cargar y mostrar estadísticas de Spotify ---
    async function loadSpotifyStats() {
        if (!currentUserId) {
            return;
        }
        try {
            const response = await fetch(`${BACKEND_BASE_URL}/api/v1/spotify/stats/${currentUserId}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}. Detail: ${errorData.detail || 'No detail.'}`);
            }
            const data = await response.json();
            console.log('Estadísticas de Spotify cargadas:', data);
            spotifyMinutesEl.textContent = `${data.total_spotify_minutes || 0} minutos`;           
            spotifyTopSongsEl.innerHTML = data.top_10_tracks.map(track => `
                <li>
                    ${track.image_url ? `<img src="${track.image_url}" alt="${track.title}" class="item-image">` : ''}
                    <div class="item-text">
                        ${track.title} (${track.play_count} reproducciones)
                    </div>
                </li>
            `).join('');
            if (data.top_10_tracks.length === 0) spotifyTopSongsEl.innerHTML = '<li>No hay canciones top disponibles aún.</li>';

            spotifyTopArtistsEl.innerHTML = data.top_5_artists.map(artist => `
                <li>
                    ${artist.image_url ? `<img src="${artist.image_url}" alt="${artist.name}" class="item-image item-image--round">` : ''}
                    <div class="item-text">
                        ${artist.name} (${artist.play_count} reproducciones)
                    </div>
                </li>
            `).join('');
            if (data.top_5_artists.length === 0) spotifyTopArtistsEl.innerHTML = '<li>No hay artistas top disponibles aún.</li>';

            spotifyLikedTracksEl.innerHTML = data.liked_tracks.map(track => `
                <li>
                    ${track.image_url ? `<img src="${track.image_url}" alt="${track.title}" class="item-image">` : ''}
                    <div class="item-text">
                        ${track.title}
                    </div>
                </li>
            `).join('');
            if (data.liked_tracks.length === 0) spotifyLikedTracksEl.innerHTML = '<li>No hay canciones favoritas disponibles.</li>';

            spotifyPlaylistsEl.innerHTML = data.playlists.map(playlist => `<li>${playlist}</li>`).join('');
            if (data.playlists.length === 0) spotifyPlaylistsEl.innerHTML = '<li>No hay playlists disponibles.</li>';

            updateMinutesChart(data.total_spotify_minutes || 0);

        } catch (error) {
            console.error('Error al cargar estadísticas de Spotify:', error);
            if (spotifyMinutesEl) {
                spotifyMinutesEl.textContent = 'Error al cargar los datos.';
            }
            if (error.message.includes("404 Not Found") || error.message.includes("401 Unauthorized")) {
                authStatusMessage.style.color = 'red';
                authStatusMessage.textContent = "Usuario no encontrado o sesión expirada. Por favor, autentica con Spotify de nuevo.";
                handleLogout();
            }
        }
    }

    let minutesChartInstance = null;
    function updateMinutesChart(spotifyMinutes) {
        const data = {
            labels: ['Spotify'],
            datasets: [{
                label: 'Minutos Escuchados',
                data: [spotifyMinutes],
                backgroundColor: ['rgba(29, 185, 84, 0.6)'],
                borderColor: ['rgba(29, 185, 84, 1)'],
                borderWidth: 1
            }]
        };

        if (minutesChartInstance) {
            minutesChartInstance.data = data;
            minutesChartInstance.update();
        } else {
            minutesChartInstance = new Chart(minutesChartCtx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
    }

    function handleLogout() {
        currentUserId = null;
        currentSpotifyId = null;
        localStorage.removeItem('user_id');
        localStorage.removeItem('spotify_id');
        authStatusMessage.style.color = 'orange';
        authStatusMessage.textContent = 'Sesión cerrada. Por favor, autentica con Spotify.';
        updateUIForLoggedOutUser();
        spotifyMinutesEl.textContent = 'Cargando...';
        spotifyTopSongsEl.innerHTML = '<li>Cargando...</li>';
        spotifyTopArtistsEl.innerHTML = '<li>Cargando...</li>';
        spotifyLikedTracksEl.innerHTML = '<li>Cargando...</li>';
        spotifyPlaylistsEl.innerHTML = '<li>Cargando...</li>';
        if (minutesChartInstance) {
            minutesChartInstance.destroy();
            minutesChartInstance = null;
        }
    }

    function updateUIForAuthenticatedUser() {
        currentUserInfo.textContent = ` ${currentSpotifyId}`;
        spotifyAuthBtn.style.display = 'none';
        syncSpotifyBtn.style.display = 'inline-block';
        logoutBtn.style.display = 'inline-block';
        document.getElementById('spotify-stats').style.display = 'block';
    }

    function updateUIForLoggedOutUser() {
        currentUserInfo.textContent = '';
        spotifyAuthBtn.style.display = 'inline-block';
        syncSpotifyBtn.style.display = 'none';
        logoutBtn.style.display = 'none';
        document.getElementById('spotify-stats').style.display = 'none';
    }

    // --- Inicialización y Event Listeners ---
    spotifyAuthBtn.addEventListener('click', initiateSpotifyAuth);
    syncSpotifyBtn.addEventListener('click', syncSpotifyData);
    logoutBtn.addEventListener('click', handleLogout);

    if (window.location.pathname === '/static/callback/spotify.html') {
    } else {
        currentUserId = localStorage.getItem('user_id');
        currentSpotifyId = localStorage.getItem('spotify_id');
        if (currentUserId && currentSpotifyId) {
            updateUIForAuthenticatedUser();
            loadSpotifyStats();
        } else {
            updateUIForLoggedOutUser();
            authStatusMessage.style.color = 'orange';
            authStatusMessage.textContent = 'Por favor, autentica con Spotify para empezar.';
        }
    }
});