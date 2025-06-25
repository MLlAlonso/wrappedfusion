document.addEventListener('DOMContentLoaded', () => {
    console.log('WrappedFusion frontend principal cargado.');

    const spotifyAuthBtn = document.getElementById('spotify-auth-btn');
    const googleAuthBtn = document.getElementById('google-auth-btn');
    const totalMinutesEl = document.getElementById('total-minutes');
    const generalTopSongsEl = document.getElementById('general-top-songs');
    const generalTopArtistsEl = document.getElementById('general-top-artists');
    const minutesChartCtx = document.getElementById('minutesChart').getContext('2d');
    const authStatusMessage = document.getElementById('auth-status-message'); 

    const BACKEND_BASE_URL = 'http://127.0.0.1:8000';

    // --- Lógica para Iniciar Autenticación de Spotify 
    function dec2hex(dec) {
        return ('0' + dec.toString(16)).substr(-2);
    }
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
        for (let i = 0; i < len; i++) {
            str += String.fromCharCode(bytes[i]);
        }
        return btoa(str)
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=+$/, '');
    }

    const SPOTIFY_CLIENT_ID = "f4ceb63f51eb44be94f633d8666c26e1";
    const SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/static/callback/spotify.html";
    const SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize";
    const SPOTIFY_SCOPES = [
        "user-read-private",
        "user-read-email",
        "user-read-recently-played",
        "user-library-read",
        "playlist-read-private",
        "playlist-read-collaborative",
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


    // --- Event Listeners ---
    if (spotifyAuthBtn) {
        spotifyAuthBtn.addEventListener('click', initiateSpotifyAuth);
    }

    if (googleAuthBtn) {
        googleAuthBtn.addEventListener('click', () => {
            alert('Autenticación con Google aún no implementada.');
        });
    }

    // Cargar datos de la API
    const loadStats = async () => {
        try {
            const response = await fetch(`${BACKEND_BASE_URL}/api/v1/health`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Datos de la API:', data);

            totalMinutesEl.textContent = 'Aquí irán los minutos totales (ej: 12345 minutos)';
            generalTopSongsEl.innerHTML = '<li>Canción 1</li><li>Canción 2</li>';
            generalTopArtistsEl.innerHTML = '<li>Artista A</li><li>Artista B</li>';

            new Chart(minutesChartCtx, {
                type: 'bar',
                data: {
                    labels: ['Spotify', 'YouTube', 'Total'],
                    datasets: [{
                        label: 'Minutos Escuchados',
                        data: [10000, 5000, 15000],
                        backgroundColor: [
                            'rgba(29, 185, 84, 0.6)',
                            'rgba(255, 0, 0, 0.6)',
                            'rgba(75, 192, 192, 0.6)'
                        ],
                        borderColor: [
                            'rgba(29, 185, 84, 1)',
                            'rgba(255, 0, 0, 1)',
                            'rgba(75, 192, 192, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

        } catch (error) {
            console.error('Error al cargar las estadísticas:', error);
            totalMinutesEl.textContent = 'Error al cargar los datos.';
        }
    };
    loadStats();
});