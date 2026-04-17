FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
# Note: build tools removed since we use requirements-server.txt (no pyaudio)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (server-only, no pyaudio build complexity)
COPY backend/requirements-server.txt .
RUN pip install --no-cache-dir -r requirements-server.txt

# Copy backend code (includes unified farm_advisory module)
COPY backend/ .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app with proper startup message
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
