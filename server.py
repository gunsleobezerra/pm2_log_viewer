#!/usr/bin/env python3
import os
import json
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Diretório onde estão os logs (configurável via variável de ambiente)
LOG_DIR = os.environ.get('LOG_DIR', '/app/logs')

class LogServer(SimpleHTTPRequestHandler):
    def do_GET(self):
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
            start_time = query.get('start', [''])[0]
            end_time = query.get('end', [''])[0]
            
            # Construir o caminho completo do arquivo
            full_path = os.path.join(LOG_DIR, filename)
            if os.path.exists(full_path) and filename.endswith('.log'):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                lines = []
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        include = True
                        if search and search not in line.lower():
                            include = False
                        if include and start_time:
                            match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                            if not match or match[1] < start_time:
                                include = False
                        if include and end_time:
                            match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                            if not match or match[1] > end_time:
                                include = False
                        if include:
                            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line.rstrip().replace('\r', ''))
                            lines.append(clean_line)
                            if len(lines) >= 5000:  # Limite
                                break
                self.wfile.write(json.dumps(lines).encode())
            else:
                self.send_error(404)
        else:
            super().do_GET()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 9020), LogServer)
    print("Servidor rodando em http://localhost:9020")
    print("Abra index.html no navegador.")
    server.serve_forever()