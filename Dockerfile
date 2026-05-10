# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv (from official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies first to cache them
COPY backend/requirements.txt ./backend/
RUN uv pip install --system -r backend/requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY VERSION ./

# Expose ports
EXPOSE 8000

# Start command with Gunicorn (4 workers) for higher concurrency
CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
