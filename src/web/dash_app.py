"""Minimal Dash app for comparing offer value side by side."""

import os
from pathlib import Path

from dash import Dash

from offers.loader import ensure_refined_skattetabell
from web.auth import configure_basic_auth
from web.callbacks.comparison import register_comparison_callbacks
from web.layout.shell import create_layout
from web.routes import register_routes
from web.services.comparison import (
    available_tax_tables,
    default_salary,
)


ASSETS_DIR = Path(__file__).parent / "assets"

def create_app() -> Dash:
    """Create and configure the Dash app."""
    ensure_refined_skattetabell()
    default_salary_value = default_salary()
    tax_tables = available_tax_tables()
    default_table = 33 if 33 in tax_tables else tax_tables[0]

    app = Dash(
        __name__,
        title="Offer comparison",
        assets_folder=str(ASSETS_DIR),
    )
    app.layout = create_layout(
        default_salary_value=default_salary_value,
        tax_tables=tax_tables,
        default_table=default_table,
    )

    register_comparison_callbacks(
        app=app,
        default_salary_value=default_salary_value,
        default_table=default_table,
    )

    # Register HTTP authentication and URL routes.
    configure_basic_auth(app.server)
    register_routes(app.server)
    return app


app = create_app()
server = app.server


def main() -> None:
    """Run the app locally or in a container."""
    port = int(os.getenv("PORT", "8050"))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
