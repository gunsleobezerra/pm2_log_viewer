# Sistema de Login - PM2 Log Viewer

## ✅ Implementação Completa

Sistema de autenticação opcional com SQLite implementado com sucesso!

## 📦 Arquivos Criados/Modificados

### Novos Arquivos
1. **auth.py** - Módulo de autenticação com SQLite
2. **login.html** - Interface de login
3. **init_users.py** - Script de inicialização de usuários
4. **manage_users.py** - Utilitário CLI para gerenciar usuários
5. **SECURITY.md** - Guia de segurança
6. **QUICKSTART.md** - Guia rápido de uso
7. **IMPLEMENTATION.md** - Este arquivo

### Arquivos Modificados
1. **server.py** - Adicionado middleware de autenticação e rotas de login/logout
2. **index.html** - Adicionado botão de logout e verificação de autenticação
3. **compose.yml** - Adicionadas variáveis de ambiente para autenticação
4. **Dockerfile** - Atualizado para incluir SQLite e novos arquivos
5. **manage.sh** - Adicionados comandos para gerenciar usuários
6. **README.md** - Documentação atualizada com seção de autenticação

## 🔧 Recursos Implementados

### Segurança
- ✅ Hash de senhas com SHA-256 + salt único por usuário
- ✅ Sessões com expiração configurável
- ✅ Cookies HttpOnly e SameSite
- ✅ Renovação automática de sessão (sliding expiration)
- ✅ Limpeza automática de sessões expiradas
- ✅ Proteção de rotas quando autenticação está ativa

### Gerenciamento
- ✅ Criação automática de usuário admin na primeira execução
- ✅ Script CLI para gerenciar usuários (create, delete, list, passwd)
- ✅ Comandos no manage.sh para facilitar o gerenciamento
- ✅ Persistência do banco de dados em volume Docker

### Interface
- ✅ Página de login responsiva e moderna
- ✅ Botão de logout no index.html (visível apenas quando auth está ativa)
- ✅ Redirecionamento automático quando não autenticado
- ✅ Mensagens de erro e sucesso amigáveis

### Configuração
- ✅ Ativação/desativação fácil via variável de ambiente
- ✅ Configuração de timeout de sessão
- ✅ Customização de credenciais admin via environment
- ✅ Volume Docker para persistência do banco de dados

## 🚀 Como Usar

### Ativar Autenticação
```bash
# 1. Editar compose.yml
# Alterar: AUTH_ENABLED=true
# Alterar: ADMIN_PASSWORD=sua_senha_segura

# 2. Reconstruir e iniciar
docker compose down
docker compose up -d --build

# 3. Acessar http://localhost:8102
# Login: admin / sua_senha_segura
```

### Desativar Autenticação
```bash
# 1. Editar compose.yml
# Alterar: AUTH_ENABLED=false

# 2. Reiniciar
docker compose restart
```

### Gerenciar Usuários
```bash
# Listar
./manage.sh users list

# Criar
./manage.sh users create

# Alterar senha
./manage.sh users passwd

# Deletar
./manage.sh users delete
```

## 🗂️ Estrutura do Banco de Dados

### Tabela: users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Tabela: sessions
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

## 🔐 Variáveis de Ambiente

```yaml
AUTH_ENABLED=false              # Ativa/desativa autenticação
AUTH_DB_PATH=/app/data/auth.db  # Caminho do banco SQLite
SESSION_TIMEOUT=3600            # Timeout em segundos (1h)
ADMIN_USERNAME=admin            # Usuário admin inicial
ADMIN_PASSWORD=changeme         # Senha admin inicial (ALTERE!)
```

## 📋 Endpoints da API

### Públicos (sem autenticação)
- `GET /login.html` - Página de login
- `GET /api/auth-status` - Status de autenticação

### Protegidos (requerem autenticação quando AUTH_ENABLED=true)
- `GET /` ou `/index.html` - Interface principal
- `GET /files` - Lista arquivos de log
- `GET /file/{filename}` - Lê arquivo de log

### Autenticação
- `POST /api/login` - Fazer login (retorna cookie de sessão)
- `POST /api/logout` - Fazer logout (remove sessão)

## 🧪 Testes

### Testar sem autenticação
```bash
# compose.yml: AUTH_ENABLED=false
docker compose up -d
curl http://localhost:8102/
# Deve retornar a página index.html
```

### Testar com autenticação
```bash
# compose.yml: AUTH_ENABLED=true
docker compose up -d

# Sem login - deve redirecionar
curl -v http://localhost:8102/
# Deve retornar 302 redirect para /login.html

# Com login
curl -v -X POST http://localhost:8102/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}' \
  -c cookies.txt

# Acessar com sessão
curl -v http://localhost:8102/ -b cookies.txt
# Deve retornar a página index.html
```

## 📝 Checklist de Implementação

- [x] Módulo de autenticação (auth.py)
- [x] Middleware no servidor (server.py)
- [x] Página de login (login.html)
- [x] Integração no index.html
- [x] Configuração no compose.yml
- [x] Atualização do Dockerfile
- [x] Script de inicialização (init_users.py)
- [x] CLI de gerenciamento (manage_users.py)
- [x] Comandos no manage.sh
- [x] Documentação (README.md)
- [x] Guia de segurança (SECURITY.md)
- [x] Guia rápido (QUICKSTART.md)

## 🎯 Próximos Passos (Opcional)

Sugestões para melhorias futuras:
- [ ] Interface web para gerenciar usuários
- [ ] Suporte a múltiplos perfis/roles
- [ ] Logs de auditoria (quem acessou quando)
- [ ] Autenticação via LDAP/OAuth
- [ ] Rate limiting para login
- [ ] 2FA (autenticação de dois fatores)
- [ ] API REST completa para usuários

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte o [README.md](README.md)
2. Consulte o [QUICKSTART.md](QUICKSTART.md)
3. Consulte o [SECURITY.md](SECURITY.md)
4. Abra uma issue no repositório

---

**Implementado com ❤️ para melhorar a segurança do PM2 Log Viewer**
