FROM python:3.11-slim

# System dependencies: ffmpeg for Whisper, build tools for some Python packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (better Docker layer caching —
# this layer only rebuilds if requirements.txt changes, not on every code edit)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Copy application code
COPY personal_ai_assistant/ ./personal_ai_assistant/
COPY setup.py pyproject.toml ./

# Create runtime data directories (mounted as volumes in docker-compose, but
# created here too so the app doesn't fail if run standalone without compose)
RUN mkdir -p data/documents data/voice data/vision data/generated_images data/metrics

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "personal_ai_assistant.api.main:app", "--host", "0.0.0.0", "--port", "8000"]