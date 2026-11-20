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
// now handles ended session. 401 request that sent token means that token is expired or invalid, so now we clear it and go to login page.
async function apiFetch(path, options = {}) {
    const headers = Object.assign({}, options.headers);
    const token = getToken();
    const isLoginRequest = path == "/auth/login";
    if (token && !isLoginRequest) {
        headers["Authorization"] = "Bearer " + token;
    }
    const response = await fetch(API_URL + path, Object.assign({}, options, { headers: headers }));
    if (response.status === 401 && token && !isLoginRequest) {
        clearToken();
        window.location.href = "login.html"
    }
    return response
}

function errorMessageFor(status) {
    if (status === 403) {
        return "You do not have access to this account.";
    }
    if (status === 404) {
        return "Account not found.";
    }
    return "Something went wrong. Please try again.";
}

function getCustomerId() {
    const token = getToken();
    if (!token) {
        return null;
    }
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        return Number(payload.sub);
    } catch (error) {
        return null;
    }
}