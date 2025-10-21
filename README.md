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
- 🐳 Container Docker pronto para uso

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
  -p 8001:8001 \
  -v $(pwd)/../:/app/logs:ro \
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
http://localhost:8001
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

### Arquivo de Configuração (.env.viewer)

O projeto suporta configuração através de arquivo `.env.viewer`. Para usar:

```bash
# Copie o arquivo de exemplo
cp .env.viewer.example .env.viewer

# Edite as configurações conforme necessário
nano .env.viewer
```

### Principais Variáveis de Ambiente

- `PORT`: Porta do servidor (padrão: 8001)
- `EXTERNAL_PORT`: Porta externa para acesso (padrão: 8001)
- `TZ`: Timezone (padrão: America/Sao_Paulo)
- `CONTAINER_NAME`: Nome do container (padrão: pm2-log-viewer)
- `LOGS_HOST_PATH`: Caminho dos logs no host (padrão: ../)
- `LOGS_CONTAINER_PATH`: Caminho dos logs no container (padrão: /app/logs)
- `RESTART_POLICY`: Política de restart (padrão: unless-stopped)
- `NETWORK_NAME`: Nome da rede Docker (padrão: log-viewer-network)
- `NETWORK_DRIVER`: Driver da rede (padrão: bridge)

### Configuração de Volumes

O Docker Compose monta automaticamente o diretório configurado em `LOGS_HOST_PATH` como `LOGS_CONTAINER_PATH` no container em modo somente leitura.

Para personalizar, edite o arquivo `.env.viewer`:

```bash
# Exemplo: logs em diretório específico
LOGS_HOST_PATH=/var/log/pm2
LOGS_CONTAINER_PATH=/app/logs
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
- Apenas requisições GET são permitidas
- Limit de 5000 linhas por consulta

## 🐛 Troubleshooting

### Container não inicia

```bash
# Verifique os logs
docker compose logs

# Verifique se a porta 8001 está disponível
sudo lsof -i :8001
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
