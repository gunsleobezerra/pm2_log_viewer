# PM2 Log Viewer

Interface web para visualizar e filtrar logs do PM2 com suporte a múltiplos idiomas.

## 🚀 Características

- 📊 Visualização de logs em tempo real
- 🔍 Pesquisa por palavras-chave com destaque
- 📅 Filtro por data/hora
- 🎨 Tema customizável (cores e layout)
- 🌍 Suporte a múltiplos idiomas (PT, EN, ES)
- 📄 Paginação avançada
- 💾 Salvamento de preferências no localStorage
- � Sistema de autenticação opcional com SQLite
- �🐳 Container Docker pronto para uso

## 📋 Pré-requisitos

- Docker
- Docker Compose

## 🔧 Instalação e Uso

### Opção 1: Docker Compose (Recomendado)

```bash
# Clone ou navegue até a pasta do projeto
cd pm2_log_viewer

# Construa e inicie o container
docker compose up -d

# Visualize os logs
docker compose logs -f

# Pare o container
docker compose down
```

### Opção 2: Docker Run

```bash
# Construa a imagem
docker build -t pm2-log-viewer .

# Execute o container
docker run -d \
  --name pm2-log-viewer \
  -p 8102:8001 \
  -v /root/.pm2/logs:/app/logs:ro \
  pm2-log-viewer
```

### Opção 3: Execução Local (sem Docker)

```bash
# Execute o servidor Python
python server.py

# Abra no navegador
# http://localhost:8001
```

## 🌐 Acesso

Após iniciar o container, acesse:
```
http://localhost:8102
```

## 📁 Estrutura do Projeto

```
pm2_log_viewer/
├── Dockerfile          # Configuração do container Docker
├── compose.yml         # Configuração do Docker Compose
├── server.py           # Servidor Python HTTP
├── index.html          # Interface web
└── README.md          # Este arquivo
```

## ⚙️ Configurações

### Configuração Básica

O projeto usa uma configuração simples e direta através do arquivo `compose.yml`. As configurações principais são:

- **Porta**: 8102 (externa) → 8001 (interna)
- **Logs**: `/root/.pm2/logs` montado em `/app/logs` (somente leitura)
- **Timezone**: America/Sao_Paulo
- **Container**: pm2-log-viewer
- **Restart**: unless-stopped

### Personalização do compose.yml

Para alterar as configurações, edite diretamente o arquivo `compose.yml`:

```yaml
services:
  pm2-log-viewer:
    ports:
      - "PORTA_EXTERNA:8001"  # Altere PORTA_EXTERNA
    volumes:
      - /caminho/para/logs:/app/logs:ro  # Altere o caminho dos logs
    environment:
      - TZ=Seu/Timezone  # Altere o timezone
```

### Configuração de Volumes

Por padrão, o sistema monta `/root/.pm2/logs` do host no container. Para usar um diretório diferente:

```bash
# Edite compose.yml e altere a linha:
volumes:
  - /seu/diretorio/de/logs:/app/logs:ro
```

### Mudança de Porta

Para alterar a porta de acesso, edite o arquivo `compose.yml`:

```yaml
ports:
  - "NOVA_PORTA:8001"  # Substitua NOVA_PORTA pela porta desejada
```

Depois reinicie o container:
```bash
docker compose down && docker compose up -d
```

## 🎨 Funcionalidades

### Filtros
- **Pesquisa**: Busca por palavras-chave com destaque
- **Data/Hora**: Filtro por intervalo de tempo
- **Arquivo**: Seleção de arquivo de log específico

### Personalização
- Cores da interface (gradiente de fundo, botões, área de logs)
- Quantidade de linhas por página (10-500)
- Idioma (Português, Inglês, Espanhol)

### Visualização
- Datetime em negrito
- Status coloridos (INFO, ERROR, WARN, DEBUG, FATAL)
- Paginação avançada com navegação rápida
- Área de logs com scroll

## 🔒 Segurança

- Container executado em modo somente leitura para os logs
- Apenas requisições GET são permitidas (exceto para login/logout)
- Limit de 5000 linhas por consulta
- Sistema de autenticação opcional com sessões seguras
- Senhas armazenadas com hash SHA-256 e salt

## 🔐 Sistema de Autenticação

O PM2 Log Viewer possui um sistema de autenticação opcional que pode ser ativado/desativado facilmente.

### Ativando a Autenticação

Edite o arquivo `compose.yml` e altere a variável de ambiente:

```yaml
environment:
  - AUTH_ENABLED=true  # Altere de 'false' para 'true'
  - ADMIN_USERNAME=admin  # Usuário admin padrão
  - ADMIN_PASSWORD=changeme  # ALTERE ESTA SENHA!
  - SESSION_TIMEOUT=3600  # Tempo de sessão em segundos (1 hora)
```

**⚠️ IMPORTANTE**: Altere a senha padrão (`ADMIN_PASSWORD`) antes de ativar a autenticação!

### Credenciais Padrão

Na primeira execução com autenticação habilitada, um usuário admin é criado automaticamente:

- **Usuário**: admin (ou o valor de `ADMIN_USERNAME`)
- **Senha**: changeme (ou o valor de `ADMIN_PASSWORD`)

### Banco de Dados

- O sistema usa SQLite para armazenar usuários e sessões
- O banco de dados é persistido no volume `pm2-log-viewer-data`
- Localização: `/app/data/auth.db` (dentro do container)

### Recursos de Segurança

- ✅ Senhas armazenadas com hash SHA-256 + salt único por usuário
- ✅ Sessões com expiração configurável (padrão: 1 hora)
- ✅ Cookies HttpOnly e SameSite para proteção contra XSS
- ✅ Renovação automática de sessão (sliding expiration)
- ✅ Limpeza automática de sessões expiradas
- ✅ Proteção de todas as rotas quando autenticação está ativa

### Desativando a Autenticação

Para desativar a autenticação, basta alterar no `compose.yml`:

```yaml
environment:
  - AUTH_ENABLED=false
```

E reiniciar o container:

```bash
docker compose down && docker compose up -d
```

### Gerenciamento de Usuários

O sistema possui um utilitário de linha de comando para facilitar o gerenciamento de usuários.

#### Usando o script manage_users.py

```bash
# Listar todos os usuários
docker exec -it pm2-log-viewer python manage_users.py list

# Criar novo usuário (modo interativo)
docker exec -it pm2-log-viewer python manage_users.py create

# Criar usuário com credenciais (não-interativo)
docker exec -it pm2-log-viewer python manage_users.py create -u usuario -p senha

# Alterar senha de um usuário
docker exec -it pm2-log-viewer python manage_users.py passwd -u usuario

# Deletar um usuário
docker exec -it pm2-log-viewer python manage_users.py delete -u usuario
```

#### Usando Python diretamente

Atualmente, o sistema cria apenas o usuário admin inicial. Para gerenciar usuários adicionais, você pode:

1. Acessar o container:
   ```bash
   docker exec -it pm2-log-viewer python
   ```

2. Usar o módulo de autenticação:
   ```python
   from auth import get_auth_manager
   auth = get_auth_manager()
   
   # Criar novo usuário
   auth.create_user('novo_usuario', 'senha_segura')
   
   # Listar usuários
   print(auth.list_users())
   
   # Alterar senha
   auth.change_password('usuario', 'nova_senha')
   
   # Deletar usuário
   auth.delete_user('usuario')
   ```

### Resetar Banco de Dados de Autenticação

Para resetar completamente o sistema de autenticação:

```bash
# Parar o container
docker compose down

# Remover o volume de dados
docker volume rm pm2_log_viewer_pm2-log-viewer-data

# Reiniciar (um novo banco será criado)
docker compose up -d
```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Verifique os logs
docker compose logs

# Verifique se a porta 8102 está disponível
sudo lsof -i :8102
```

### Logs não aparecem

1. Verifique se o volume está montado corretamente
2. Certifique-se de que os arquivos `.log` existem no diretório
3. Verifique as permissões dos arquivos de log

### Erro de conexão

```bash
# Reinicie o container
docker compose restart

# Reconstrua se necessário
docker compose up -d --build
```

## 📝 Licença

Este projeto é de código aberto.

## 👥 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## 📞 Suporte

Para problemas ou sugestões, abra uma issue no repositório do projeto.
