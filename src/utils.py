
"""
Script di utilità per il Web Server HTTP
Fornisce comandi per gestione, testing e monitoraggio del server
"""

import argparse
import sys
import os
import subprocess
import time
import requests
import json
from pathlib import Path

def start_server(host='localhost', port=8080, directory='www'):
    """Avvia il server HTTP"""
    script_path = Path(__file__).parent / 'server.py'
    cmd = [sys.executable, str(script_path), '--host', host, '--port', str(port), '--dir', directory]
    
    print(f"🚀 Avvio server su http://{host}:{port}")
    print(f"📁 Document root: {directory}")
    print("📝 Premere Ctrl+C per fermare il server\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n🛑 Server fermato dall'utente")

def test_server(host='localhost', port=8080):
    """Esegue test di base sul server"""
    base_url = f"http://{host}:{port}"
    
    tests = [
        {'name': 'Homepage', 'url': '/', 'expected_status': 200},
        {'name': 'Intro Page', 'url': '/intro.html', 'expected_status': 200},
        {'name': 'Server Info', 'url': '/server.html', 'expected_status': 200},
        {'name': 'Header Info', 'url': '/header.html', 'expected_status': 200},
        {'name': 'Statistics', 'url': '/stats', 'expected_status': 200},
        {'name': 'CSS File', 'url': '/style.css', 'expected_status': 200},
        {'name': '404 Test', 'url': '/nonexistent.html', 'expected_status': 404},
        {'name': 'Directory Listing', 'url': '/icons/', 'expected_status': 200},
    ]
    
    print(f"🧪 Testing server su {base_url}")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            response = requests.get(base_url + test['url'], timeout=5)
            if response.status_code == test['expected_status']:
                print(f"✅ {test['name']}: {response.status_code}")
                passed += 1
            else:
                print(f"❌ {test['name']}: {response.status_code} (expected {test['expected_status']})")
                failed += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ {test['name']}: Connection error - {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Risultati: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 Tutti i test sono passati!")
        return True
    else:
        print("⚠️ Alcuni test sono falliti")
        return False

def benchmark_server(host='localhost', port=8080, requests_count=1000, concurrency=10):
    """Esegue benchmark di performance sul server"""
    base_url = f"http://{host}:{port}"
    
    print(f"🏃 Benchmark server su {base_url}")
    print(f"📊 Richieste: {requests_count}, Concorrenza: {concurrency}")
    print("=" * 50)
    
    
    import concurrent.futures
    import time
    
    def make_request():
        try:
            start_time = time.time()
            response = requests.get(base_url + '/', timeout=5)
            end_time = time.time()
            return {
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == 200
            }
        except:
            return {
                'status_code': 0,
                'response_time': 0,
                'success': False
            }
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(make_request) for _ in range(requests_count)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    end_time = time.time()
    total_time = end_time - start_time
    
    
    successful_requests = sum(1 for r in results if r['success'])
    failed_requests = len(results) - successful_requests
    response_times = [r['response_time'] for r in results if r['success']]
    
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        requests_per_second = successful_requests / total_time
    else:
        avg_response_time = min_response_time = max_response_time = requests_per_second = 0
    
    print(f"⏱️  Tempo totale: {total_time:.2f}s")
    print(f"✅ Richieste riuscite: {successful_requests}")
    print(f"❌ Richieste fallite: {failed_requests}")
    print(f"🚀 Richieste/secondo: {requests_per_second:.2f}")
    print(f"📈 Tempo risposta medio: {avg_response_time*1000:.2f}ms")
    print(f"⚡ Tempo risposta min: {min_response_time*1000:.2f}ms")
    print(f"🐌 Tempo risposta max: {max_response_time*1000:.2f}ms")

def check_dependencies():
    """Verifica le dipendenze necessarie"""
    print("🔍 Verifica dipendenze...")
    
    
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 7:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor} non supportata (richiede 3.7+)")
        return False
    
    
    required_modules = ['socket', 'threading', 'logging', 'pathlib', 'datetime', 'mimetypes']
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} non disponibile")
            return False
    
    
    optional_modules = ['requests']
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} (opzionale)")
        except ImportError:
            print(f"⚠️  {module} non disponibile (opzionale per testing)")
    
    
    server_file = Path(__file__).parent / 'server.py'
    www_dir = Path(__file__).parent / 'www'
    
    if server_file.exists():
        print(f"✅ server.py trovato")
    else:
        print(f"❌ server.py non trovato")
        return False
    
    if www_dir.exists():
        print(f"✅ directory www/ trovata")
    else:
        print(f"❌ directory www/ non trovata")
        return False
    
    print("🎉 Tutte le dipendenze sono soddisfatte!")
    return True

def show_stats(host='localhost', port=8080):
    """Mostra statistiche del server"""
    stats_url = f"http://{host}:{port}/stats"
    
    try:
        response = requests.get(stats_url, timeout=5)
        if response.status_code == 200:
            print(f"📊 Statistiche server da {stats_url}")
            print("=" * 50)
            
            print("✅ Server raggiungibile e statistiche disponibili")
            print(f"📝 Visualizza nel browser: {stats_url}")
        else:
            print(f"❌ Errore nel recupero statistiche: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossibile connettersi al server: {e}")

def create_config():
    """Crea file di configurazione esempio"""
    config = {
        "server": {
            "host": "localhost",
            "port": 8080,
            "document_root": "www"
        },
        "logging": {
            "level": "INFO",
            "file_rotation": True,
            "max_size": "10MB",
            "backup_count": 5
        },
        "security": {
            "allowed_methods": ["GET"],
            "max_request_size": 1024,
            "rate_limiting": False
        },
        "performance": {
            "thread_pool_size": 10,
            "connection_timeout": 30,
            "keep_alive": False
        }
    }
    
    config_file = Path(__file__).parent / 'config.json'
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"📄 File di configurazione creato: {config_file}")
    print("✏️  Modifica il file per personalizzare le impostazioni")

def main():
    parser = argparse.ArgumentParser(description='Utility per Web Server HTTP')
    subparsers = parser.add_subparsers(dest='command', help='Comandi disponibili')
    
    
    start_parser = subparsers.add_parser('start', help='Avvia il server')
    start_parser.add_argument('--host', default='localhost', help='Host address')
    start_parser.add_argument('--port', type=int, default=8080, help='Port number')
    start_parser.add_argument('--dir', default='www', help='Document root directory')
    
    
    test_parser = subparsers.add_parser('test', help='Esegue test sul server')
    test_parser.add_argument('--host', default='localhost', help='Host address')
    test_parser.add_argument('--port', type=int, default=8080, help='Port number')
    
    
    bench_parser = subparsers.add_parser('benchmark', help='Esegue benchmark di performance')
    bench_parser.add_argument('--host', default='localhost', help='Host address')
    bench_parser.add_argument('--port', type=int, default=8080, help='Port number')
    bench_parser.add_argument('--requests', type=int, default=1000, help='Numero di richieste')
    bench_parser.add_argument('--concurrency', type=int, default=10, help='Richieste concorrenti')
    
    
    subparsers.add_parser('check', help='Verifica dipendenze')
    
    
    stats_parser = subparsers.add_parser('stats', help='Mostra statistiche server')
    stats_parser.add_argument('--host', default='localhost', help='Host address')
    stats_parser.add_argument('--port', type=int, default=8080, help='Port number')
    
    
    subparsers.add_parser('config', help='Crea file di configurazione')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        start_server(args.host, args.port, args.dir)
    elif args.command == 'test':
        test_server(args.host, args.port)
    elif args.command == 'benchmark':
        benchmark_server(args.host, args.port, args.requests, args.concurrency)
    elif args.command == 'check':
        check_dependencies()
    elif args.command == 'stats':
        show_stats(args.host, args.port)
    elif args.command == 'config':
        create_config()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
