FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ADD pyproject.toml .
ADD uv.lock .

RUN uv sync --frozen --no-cache
COPY . .

CMD ["uv", "run", "uvicorn", "skill_tracker.main:app", "--host", "0.0.0.0", "--port", "8000"]
