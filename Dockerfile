FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY tracker_monitor.py .

# Create config directory
RUN mkdir -p /config

# Run as non-root user for security
RUN useradd -m -u 1000 tracker && \
    chown -R tracker:tracker /app /config

USER tracker

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Health check - Version corrigée
HEALTHCHECK --interval=5m --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import json, os; from datetime import datetime, timedelta; state = json.load(open('/config/state.json')) if os.path.exists('/config/state.json') else {}; exit(1) if not state else None; last_checks = [datetime.fromisoformat(v['last_check']) for v in state.values() if 'last_check' in v]; exit(0 if last_checks and max(last_checks) > datetime.now() - timedelta(hours=1) else 1)"

# Run the application
CMD ["python", "-u", "tracker_monitor.py"]
