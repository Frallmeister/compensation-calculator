# Offer comparison sandbox

This project is organized so the notebooks stay thin while the comparison logic,
config loading, and reference data handling live in a small Python package.

## Structure

- `src/offers/`: domain logic for compensation calculations
- `src/web/`: Dash frontend app and web entrypoints
- `configs/employers/`: one TOML file per employer offer
- `configs/assumptions.toml`: shared assumptions
- `data/raw/skattetabell.csv`: tax table source data
- `data/processed/skattetabell.parquet`: generated artifact (not committed)

## Quick start

Create or sync the local environment with uv:

```bash
uv sync
```

Generate the tax parquet once after cloning:

```bash
uv run python -c "from offers.loader import refine_skattetabell; refine_skattetabell()"
```

This creates `data/processed/skattetabell.parquet` from
`data/raw/skattetabell.csv`.

Run the Dash app locally:

```bash
uv run offers-dash
```

Open `http://localhost:8050`.

## Run locally with Docker

Build the image from the repository root:

```bash
docker build -t offers-app .
```

Run the container in the foreground:

```bash
docker run --rm -p 8050:8050 --name offers-app-test offers-app
```

Open `http://localhost:8050`.

Optionally run detached and inspect logs:

```bash
docker run -d --rm -p 8050:8050 --name offers-app-test offers-app
docker logs -f offers-app-test
```

Stop the container:

```bash
docker stop offers-app-test
```

Generate or refresh the lockfile explicitly when needed:

```bash
uv lock
```

## Deploy to Render

This repository includes a `Dockerfile` and `render.yaml`.

How deployment works for data:

- The Docker build runs `refine_skattetabell()`.
- `data/processed/skattetabell.parquet` is baked into the image.
- Because data is static for this project, redeploying only when configs/data
	change is enough.

Deploy steps:

1. Push the repository to GitHub.
2. In Render, create a new Blueprint service from the repository.
3. Render reads `render.yaml` and builds using the `Dockerfile`.
4. After deploy finishes, open the generated Render URL and verify `/` responds.

## Connect custom domain (GoDaddy -> Render)

1. In Render service settings, open Custom Domains and add your domain/subdomain.
2. Copy the DNS records Render gives you.
3. In GoDaddy DNS management, create matching records.
4. Wait for DNS propagation, then verify domain status in Render.

Common setup:

- Use a CNAME when deploying to a subdomain (for example `app.yourdomain.com`).
- For apex domain (`yourdomain.com`), use the A/ALIAS records Render provides.
