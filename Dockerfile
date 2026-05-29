FROM python:3.12-slim

# Set working directory
WORKDIR /fastapi-architecture-dkr

# Firt: Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install UV CLI
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install python dependencies
RUN uv sync --frozen --no-cache

# Finally: Copy application code
COPY . .

# Run the application
# CMD ["/fastapi-architecture-dkr/.venv/bin/fastapi", "run", "app/main.py", "--port", "8083", "--host", "0.0.0.0"]
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8083", "--host", "0.0.0.0"]
# CMD ["uv", "run", "uvicorn", "app.main:app", "--port", "8083", "--host", "0.0.0.0"]
