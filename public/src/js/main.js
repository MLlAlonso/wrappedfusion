document.addEventListener('DOMContentLoaded', () => {
    console.log('Spotify Fusion Service frontend principal cargado.');

    const spotifyAuthBtn = document.getElementById('spotify-auth-btn');
    const syncSpotifyBtn = document.getElementById('sync-spotify-btn');
    const authStatusMessage = document.getElementById('auth-status-message');

    // Elementos para mostrar estadísticas de Spotify
    const spotifyMinutesEl = document.getElementById('spotify-minutes');
    const spotifyTopSongsEl = document.getElementById('spotify-top-songs');
    const spotifyTopArtistsEl = document.getElementById('spotify-top-artists');
    const spotifyLikedTracksEl = document.getElementById('spotify-liked-tracks');
    const spotifyPlaylistsEl = document.getElementById('spotify-playlists');

    // Gráfica de minutos
    const minutesChartCtx = document.getElementById('minutesChart').getContext('2d');

    // --- Constantes de Backend ---
    const BACKEND_BASE_URL = 'http://127.0.0.1:8000';

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

    const SPOTIFY_CLIENT_ID = "f4ceb63f51eb44be94f633d8666c26e1";
    const SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/static/callback/spotify.html";
    const SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize";
    const SPOTIFY_SCOPES = [
        "user-read-private", "user-read-email", "user-read-recently-played",
        "user-library-read", "playlist-read-private", "playlist-read-collaborative",
        "user-top-read"
    ].join(' ');

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

    // --- Lógica para sincronizar datos de Spotify ---
    async function syncSpotifyData() {
        authStatusMessage.style.color = '#3498db';
        authStatusMessage.textContent = 'Sincronizando datos de Spotify... Por favor, espera.';
        try {
            const userId = 1;

            const response = await fetch(`${BACKEND_BASE_URL}/api/v1/spotify/sync_data/${userId}`, {
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
            
            loadSpotifyStats(); // Recargar estadísticas después de sincronizar

        } catch (error) {
            console.error('Error al sincronizar datos de Spotify:', error);
            authStatusMessage.style.color = 'red';
            authStatusMessage.textContent = `Error al sincronizar Spotify: ${error.message}`;
        }
    }

    // --- Lógica para cargar y mostrar estadísticas de Spotify ---
    async function loadSpotifyStats() {
        try {
            const userId = 1;
            const response = await fetch(`${BACKEND_BASE_URL}/api/v1/spotify/stats/${userId}`);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`HTTP error! status: ${response.status}. Detail: ${errorData.detail || 'No detail.'}`);
            }
            const data = await response.json();
            console.log('Estadísticas de Spotify cargadas:', data);

            // Actualizar el DOM con los datos de Spotify
            spotifyMinutesEl.textContent = `${data.total_spotify_minutes || 0} minutos`;
            
            spotifyTopSongsEl.innerHTML = data.top_10_tracks.map(track => `<li>${track.title} (${track.play_count} reproducciones)</li>`).join('');
            if (data.top_10_tracks.length === 0) spotifyTopSongsEl.innerHTML = '<li>No hay canciones top disponibles aún.</li>';

            spotifyTopArtistsEl.innerHTML = data.top_5_artists.map(artist => `<li>${artist.name} (${artist.play_count} reproducciones)</li>`).join('');
            if (data.top_5_artists.length === 0) spotifyTopArtistsEl.innerHTML = '<li>No hay artistas top disponibles aún.</li>';

            spotifyLikedTracksEl.innerHTML = data.liked_tracks.map(track => `<li>${track.title}</li>`).join('');
            if (data.liked_tracks.length === 0) spotifyLikedTracksEl.innerHTML = '<li>No hay canciones favoritas disponibles.</li>';

            spotifyPlaylistsEl.innerHTML = data.playlists.map(playlist => `<li>${playlist}</li>`).join('');
            if (data.playlists.length === 0) spotifyPlaylistsEl.innerHTML = '<li>No hay playlists disponibles.</li>';

            // Actualizar gráfica de minutos
            updateMinutesChart(data.total_spotify_minutes || 0);

        } catch (error) {
            console.error('Error al cargar estadísticas de Spotify:', error);
            if (spotifyMinutesEl) {
                spotifyMinutesEl.textContent = 'Error al cargar los datos.';
            }
        }
    }

    // Actualizar gráfica de minutos
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


    // --- Event Listeners ---
    if (spotifyAuthBtn) {
        spotifyAuthBtn.addEventListener('click', initiateSpotifyAuth);
    }

    if (syncSpotifyBtn) {
        syncSpotifyBtn.addEventListener('click', syncSpotifyData);
    }

    // Cargar estadísticas de Spotify al iniciar la página principal
    if (window.location.pathname !== '/static/callback/spotify.html') {
        loadSpotifyStats();
    }
});