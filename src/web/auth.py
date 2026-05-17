"""Handle authentication check."""
import hmac
import os

from flask import Flask, Response, request

EXEMPT_PATHS = frozenset(("/healthz", "/robots.txt"))


def _auth_credentials() -> tuple[str, str] | None:
    """Return configured credentials, or None when auth is disabled."""
    username = os.getenv("DASH_USERNAME")
    password = os.getenv("DASH_PASSWORD")
    if not username or not password:
        return None
    return username, password


def _unauthorized() -> Response:
    """Return a Basic Auth challenge response."""
    response = Response("Authentication required\n", status=401, mimetype="text/plain")
    response.headers["WWW-Authenticate"] = 'Basic realm="Dashboard"'
    return response


def require_basic_auth() -> Response | None:
    """Protect dashboard routes with HTTP Basic Auth when configured."""
    if request.path in EXEMPT_PATHS:
        return None

    credentials = _auth_credentials()
    if credentials is None:
        return None

    auth = request.authorization
    if auth is None or auth.type.lower() != "basic":
        return _unauthorized()

    expected_username, expected_password = credentials
    if not hmac.compare_digest(auth.username or "", expected_username):
        return _unauthorized()
    if not hmac.compare_digest(auth.password or "", expected_password):
        return _unauthorized()
    return None

def configure_basic_auth(server: Flask) -> None:
    """Register Basic Auth middleware on a Flask server."""
    server.before_request(require_basic_auth)
