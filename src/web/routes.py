"""Define routes to be registered in the Flask server."""
from flask import Flask, Response


def healthz() -> Response:
    """Return liveness status for platform health checks."""
    return Response("ok\n", mimetype="text/plain")


def robots_txt() -> Response:
    """Disallow crawler indexing for this dashboard."""
    content = "User-agent: *\nDisallow: /\n"
    return Response(content, mimetype="text/plain; charset=utf-8")


def register_routes(server: Flask) -> None:
    """Register non-Dash Flask routes."""
    server.add_url_rule("/healthz", view_func=healthz, methods=["GET"])
    server.add_url_rule("/robots.txt", view_func=robots_txt, methods=["GET"])
