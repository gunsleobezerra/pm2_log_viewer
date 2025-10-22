#!/usr/bin/env python3
"""
Script de inicialização de usuários.
Cria o usuário admin inicial se a autenticação estiver habilitada
e se não existir nenhum usuário no banco de dados.
"""
import os
import sys

# Verificar se a autenticação está habilitada
AUTH_ENABLED = os.environ.get('AUTH_ENABLED', 'false').lower() == 'true'

if not AUTH_ENABLED:
    print("Autenticação desabilitada. Nenhum usuário será criado.")
    sys.exit(0)

# Importar módulo de autenticação
try:
    from auth import get_auth_manager
except ImportError as e:
    print(f"Erro ao importar módulo de autenticação: {e}")
    sys.exit(1)

def init_admin_user():
    """Inicializa o usuário admin se não existir nenhum usuário."""
    auth_manager = get_auth_manager()
    
    # Verificar se já existem usuários
    user_count = auth_manager.get_user_count()
    
    if user_count > 0:
        print(f"Banco de dados já contém {user_count} usuário(s). Nenhum usuário será criado.")
        return
    
    # Obter credenciais do ambiente
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'changeme')
    
    # Criar usuário admin
    try:
        success = auth_manager.create_user(admin_username, admin_password)
        
        if success:
            print(f"✓ Usuário admin criado com sucesso!")
            print(f"  Username: {admin_username}")
            print(f"  Password: {admin_password}")
            print("\n⚠️  IMPORTANTE: Altere a senha padrão após o primeiro login!")
        else:
            print(f"✗ Erro ao criar usuário admin (usuário já pode existir)")
    except Exception as e:
        print(f"✗ Erro ao criar usuário admin: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("Inicializando sistema de autenticação...")
    print("=" * 60)
    
    try:
        init_admin_user()
        print("=" * 60)
        print("Inicialização concluída!")
        print("=" * 60)
    except Exception as e:
        print(f"Erro durante a inicialização: {e}")
        sys.exit(1)
