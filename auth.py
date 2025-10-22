#!/usr/bin/env python3
"""
Módulo de autenticação com SQLite para o PM2 Log Viewer.
Gerencia usuários, sessões e verificação de credenciais.
"""
import os
import sqlite3
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from contextlib import contextmanager

# Configurações
DB_PATH = os.environ.get('AUTH_DB_PATH', '/app/data/auth.db')
SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '3600'))  # 1 hora padrão


class AuthManager:
    """Gerenciador de autenticação com SQLite."""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Garante que o diretório do banco de dados existe."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexões com o banco."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Tabela de sessões
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            
            # Índices para melhor performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON sessions(session_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON sessions(expires_at)
            ''')
    
    @staticmethod
    def _hash_password(password):
        """Gera hash seguro da senha usando SHA-256 com salt."""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    @staticmethod
    def _verify_password(password, password_hash):
        """Verifica se a senha corresponde ao hash armazenado."""
        try:
            salt, pwd_hash = password_hash.split('$')
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
        except ValueError:
            return False
    
    def create_user(self, username, password):
        """
        Cria um novo usuário.
        Retorna True se criado com sucesso, False se já existe.
        """
        try:
            password_hash = self._hash_password(password)
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, password_hash)
                )
                return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_credentials(self, username, password):
        """
        Verifica as credenciais do usuário.
        Retorna o ID do usuário se válido, None caso contrário.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, password_hash FROM users WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()
            
            if row and self._verify_password(password, row['password_hash']):
                # Atualiza o último login
                cursor.execute(
                    'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                    (row['id'],)
                )
                return row['id']
            return None
    
    def create_session(self, user_id):
        """
        Cria uma nova sessão para o usuário.
        Retorna o ID da sessão.
        """
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(seconds=SESSION_TIMEOUT)
        expires_at_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)',
                (session_id, user_id, expires_at_str)
            )
        
        return session_id
    
    def validate_session(self, session_id):
        """
        Valida uma sessão.
        Retorna o user_id se válida, None caso contrário.
        Remove sessões expiradas.
        """
        if not session_id:
            return None
        
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Limpar sessões expiradas
            cursor.execute(
                'DELETE FROM sessions WHERE expires_at < ?',
                (now_str,)
            )
            
            # Verificar sessão atual
            cursor.execute(
                'SELECT user_id FROM sessions WHERE session_id = ? AND expires_at > ?',
                (session_id, now_str)
            )
            row = cursor.fetchone()
            
            if row:
                # Renovar sessão (sliding expiration)
                new_expires_at = datetime.now() + timedelta(seconds=SESSION_TIMEOUT)
                new_expires_at_str = new_expires_at.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    'UPDATE sessions SET expires_at = ? WHERE session_id = ?',
                    (new_expires_at_str, session_id)
                )
                return row['user_id']
            
            return None
    
    def delete_session(self, session_id):
        """Deleta uma sessão (logout)."""
        if not session_id:
            return
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    
    def get_user_count(self):
        """Retorna o número total de usuários cadastrados."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) as count FROM users')
            return cursor.fetchone()['count']
    
    def list_users(self):
        """Lista todos os usuários (sem senhas)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, created_at, last_login FROM users ORDER BY username')
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_user(self, username):
        """Deleta um usuário e suas sessões."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            return cursor.rowcount > 0
    
    def change_password(self, username, new_password):
        """Altera a senha de um usuário."""
        password_hash = self._hash_password(new_password)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET password_hash = ? WHERE username = ?',
                (password_hash, username)
            )
            return cursor.rowcount > 0


# Instância global do gerenciador de autenticação
_auth_manager = None

def get_auth_manager():
    """Retorna a instância única do AuthManager (singleton)."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager
