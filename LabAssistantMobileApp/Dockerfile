FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Force stdout and stderr to be unbuffered (Logs appear instantly)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m appuser

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and set ownership
COPY --chown=appuser:appuser . .

# Switch to the non-root user
USER appuser

# Expose the internal port
EXPOSE 6999

# Start command
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:6999", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
