# Server HTTP Minimale

Progetto di un server web minimale in Python per il servizio di pagine HTML statiche.

## Descrizione

Questo progetto implementa un semplice server HTTP in Python capace di servire un sito web statico. Il server gestisce richieste GET, HEAD e OPTIONS e restituisce file HTML, CSS, JavaScript e immagini dalla cartella "www".

## Come si usa

Richiesto un ambiente con Python 3. Aprire il file server.py e se necessario posizionarsi nella cartella contenente www/ e server.py. Il server si avvia eseguendo il file server.py. La connessione al server avviene tramite browser all'indirizzo: http://localhost:8080.

## Struttura del progetto

- server.py -> Codice del server
- www/ -> Contenuti del sito (HTML, immagini, CSS)
- www/index.html -> Pagina principale

## Funzionalità

- Gestione richieste GET, HEAD, OPTIONS con risposta 405 (Method Not Allowed) per metodi non supportati.
- Risposte HTTP con intestazioni corrette
- Supporto per file .html, .css, .js, .png, .jpg, .svg, .ico
- Risposta 404 per file non trovati
- Pagina statistiche del server (/stats)
- Logging delle richieste
- Directory listing per cartelle
- Gestione concorrente delle richieste

## Avvio del server

```bash
cd src
python server.py
```

Parametri opzionali:
```bash
python server.py --host localhost --port 8080 --dir www
```

Il server sarà disponibile su http://localhost:8080

Autore: Filippo Patrignani