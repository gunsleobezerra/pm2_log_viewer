# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8001

# Install SQLite (já vem com Python, mas garantir que está disponível)
RUN apt-get update && \
    apt-get install -y --no-install-recommends sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY server.py .
COPY auth.py .
COPY index.html .
COPY login.html .
COPY init_users.py .
COPY manage_users.py .

# Create directories
RUN mkdir -p /app/logs /app/data && \
    chmod 755 /app/data

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001')" || exit 1

# Inicializar usuários e depois rodar o servidor
CMD python init_users.py && python server.py
