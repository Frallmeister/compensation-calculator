"""Smoke tests for Dash app startup and critical routes."""

import base64
import os
import unittest
from typing import ClassVar
from unittest.mock import patch

from flask.testing import FlaskClient
from web import dash_app


class DashStartupSmokeTest(unittest.TestCase):
    """Verify the dashboard app initializes and serves expected routes."""

    client: ClassVar[FlaskClient]

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = dash_app.server.test_client()

    def test_dash_layout_endpoint_returns_ok(self) -> None:
        """Dash layout endpoint should be available when app starts."""
        response = self.client.get("/_dash-layout")
        self.assertEqual(response.status_code, 200)

    def test_healthz_endpoint_returns_ok(self) -> None:
        """Health endpoint should be available without auth."""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "ok\n")

    def test_robots_txt_disallows_all_crawlers(self) -> None:
        """robots.txt should explicitly block indexing for this app."""
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn("User-agent: *", content)
        self.assertIn("Disallow: /", content)

    def test_auth_requires_credentials_when_enabled(self) -> None:
        """Protected routes should challenge when auth env vars are configured."""
        with patch.dict(os.environ, {"DASH_USERNAME": "alice", "DASH_PASSWORD": "secret"}):
            response = self.client.get("/_dash-layout")
        self.assertEqual(response.status_code, 401)
        self.assertIn("Basic", response.headers.get("WWW-Authenticate", ""))

    def test_auth_accepts_valid_basic_credentials(self) -> None:
        """Protected routes should return 200 with valid Basic Auth credentials."""
        token = base64.b64encode(b"alice:secret").decode("ascii")
        headers = {"Authorization": f"Basic {token}"}
        with patch.dict(os.environ, {"DASH_USERNAME": "alice", "DASH_PASSWORD": "secret"}):
            response = self.client.get("/_dash-layout", headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_healthz_is_exempt_when_auth_enabled(self) -> None:
        """Health endpoint should remain open for Render health checks."""
        with patch.dict(os.environ, {"DASH_USERNAME": "alice", "DASH_PASSWORD": "secret"}):
            response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
