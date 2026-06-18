FROM python:3.14-slim-trixie

USER root

EXPOSE 8000

WORKDIR /app

ENV UV_NO_DEV=1 \
    PATH="/app/.venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./.python-version ./.python-version
COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock
RUN uv sync

COPY . .

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN mkdir -p /app/logs \
    && chown -R appuser:appuser /app/logs

USER appuser