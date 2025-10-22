#!/bin/bash

# Script para gerenciar o PM2 Log Viewer

set -e

PROJECT_NAME="pm2-log-viewer"
COMPOSE_FILE="compose.yml"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

function print_error() {
    echo -e "${RED}✗ $1${NC}"
}

function print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

function check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker não está instalado!"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        print_error "Docker Compose não está instalado!"
        exit 1
    fi
}

function start() {
    print_info "Iniciando $PROJECT_NAME..."
    docker compose -f "$COMPOSE_FILE" up -d
    print_success "Container iniciado!"
    print_info "Acesse: http://localhost:8000"
}

function stop() {
    print_info "Parando $PROJECT_NAME..."
    docker compose -f "$COMPOSE_FILE" down
    print_success "Container parado!"
}

function restart() {
    print_info "Reiniciando $PROJECT_NAME..."
    docker compose -f "$COMPOSE_FILE" restart
    print_success "Container reiniciado!"
}

function logs() {
    docker compose -f "$COMPOSE_FILE" logs -f
}

function build() {
    print_info "Construindo imagem..."
    docker compose -f "$COMPOSE_FILE" build --no-cache
    print_success "Imagem construída!"
}

function rebuild() {
    print_info "Reconstruindo e reiniciando..."
    docker compose -f "$COMPOSE_FILE" down
    docker compose -f "$COMPOSE_FILE" build --no-cache
    docker compose -f "$COMPOSE_FILE" up -d
    print_success "Reconstruído e iniciado!"
    print_info "Acesse: http://localhost:8000"
}

function status() {
    docker compose -f "$COMPOSE_FILE" ps
}

function shell() {
    print_info "Abrindo shell no container..."
    docker compose -f "$COMPOSE_FILE" exec pm2-log-viewer /bin/bash
}

function users() {
    print_info "Gerenciamento de usuários..."
    
    if [ -z "$2" ]; then
        print_info "Use: $0 users [list|create|delete|passwd]"
        return
    fi
    
    case "$2" in
        list)
            docker exec -it pm2-log-viewer python manage_users.py list
            ;;
        create)
            docker exec -it pm2-log-viewer python manage_users.py create
            ;;
        delete)
            docker exec -it pm2-log-viewer python manage_users.py delete
            ;;
        passwd)
            docker exec -it pm2-log-viewer python manage_users.py passwd
            ;;
        *)
            print_error "Comando de usuário inválido: $2"
            print_info "Comandos disponíveis: list, create, delete, passwd"
            ;;
    esac
}

function enable_auth() {
    print_info "Habilitando autenticação..."
    print_info "Edite o arquivo compose.yml e altere:"
    echo ""
    echo "  - AUTH_ENABLED=true"
    echo ""
    print_info "Depois execute: $0 restart"
}

function disable_auth() {
    print_info "Desabilitando autenticação..."
    print_info "Edite o arquivo compose.yml e altere:"
    echo ""
    echo "  - AUTH_ENABLED=false"
    echo ""
    print_info "Depois execute: $0 restart"
}

function usage() {
    cat << EOF
Uso: $0 [comando]

Comandos disponíveis:
    start       Inicia o container
    stop        Para o container
    restart     Reinicia o container
    logs        Mostra os logs do container (Ctrl+C para sair)
    build       Reconstrói a imagem Docker
    rebuild     Reconstrói e reinicia completamente
    status      Mostra o status do container
    shell       Abre um shell dentro do container
    users       Gerencia usuários (list|create|delete|passwd)
    enable-auth Instruções para habilitar autenticação
    disable-auth Instruções para desabilitar autenticação
    help        Mostra esta mensagem

Exemplos:
    $0 start
    $0 logs
    $0 rebuild
    $0 users list
    $0 users create

EOF
}

# Main
check_docker

case "${1:-help}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    build)
        build
        ;;
    rebuild)
        rebuild
        ;;
    status)
        status
        ;;
    shell)
        shell
        ;;
    users)
        users "$@"
        ;;
    enable-auth)
        enable_auth
        ;;
    disable-auth)
        disable_auth
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        print_error "Comando inválido: $1"
        echo ""
        usage
        exit 1
        ;;
esac
