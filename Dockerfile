FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Compile bytecode at build time (faster startup); copy instead of hardlink
# because the uv cache lives on a different filesystem layer.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Install dependencies first, project second — dependency layers only rebuild
# when the lockfile changes, not on every source edit.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
