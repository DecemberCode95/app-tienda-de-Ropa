# Dockerfile para Tienda de Ropa Django REST API
# Basado en Python 3.12 slim para imagen ligera

FROM python:3.12-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p staticfiles media logs

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput || true

# Crear usuario no root para mayor seguridad
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "config.wsgi:application"]
