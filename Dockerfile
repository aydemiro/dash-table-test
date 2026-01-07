# Dockerfile for a Dash app (expects app.py and requirements.txt in the build context)
FROM python:3.11-slim

LABEL maintainer="GitHub Copilot"

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 

WORKDIR /app

# Install build deps (some Python packages require a compiler)
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run with gunicorn mapping to a random port between 8050-8090
CMD ["gunicorn", "-bind", "0.0.0.0:$(shuf -i 8050-8090 -n 1)", "app:server"]
