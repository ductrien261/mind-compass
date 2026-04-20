# ════════════════════════════════════════════════════════════════════
# Dockerfile — MindCompass Backend
# Base: Python 3.11 + SWI-Prolog (apt) + Django + pyswip
# Deploy target: Render.com (free tier)
# ════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

# Cài đặt SWI-Prolog từ apt
RUN apt-get update && apt-get install -y \
    swi-prolog \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Collect static files
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Expose port
EXPOSE 8000

# Khởi động với Gunicorn
# Render truyền $PORT động, default 8000 cho local Docker
CMD gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --log-level info
