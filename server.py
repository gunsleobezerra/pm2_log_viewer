#!/usr/bin/env python3
import os
import json
import re
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from http import cookies
import urllib.parse

# Importar autenticação se habilitada
AUTH_ENABLED = os.environ.get('AUTH_ENABLED', 'false').lower() == 'true'
if AUTH_ENABLED:
    from auth import get_auth_manager

# Diretório onde estão os logs (configurável via variável de ambiente)
LOG_DIR = os.environ.get('LOG_DIR', '/app/logs')

def extract_timestamp_from_line(line):
    """
    Extrai timestamp de uma linha de log, suportando múltiplos formatos.
    Retorna um datetime object ou None se não encontrar timestamp válido.
    """
    # Formato: [DD-MM-YYYY HH:MM:SS] (usado pelo frontend)
    match = re.search(r'\[(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})\]', line)
    if match:
        try:
            return datetime.strptime(match[1], '%d-%m-%Y %H:%M:%S')
        except ValueError:
            pass
    
    # Formato: M/D/YYYY H:MM:SS AM/PM (logs do tipo frontend)
    match = re.search(r'(\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} (?:AM|PM))', line)
    if match:
        try:
            return datetime.strptime(match[1], '%m/%d/%Y %I:%M:%S %p')
        except ValueError:
            pass
    
    # Formato: Day, DD Mon YYYY HH:MM:SS GMT (logs de erro)
    match = re.search(r'(\w{3}, \d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2} GMT)', line)
    if match:
        try:
            return datetime.strptime(match[1], '%a, %d %b %Y %H:%M:%S GMT')
        except ValueError:
            pass
    
    # Formato: YYYY-MM-DD HH:MM:SS (ISO format)
    match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
    if match:
        try:
            return datetime.strptime(match[1], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
    
    # Formato JSON com timestamp Unix (logs do PM2 metrics)
    try:
        if line.strip().startswith('{'):
            data = json.loads(line.strip())
            if 'time' in data:
                return datetime.fromtimestamp(data['time'] / 1000)  # Converte de ms para s
    except (json.JSONDecodeError, ValueError, KeyError):
        pass
    
    return None

def parse_datetime_input(datetime_str):
    """
    Converte string de datetime-local do frontend para datetime object.
    Formato esperado: YYYY-MM-DDTHH:MM ou YYYY-MM-DD HH:MM:SS
    """
    if not datetime_str:
        return None
    
    # Remover segundos se vier do formato normalizado
    datetime_str = datetime_str.replace(':00', '', 1) if datetime_str.endswith(':00') else datetime_str
    
    try:
        # Formato: YYYY-MM-DDTHH:MM (datetime-local input)
        if 'T' in datetime_str:
            return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
        # Formato: YYYY-MM-DD HH:MM:SS (já normalizado)
        else:
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

class LogServer(SimpleHTTPRequestHandler):
    def _get_session_id(self):
        """Extrai o session_id dos cookies."""
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            print(f"DEBUG: Sem cookie header no path {self.path}")
            return None
        
        cookie = cookies.SimpleCookie()
        cookie.load(cookie_header)
        
        if 'session_id' in cookie:
            session_id = cookie['session_id'].value
            print(f"DEBUG: Session ID encontrado: {session_id[:20]}... para {self.path}")
            return session_id
        
        print(f"DEBUG: Cookie header presente mas sem session_id: {cookie_header}")
        return None
    
    def _is_authenticated(self):
        """Verifica se o usuário está autenticado."""
        if not AUTH_ENABLED:
            return True
        
        session_id = self._get_session_id()
        if not session_id:
            print(f"DEBUG: Sem session_id para {self.path}")
            return False
        
        auth_manager = get_auth_manager()
        is_valid = auth_manager.validate_session(session_id) is not None
        print(f"DEBUG: Sessão válida: {is_valid} para {self.path}")
        return is_valid
    
    def _send_json_response(self, data, status=200):
        """Envia resposta JSON."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_unauthorized(self):
        """Envia resposta de não autorizado."""
        self._send_json_response({'error': 'Unauthorized'}, 401)
    
    def _set_session_cookie(self, session_id):
        """Define o cookie de sessão."""
        cookie = cookies.SimpleCookie()
        cookie['session_id'] = session_id
        cookie['session_id']['path'] = '/'
        cookie['session_id']['httponly'] = True
        cookie['session_id']['samesite'] = 'Strict'
        # cookie['session_id']['secure'] = True  # Descomente se usar HTTPS
        self.send_header('Set-Cookie', cookie['session_id'].OutputString())
    
    def _clear_session_cookie(self):
        """Remove o cookie de sessão."""
        cookie = cookies.SimpleCookie()
        cookie['session_id'] = ''
        cookie['session_id']['path'] = '/'
        cookie['session_id']['max-age'] = 0
        self.send_header('Set-Cookie', cookie['session_id'].OutputString())
    
    def do_POST(self):
        """Trata requisições POST para login/logout."""
        if self.path == '/api/login':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode())
                username = data.get('username', '')
                password = data.get('password', '')
                
                if not AUTH_ENABLED:
                    self._send_json_response({'error': 'Authentication not enabled'}, 400)
                    return
                
                auth_manager = get_auth_manager()
                user_id = auth_manager.verify_credentials(username, password)
                
                if user_id:
                    session_id = auth_manager.create_session(user_id)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self._set_session_cookie(session_id)
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True}).encode())
                else:
                    self._send_json_response({'error': 'Invalid credentials'}, 401)
            except Exception as e:
                self._send_json_response({'error': str(e)}, 400)
        
        elif self.path == '/api/logout':
            if AUTH_ENABLED:
                session_id = self._get_session_id()
                if session_id:
                    auth_manager = get_auth_manager()
                    auth_manager.delete_session(session_id)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._clear_session_cookie()
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
        else:
            self.send_error(404)
    
    def do_GET(self):
        # Rotas públicas (não requerem autenticação)
        public_routes = ['/login.html', '/api/auth-status']
        
        # Verificar status de autenticação
        if self.path == '/api/auth-status':
            self._send_json_response({
                'enabled': AUTH_ENABLED,
                'authenticated': self._is_authenticated()
            })
            return
        
        # Verificar autenticação para rotas protegidas
        if AUTH_ENABLED and self.path not in public_routes:
            if not self._is_authenticated():
                # Redirecionar para login se for página HTML
                if self.path == '/' or self.path == '/index.html' or self.path.startswith('/file'):
                    self.send_response(302)
                    self.send_header('Location', '/login.html')
                    self.end_headers()
                else:
                    self._send_unauthorized()
                return
        
        if self.path == '/files':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            files = [f for f in os.listdir(LOG_DIR) if f.endswith('.log')]
            self.wfile.write(json.dumps(files).encode())
        elif self.path.startswith('/file/'):
            parsed = urllib.parse.urlparse(self.path)
            filename = urllib.parse.unquote(parsed.path[6:])
            query = urllib.parse.parse_qs(parsed.query)
            search = query.get('search', [''])[0].lower()
            start_time_str = query.get('start', [''])[0]
            end_time_str = query.get('end', [''])[0]
            
            # Converter strings de tempo para datetime objects
            start_time = parse_datetime_input(start_time_str)
            end_time = parse_datetime_input(end_time_str)
            
            # Construir o caminho completo do arquivo
            full_path = os.path.join(LOG_DIR, filename)
            if os.path.exists(full_path) and filename.endswith('.log'):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                lines = []
                
                # Ler todas as linhas do arquivo
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    all_lines = f.readlines()
                
                # Processar linhas de forma reversa (últimas primeiro)
                for line in reversed(all_lines):
                    include = True
                    
                    # Filtro de busca por texto
                    if search and search not in line.lower():
                        include = False
                    
                    # Filtro de data/hora
                    if include and (start_time or end_time):
                        line_timestamp = extract_timestamp_from_line(line)
                        if line_timestamp:
                            # Verificar se a linha está dentro do intervalo de tempo
                            if start_time and line_timestamp < start_time:
                                include = False
                            if include and end_time and line_timestamp > end_time:
                                include = False
                        else:
                            # Se não conseguir extrair timestamp e há filtros de data, excluir
                            if start_time or end_time:
                                include = False
                    
                    if include:
                        # Limpar códigos ANSI e caracteres especiais
                        clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line.rstrip().replace('\r', ''))
                        lines.append(clean_line)
                        if len(lines) >= 5000:  # Limite para evitar sobrecarga
                            break
                
                self.wfile.write(json.dumps(lines).encode())
            else:
                self.send_error(404)
        else:
            super().do_GET()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    server = HTTPServer(('0.0.0.0', port), LogServer)
    print(f"Servidor rodando em http://0.0.0.0:{port}")
    print("Abra index.html no navegador.")
    server.serve_forever()