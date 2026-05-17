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

CMD ["sh", "-c", "uv run python -m web.dash_app"]
