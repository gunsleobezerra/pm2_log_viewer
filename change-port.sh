#!/bin/bash

# Script para alterar a porta do PM2 Log Viewer
# Uso: ./change-port.sh <nova_porta>

if [ -z "$1" ]; then
    echo "❌ Erro: Informe a nova porta"
    echo "📖 Uso: $0 <porta>"
    echo "📝 Exemplo: $0 8080"
    exit 1
fi

NEW_PORT=$1

# Verificar se a porta é válida
if ! [[ "$NEW_PORT" =~ ^[0-9]+$ ]] || [ "$NEW_PORT" -lt 1024 ] || [ "$NEW_PORT" -gt 65535 ]; then
    echo "❌ Erro: Porta inválida. Use um número entre 1024 e 65535"
    exit 1
fi

# Verificar se existe arquivo .env.viewer
if [ ! -f ".env.viewer" ]; then
    echo "📄 Arquivo .env.viewer não encontrado. Copiando do exemplo..."
    cp .env.viewer.example .env.viewer
fi

# Verificar se a porta já está em uso
if lsof -i :$NEW_PORT > /dev/null 2>&1; then
    echo "⚠️  Aviso: A porta $NEW_PORT já está em uso!"
    read -p "🤔 Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Operação cancelada"
        exit 1
    fi
fi

# Fazer backup do arquivo atual
cp .env.viewer .env.viewer.bak
echo "💾 Backup criado: .env.viewer.bak"

# Alterar a porta no arquivo
sed -i "s/^EXTERNAL_PORT=.*/EXTERNAL_PORT=$NEW_PORT/" .env.viewer

echo "🔧 Porta alterada para $NEW_PORT no arquivo .env.viewer"

# Verificar se Docker Compose está rodando
if docker compose ps | grep -q "pm2-log-viewer"; then
    echo "🐳 Reiniciando container com nova porta..."
    docker compose down
    docker compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Container reiniciado com sucesso!"
        echo "🌐 Acesse: http://localhost:$NEW_PORT"
    else
        echo "❌ Erro ao reiniciar container"
        echo "🔄 Restaurando backup..."
        mv .env.viewer.bak .env.viewer
        exit 1
    fi
else
    echo "📝 Para aplicar a mudança, execute:"
    echo "   docker compose up -d"
    echo "🌐 Depois acesse: http://localhost:$NEW_PORT"
fi

echo "🎉 Concluído!"