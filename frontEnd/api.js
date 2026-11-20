// The API client. Every page sends its requests through apiFetch,
// so the token is attached in one place and pages never handle it themselves. #Sidenote, but I don't fully understand how it works
const API_URL = "http://127.0.0.1:8000";
const TOKEN_KEY = "access_token";

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

// Works like fetch, instead goes through path like "/customers" and adds token when signed in
function apiFetch(path, options = {}) {
    const headers = Object.assign({}, options.headers);
    const token = getToken();
    if (token) {
        headers["Authorization"] = "Bearer " + token;
    }
    return fetch(API_URL + path, Object.assign({}, options, { headers: headers }));
}