"""Smoke tests for Dash app startup and critical routes."""

import unittest
from typing import ClassVar

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

    def test_robots_txt_disallows_all_crawlers(self) -> None:
        """robots.txt should explicitly block indexing for this app."""
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        content = response.get_data(as_text=True)
        self.assertIn("User-agent: *", content)
        self.assertIn("Disallow: /", content)


if __name__ == "__main__":
    unittest.main()
