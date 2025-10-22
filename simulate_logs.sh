#!/bin/bash

# Script para adicionar logs de teste para demonstrar o auto-refresh

LOG_FILE="/home/leonardo/Documentos/Repositories/Backups/log_backup/logs/test-auto-refresh.log"

# Criar arquivo se não existir
if [ ! -f "$LOG_FILE" ]; then
    echo "Criando arquivo de teste: $LOG_FILE"
    touch "$LOG_FILE"
fi

# Adicionar logs de teste a cada 2 segundos
echo "Iniciando simulação de logs... (Ctrl+C para parar)"

counter=1
while true; do
    timestamp=$(date '+%d-%m-%Y %H:%M:%S')
    echo "[$timestamp] INFO Log de teste #$counter - Sistema funcionando normalmente" >> "$LOG_FILE"
    echo "Adicionado log #$counter em $timestamp"
    
    # A cada 5 logs, adicionar um log de nível diferente
    if [ $((counter % 5)) -eq 0 ]; then
        echo "[$timestamp] WARN Aviso de teste #$counter - Verificação periódica" >> "$LOG_FILE"
        echo "Adicionado log de WARNING #$counter"
    fi
    
    # A cada 10 logs, adicionar um erro
    if [ $((counter % 10)) -eq 0 ]; then
        echo "[$timestamp] ERROR Erro simulado #$counter - Teste de funcionalidade" >> "$LOG_FILE"
        echo "Adicionado log de ERROR #$counter"
    fi
    
    counter=$((counter + 1))
    sleep 2
done