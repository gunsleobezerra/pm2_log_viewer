# Guia Rápido - Sistema de Autenticação

## Início Rápido

### 1. Sem Autenticação (Padrão)
```bash
# O compose.yml já vem configurado sem autenticação
docker compose up -d

# Acesse: http://localhost:8102
```

### 2. Com Autenticação
```bash
# Edite compose.yml e altere:
# AUTH_ENABLED=true
# ADMIN_PASSWORD=sua_senha_segura

docker compose up -d

# Acesse: http://localhost:8102
# Login: admin / sua_senha_segura
```

## Gerenciamento de Usuários

### Listar usuários
```bash
./manage.sh users list
```

### Criar novo usuário
```bash
./manage.sh users create
```

### Alterar senha
```bash
./manage.sh users passwd
```

### Deletar usuário
```bash
./manage.sh users delete
```

## Comandos Úteis

### Ver logs do container
```bash
docker compose logs -f
```

### Entrar no container
```bash
docker exec -it pm2-log-viewer bash
```

### Reiniciar após alteração de configuração
```bash
docker compose down && docker compose up -d
```

### Resetar banco de dados de autenticação
```bash
docker compose down
docker volume rm pm2_log_viewer_pm2-log-viewer-data
docker compose up -d
```

## Troubleshooting

### Esqueci a senha do admin
```bash
# Opção 1: Resetar banco de dados
docker compose down
docker volume rm pm2_log_viewer_pm2-log-viewer-data
docker compose up -d

# Opção 2: Criar novo usuário
docker exec -it pm2-log-viewer python manage_users.py create
```

### Autenticação não funciona
```bash
# Verificar se está habilitada
docker exec pm2-log-viewer env | grep AUTH_ENABLED

# Verificar logs
docker compose logs pm2-log-viewer

# Verificar se o banco existe
docker exec pm2-log-viewer ls -la /app/data/
```

### Container não inicia
```bash
# Ver logs de erro
docker compose logs pm2-log-viewer

# Verificar permissões do volume
docker exec pm2-log-viewer ls -la /app/data/

# Reconstruir do zero
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Configurações Avançadas

### Alterar timeout de sessão
```yaml
# No compose.yml
environment:
  - SESSION_TIMEOUT=7200  # 2 horas em segundos
```

### Usar diretório diferente para logs
```yaml
# No compose.yml
volumes:
  - /seu/diretorio:/app/logs:ro
```

### Mudar porta de acesso
```yaml
# No compose.yml
ports:
  - "8080:8001"  # Acesse em http://localhost:8080
```

## Estrutura de Arquivos

```
pm2_log_viewer/
├── auth.py              # Módulo de autenticação
├── server.py            # Servidor HTTP
├── index.html           # Interface principal
├── login.html           # Página de login
├── init_users.py        # Inicialização de usuários
├── manage_users.py      # Gerenciamento de usuários CLI
├── manage.sh            # Script de gerenciamento
├── compose.yml          # Configuração Docker Compose
├── Dockerfile           # Configuração da imagem
├── README.md            # Documentação completa
├── SECURITY.md          # Guia de segurança
└── QUICKSTART.md        # Este arquivo
```

## Segurança

⚠️ **IMPORTANTE**:

1. **Sempre** altere a senha padrão `changeme`
2. Use senhas fortes (min. 12 caracteres)
3. Para produção, use HTTPS (reverse proxy)
4. Faça backup regular do banco de dados
5. Configure timeout de sessão apropriado

## Links Úteis

- [Documentação Completa](README.md)
- [Guia de Segurança](SECURITY.md)
- [Gerenciamento de Usuários](#gerenciamento-de-usuários)

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório do projeto.
