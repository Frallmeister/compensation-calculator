FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY configs ./configs
COPY data/raw ./data/raw

RUN uv sync --frozen
RUN uv run python -c "from offers.loader import refine_skattetabell; refine_skattetabell()"

EXPOSE 8050

CMD ["sh", "-c", "uv run gunicorn web.dash_app:server --bind 0.0.0.0:${PORT:-8050} --workers ${WEB_CONCURRENCY:-2} --threads ${WEB_THREADS:-4} --timeout 120"]
