#!/usr/bin/env python3
"""
Utilitário de linha de comando para gerenciar usuários do PM2 Log Viewer.
"""
import os
import sys
import argparse
from getpass import getpass

# Configurar ambiente
os.environ.setdefault('AUTH_ENABLED', 'true')
os.environ.setdefault('AUTH_DB_PATH', '/app/data/auth.db')

try:
    from auth import get_auth_manager
except ImportError as e:
    print(f"Erro ao importar módulo de autenticação: {e}")
    sys.exit(1)


def list_users():
    """Lista todos os usuários."""
    auth_manager = get_auth_manager()
    users = auth_manager.list_users()
    
    if not users:
        print("Nenhum usuário cadastrado.")
        return
    
    print("\n" + "=" * 80)
    print(f"{'ID':<5} {'Usuário':<20} {'Criado em':<25} {'Último login':<25}")
    print("=" * 80)
    
    for user in users:
        user_id = user['id']
        username = user['username']
        created_at = user['created_at'] or 'N/A'
        last_login = user['last_login'] or 'Nunca'
        
        print(f"{user_id:<5} {username:<20} {created_at:<25} {last_login:<25}")
    
    print("=" * 80)
    print(f"Total: {len(users)} usuário(s)\n")


def create_user(username=None, password=None):
    """Cria um novo usuário."""
    auth_manager = get_auth_manager()
    
    if not username:
        username = input("Digite o nome de usuário: ").strip()
    
    if not username:
        print("Erro: nome de usuário não pode ser vazio.")
        return False
    
    if not password:
        password = getpass("Digite a senha: ")
        password_confirm = getpass("Confirme a senha: ")
        
        if password != password_confirm:
            print("Erro: as senhas não coincidem.")
            return False
    
    if len(password) < 4:
        print("Erro: a senha deve ter pelo menos 4 caracteres.")
        return False
    
    success = auth_manager.create_user(username, password)
    
    if success:
        print(f"✓ Usuário '{username}' criado com sucesso!")
        return True
    else:
        print(f"✗ Erro: usuário '{username}' já existe.")
        return False


def delete_user(username=None):
    """Deleta um usuário."""
    auth_manager = get_auth_manager()
    
    if not username:
        username = input("Digite o nome do usuário a deletar: ").strip()
    
    if not username:
        print("Erro: nome de usuário não pode ser vazio.")
        return False
    
    confirm = input(f"Tem certeza que deseja deletar o usuário '{username}'? (s/N): ").strip().lower()
    
    if confirm != 's':
        print("Operação cancelada.")
        return False
    
    success = auth_manager.delete_user(username)
    
    if success:
        print(f"✓ Usuário '{username}' deletado com sucesso!")
        return True
    else:
        print(f"✗ Erro: usuário '{username}' não encontrado.")
        return False


def change_password(username=None):
    """Altera a senha de um usuário."""
    auth_manager = get_auth_manager()
    
    if not username:
        username = input("Digite o nome do usuário: ").strip()
    
    if not username:
        print("Erro: nome de usuário não pode ser vazio.")
        return False
    
    password = getpass("Digite a nova senha: ")
    password_confirm = getpass("Confirme a nova senha: ")
    
    if password != password_confirm:
        print("Erro: as senhas não coincidem.")
        return False
    
    if len(password) < 4:
        print("Erro: a senha deve ter pelo menos 4 caracteres.")
        return False
    
    success = auth_manager.change_password(username, password)
    
    if success:
        print(f"✓ Senha do usuário '{username}' alterada com sucesso!")
        return True
    else:
        print(f"✗ Erro: usuário '{username}' não encontrado.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Gerenciador de usuários do PM2 Log Viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s list                          # Lista todos os usuários
  %(prog)s create                        # Cria usuário (modo interativo)
  %(prog)s create -u admin -p senha123   # Cria usuário com credenciais
  %(prog)s delete -u admin               # Deleta um usuário
  %(prog)s passwd -u admin               # Altera senha de um usuário
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando list
    subparsers.add_parser('list', help='Lista todos os usuários')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Cria um novo usuário')
    create_parser.add_argument('-u', '--username', help='Nome do usuário')
    create_parser.add_argument('-p', '--password', help='Senha do usuário')
    
    # Comando delete
    delete_parser = subparsers.add_parser('delete', help='Deleta um usuário')
    delete_parser.add_argument('-u', '--username', help='Nome do usuário')
    
    # Comando passwd
    passwd_parser = subparsers.add_parser('passwd', help='Altera a senha de um usuário')
    passwd_parser.add_argument('-u', '--username', help='Nome do usuário')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("\n" + "=" * 60)
    print("PM2 Log Viewer - Gerenciador de Usuários")
    print("=" * 60 + "\n")
    
    try:
        if args.command == 'list':
            list_users()
        elif args.command == 'create':
            create_user(args.username, args.password)
        elif args.command == 'delete':
            delete_user(args.username)
        elif args.command == 'passwd':
            change_password(args.username)
    except Exception as e:
        print(f"\n✗ Erro: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
