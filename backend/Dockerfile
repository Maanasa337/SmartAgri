FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (NO backend/ here)
COPY requirements-server.txt .

RUN pip install --no-cache-dir -r requirements-server.txt

# Copy all backend files (already inside backend)
COPY . .

# Expose port (optional for Render)
EXPOSE 8000

# IMPORTANT: use Render port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
