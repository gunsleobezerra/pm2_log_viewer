# Exemplo de configuração do compose.yml com autenticação

## Configuração Padrão (SEM autenticação)
services:
  pm2-log-viewer:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: pm2-log-viewer
    ports:
      - "8102:8001"
    volumes:
      - /root/.pm2/logs:/app/logs:ro
      - pm2-log-viewer-data:/app/data
    environment:
      - PORT=8001
      - TZ=America/Sao_Paulo
      - LOG_DIR=/app/logs
      - AUTH_ENABLED=false
    restart: unless-stopped
    networks:
      - log-viewer-network

volumes:
  pm2-log-viewer-data:
    driver: local

networks:
  log-viewer-network:
    driver: bridge

---

## Configuração COM Autenticação Habilitada
services:
  pm2-log-viewer:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: pm2-log-viewer
    ports:
      - "8102:8001"
    volumes:
      - /root/.pm2/logs:/app/logs:ro
      - pm2-log-viewer-data:/app/data
    environment:
      - PORT=8001
      - TZ=America/Sao_Paulo
      - LOG_DIR=/app/logs
      # Configurações de Autenticação
      - AUTH_ENABLED=true
      - AUTH_DB_PATH=/app/data/auth.db
      - SESSION_TIMEOUT=3600  # 1 hora em segundos
      # Credenciais do admin (usado apenas na primeira execução)
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=SuaSenhaSeguraAqui123!  # ALTERE ISSO!
    restart: unless-stopped
    networks:
      - log-viewer-network

volumes:
  pm2-log-viewer-data:
    driver: local

networks:
  log-viewer-network:
    driver: bridge

---

## Dicas de Segurança

### 1. Senha Forte
Use uma senha forte para o usuário admin:
- Mínimo de 12 caracteres
- Combine letras maiúsculas e minúsculas
- Inclua números e caracteres especiais
- Exemplo: MyP@ssw0rd2025!SecureLog

### 2. Timeout de Sessão
Ajuste o timeout baseado nas suas necessidades:
- Desenvolvimento: 7200 (2 horas)
- Produção: 1800 (30 minutos)
- Alta segurança: 900 (15 minutos)

### 3. Backup do Banco de Dados
O banco de dados de autenticação está no volume Docker.
Para fazer backup:

```bash
# Copiar banco de dados do container
docker cp pm2-log-viewer:/app/data/auth.db ./backup-auth.db

# Restaurar banco de dados
docker cp ./backup-auth.db pm2-log-viewer:/app/data/auth.db
docker restart pm2-log-viewer
```

### 4. Usar HTTPS
Para produção, considere usar um reverse proxy com SSL/TLS:
- Nginx
- Traefik
- Caddy

Exemplo com Nginx:
```nginx
server {
    listen 443 ssl;
    server_name logs.seudominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8102;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Variáveis de Ambiente Seguras
Para ambientes de produção, use secrets do Docker:

```yaml
services:
  pm2-log-viewer:
    secrets:
      - admin_password
    environment:
      - ADMIN_PASSWORD_FILE=/run/secrets/admin_password

secrets:
  admin_password:
    file: ./secrets/admin_password.txt
```
