document.addEventListener('DOMContentLoaded', () => {
    console.log('Spotify Auth Callback Script cargado.');
    const authStatusMessage = document.getElementById('auth-status-message');
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

    // --- Manejo del Callback de Autenticación ---
    async function handleAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (code) {
            console.log('Código de autorización de Spotify recibido:', code);
            const code_verifier = localStorage.getItem('spotify_code_verifier');
            if (!code_verifier) {
                console.error("No se encontró el code_verifier en localStorage. Re-autentica.");
                if (authStatusMessage) authStatusMessage.textContent = 'Error: Code Verifier faltante. Por favor, re-autentica.';
                return;
            }
            try {
                const response = await fetch(`${BACKEND_BASE_URL}/api/v1/auth/spotify/callback`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code, code_verifier: code_verifier })
                });

                if (!response.ok) {
                    let errorMessage = `Error en el backend (HTTP ${response.status})`;
                    try {
                        const errorData = await response.json();
                        if (typeof errorData === 'object' && errorData !== null && 'detail' in errorData) {
                            errorMessage = `Error en el backend: ${errorData.detail}`;
                        } else {
                            errorMessage = `Error en el backend: ${JSON.stringify(errorData)}`;
                        }
                    } catch (jsonParseError) {
                        const errorText = await response.text();
                        errorMessage = `Error en el backend (no JSON): ${errorText.substring(0, 200)}... (ver terminal del backend para detalles)`;
                        console.error("Respuesta del backend no fue JSON válido:", errorText);
                    }
                    throw new Error(errorMessage);
                }

                const data = await response.json();
                console.log("Respuesta del backend:", data);
                if (authStatusMessage) authStatusMessage.textContent = 'Autenticación de Spotify exitosa!';
                localStorage.removeItem('spotify_code_verifier');
                localStorage.setItem('user_id', data.user_id);
                localStorage.setItem('spotify_id', data.spotify_id);

                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);

            } catch (err) {
                console.error("Error al enviar el código al backend:", err);
                if (authStatusMessage) authStatusMessage.textContent = `Error de autenticación: ${err.message}`;
            }
        } else if (error) {
            console.error("Error de autenticación de Spotify:", error);
            if (authStatusMessage) authStatusMessage.textContent = `Autenticación de Spotify fallida: ${error}.`;
        } else {
            console.log("Página de callback cargada sin parámetros de autorización.");
        }
    }
    handleAuthCallback();
});