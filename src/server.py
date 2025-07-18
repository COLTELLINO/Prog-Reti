#!/usr/bin/env python3

import socket
import threading
import os
import datetime
import mimetypes
import urllib.parse
import logging
from pathlib import Path

class SimpleHTTPServer:
    def __init__(self, host='localhost', port=8080, document_root='www'):
        self.host = host
        self.port = port
        self.document_root = Path(__file__).parent / document_root
        
        self.setup_logging()
        
        self.setup_mime_types()
        
        self.stats = {
            'requests_count': 0,
            'start_time': datetime.datetime.now(),
            'status_codes': {},
            'requested_files': {}
        }
        
        self.logger.info(f"Server inizializzato su {host}:{port}")
        self.logger.info(f"Document root: {self.document_root}")
    
    def setup_logging(self):
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger('HTTPServer')
        self.logger.setLevel(logging.INFO)
        
        file_handler = logging.FileHandler(
            log_dir / f'server_{datetime.datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def setup_mime_types(self):
        self.mime_types = {
            '.html': 'text/html; charset=utf-8',
            '.htm': 'text/html; charset=utf-8',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.ico': 'image/x-icon',
            '.svg': 'image/svg+xml',
            '.txt': 'text/plain; charset=utf-8',
            '.pdf': 'application/pdf',
            '.zip': 'application/zip'
        }
    
    def get_mime_type(self, file_path):
        extension = Path(file_path).suffix.lower()
        return self.mime_types.get(extension, 'application/octet-stream')
    
    def parse_request(self, request_data):
        lines = request_data.strip().split('\r\n')
        if not lines:
            return None
        
        request_line = lines[0]
        parts = request_line.split(' ')
        
        if len(parts) != 3:
            return None
        
        method, path, version = parts
        
        headers = {}
        for line in lines[1:]:
            if line == '':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip().lower()] = value.strip()
        
        path = urllib.parse.unquote(path)
        
        return {
            'method': method,
            'path': path,
            'version': version,
            'headers': headers
        }
    
    def build_response(self, status_code, headers=None, body=b''):
        status_messages = {
            200: 'OK',
            404: 'Not Found',
            405: 'Method Not Allowed',
            500: 'Internal Server Error'
        }
        
        status_message = status_messages.get(status_code, 'Unknown')
        
        response = f"HTTP/1.1 {status_code} {status_message}\r\n"
        
        default_headers = {
            'Server': 'SimpleHTTPServer/1.0 (Python)',
            'Date': datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Connection': 'close'
        }
        
        if headers:
            default_headers.update(headers)
        
        if 'content-length' not in [h.lower() for h in default_headers.keys()]:
            default_headers['Content-Length'] = str(len(body))
        
        for key, value in default_headers.items():
            response += f"{key}: {value}\r\n"
        
        response += "\r\n"
        
        return response.encode('utf-8') + body
    
    def serve_file(self, file_path):
        try:
            if not file_path.exists():
                return self.serve_404()
            
            if file_path.is_dir():
                for index_file in ['index.html', 'index.htm']:
                    index_path = file_path / index_file
                    if index_path.exists():
                        file_path = index_path
                        break
                else:
                    return self.generate_directory_listing(file_path)
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            mime_type = self.get_mime_type(str(file_path))
            
            headers = {
                'Content-Type': mime_type,
                'Last-Modified': datetime.datetime.fromtimestamp(
                    file_path.stat().st_mtime
                ).strftime('%a, %d %b %Y %H:%M:%S GMT')
            }
            
            return 200, headers, content
            
        except Exception as e:
            self.logger.error(f"Errore nel servire il file {file_path}: {e}")
            return 500, {'Content-Type': 'text/html'}, b'<h1>500 Internal Server Error</h1>'
    
    def serve_404(self):
        custom_404 = self.document_root / '404.html'
        if custom_404.exists():
            try:
                with open(custom_404, 'rb') as f:
                    content = f.read()
                return 404, {'Content-Type': 'text/html; charset=utf-8'}, content
            except:
                pass
        
        html_content = """
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>404 - Pagina Non Trovata</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 10px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                }
                h1 { font-size: 4em; margin: 0; }
                p { font-size: 1.2em; }
                a { color: #fff; text-decoration: underline; }
                .error-code { font-size: 8em; font-weight: bold; opacity: 0.3; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-code">404</div>
                <h1>Pagina Non Trovata</h1>
                <p>La risorsa richiesta non è stata trovata su questo server.</p>
                <p><a href="/">← Torna alla Home</a></p>
            </div>
        </body>
        </html>
        """
        return 404, {'Content-Type': 'text/html; charset=utf-8'}, html_content.encode('utf-8')
    
    def generate_directory_listing(self, dir_path):
        try:
            items = []
            for item in sorted(dir_path.iterdir()):
                if item.name.startswith('.'):
                    continue
                
                relative_path = item.relative_to(self.document_root)
                if item.is_dir():
                    items.append(f'<li><a href="/{relative_path}/">{item.name}/</a></li>')
                else:
                    size = item.stat().st_size
                    size_str = self.format_file_size(size)
                    items.append(f'<li><a href="/{relative_path}">{item.name}</a> ({size_str})</li>')
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="it">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Directory Listing - /{dir_path.relative_to(self.document_root)}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #333; }}
                    ul {{ list-style: none; padding: 0; }}
                    li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
                    a {{ text-decoration: none; color: #0066cc; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h1>Directory: /{dir_path.relative_to(self.document_root)}</h1>
                <ul>
                    <li><a href="../">.. (Parent Directory)</a></li>
                    {''.join(items)}
                </ul>
            </body>
            </html>
            """
            
            return 200, {'Content-Type': 'text/html; charset=utf-8'}, html_content.encode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Errore nel generare directory listing: {e}")
            return 500, {'Content-Type': 'text/html'}, b'<h1>500 Internal Server Error</h1>'
    
    def format_file_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def handle_stats_request(self):
        uptime = datetime.datetime.now() - self.stats['start_time']
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Statistiche Server</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{ color: #333; }}
                .stat {{ 
                    display: flex; 
                    justify-content: space-between; 
                    padding: 10px 0; 
                    border-bottom: 1px solid #eee;
                }}
                .stat:last-child {{ border-bottom: none; }}
                .value {{ font-weight: bold; color: #0066cc; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Statistiche Server</h1>
                <div class="stat">
                    <span>Richieste totali:</span>
                    <span class="value">{self.stats['requests_count']}</span>
                </div>
                <div class="stat">
                    <span>Tempo di attività:</span>
                    <span class="value">{uptime}</span>
                </div>
                <div class="stat">
                    <span>Server avviato:</span>
                    <span class="value">{self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="stat">
                    <span>Host:</span>
                    <span class="value">{self.host}:{self.port}</span>
                </div>
                <h2>Codici di Stato</h2>
                {''.join([f'<div class="stat"><span>{code}:</span><span class="value">{count}</span></div>' for code, count in self.stats['status_codes'].items()])}
                
                <h2>File più Richiesti</h2>
                {''.join([f'<div class="stat"><span>{file}:</span><span class="value">{count}</span></div>' for file, count in sorted(self.stats['requested_files'].items(), key=lambda x: x[1], reverse=True)[:10]])}
            </div>
        </body>
        </html>
        """
        
        return 200, {'Content-Type': 'text/html; charset=utf-8'}, html_content.encode('utf-8')
    
    def handle_client(self, client_socket, client_address):
        try:
            request_data = client_socket.recv(1024).decode('utf-8')
            
            if not request_data:
                return
            
            self.stats['requests_count'] += 1
            
            self.logger.info(f"Richiesta da {client_address[0]}:{client_address[1]}")
            self.logger.debug(f"Request raw:\n{request_data}")
            
            request = self.parse_request(request_data)
            
            if not request:
                response = self.build_response(400, {'Content-Type': 'text/html'}, 
                                             b'<h1>400 Bad Request</h1>')
                client_socket.send(response)
                return
            
            method = request['method']
            path = request['path']
            
            self.logger.info(f"{method} {path} da {client_address[0]}")
            
            self.stats['requested_files'][path] = self.stats['requested_files'].get(path, 0) + 1
            
            if method == 'OPTIONS':
                headers = {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, HEAD, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Content-Type': 'text/plain'
                }
                response = self.build_response(200, headers, b'OK')
                status_code = 200
            elif method in ['GET', 'HEAD']:
                if path == '/stats':
                    status_code, headers, body = self.handle_stats_request()
                else:
                    if '?' in path:
                        path = path.split('?')[0]
                    
                    if path == '/':
                        path = '/index.html'
                    
                    file_path = self.document_root / path.lstrip('/')
                    
                    try:
                        file_path = file_path.resolve()
                        if not str(file_path).startswith(str(self.document_root.resolve())):
                            status_code, headers, body = self.serve_404()
                        else:
                            status_code, headers, body = self.serve_file(file_path)
                    except:
                        status_code, headers, body = self.serve_404()
                
                if method == 'HEAD':
                    response = self.build_response(status_code, headers, b'')
                else:
                    response = self.build_response(status_code, headers, body)
            else:
                self.logger.warning(f"Metodo {method} non supportato per {path}")
                status_code = 405
                headers = {
                    'Allow': 'GET, HEAD, OPTIONS',
                    'Content-Type': 'text/html'
                }
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>405 Method Not Allowed</title></head>
                <body>
                    <h1>405 Method Not Allowed</h1>
                    <p>Il metodo <strong>{method}</strong> non è supportato per questa risorsa.</p>
                    <p>Metodi supportati: GET, HEAD, OPTIONS</p>
                    <p><a href="/">← Torna alla Home</a></p>
                </body>
                </html>
                """.encode('utf-8')
                response = self.build_response(405, headers, error_html)
            
            self.stats['status_codes'][status_code] = self.stats['status_codes'].get(status_code, 0) + 1
            
            client_socket.send(response)
            
            if method == 'HEAD':
                self.logger.info(f"Risposta: {status_code} (HEAD - no body)")
            elif 'body' in locals():
                self.logger.info(f"Risposta: {status_code} ({len(body)} bytes)")
            else:
                self.logger.info(f"Risposta: {status_code} ({len(response)} bytes)")
            
        except Exception as e:
            self.logger.error(f"Errore nel gestire il client {client_address}: {e}")
            try:
                response = self.build_response(500, {'Content-Type': 'text/html'}, 
                                             b'<h1>500 Internal Server Error</h1>')
                client_socket.send(response)
            except:
                pass
        finally:
            client_socket.close()
    
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            self.logger.info(f"Server avviato su http://{self.host}:{self.port}")
            self.logger.info(f"Serving files from: {self.document_root}")
            self.logger.info(f"Statistiche disponibili su: http://{self.host}:{self.port}/stats")
            print(f"\nServer HTTP in ascolto su http://{self.host}:{self.port}")
            print("Premere Ctrl+C per fermare il server\n")
            
            while True:
                client_socket, client_address = server_socket.accept()
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            self.logger.info("Server fermato dall'utente")
            print("\nServer fermato")
        except Exception as e:
            self.logger.error(f"Errore del server: {e}")
            print(f"Errore del server: {e}")
        finally:
            server_socket.close()
            self.logger.info("Socket del server chiuso")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument('--host', default='localhost', help='Host address (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Port number (default: 8080)')
    parser.add_argument('--dir', default='www', help='Document root directory (default: www)')
    
    args = parser.parse_args()
    
    server = SimpleHTTPServer(args.host, args.port, args.dir)
    
    server.start()

if __name__ == '__main__':
    main()
