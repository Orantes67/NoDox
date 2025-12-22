FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Crear directorio de logs
RUN mkdir -p logs

# Variables de entorno
ENV PYTHONUNBUFFERED=1

# Ejecutar NoDox
CMD ["python", "nodox.py", "protect"]