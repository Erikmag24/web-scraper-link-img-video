#!/usr/bin/env python3
import sys
import threading
import asyncio
import subprocess
import yt_dlp

# Importiamo i moduli che contengono le funzionalità esistenti.
# Supponiamo che il primo file (che contiene get_user_input, configure e l'async main) 
# sia in un modulo chiamato "config" e "scraper", mentre il secondo file (che esegue il Node.js crawler)
# venga ora integrato come funzione crawler_main.
import config
import scraper

def crawler_main(link):
    """
    Funzione per eseguire il crawler tramite lo script Node.js.
    Viene eseguito con lo stesso link passato come argomento.
    """
    try:
        result = subprocess.run(
            ['node', 'scraper.mjs', link],
            check=True,
            capture_output=True,
            text=True
        )
        print("[Crawler] Output:\n", result.stdout)
        if result.stderr:
            print("[Crawler] Errori:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        print("[Crawler] Il crawler ha incontrato un errore:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(e.returncode)

async def scraper_main(link):
    """
    Funzione wrapper per lo scraper. Invece di richiedere l'input all'utente,
    utilizziamo il link fornito come parametro.
    
    In questo esempio, costruiamo una configurazione fittizia con:
      - 'links': una lista contenente solo il link passato,
      - 'features': impostato almeno a ['video'] per attivare la logica di prova,
      - 'mode': 'async'
    """
    # Costruiamo la configurazione usando il link passato
    user_config = {
        'links': [link],
        'features': ['video'],  # Puoi aggiungere altre feature se necessario
        'mode': 'async'
    }
    
    # Configuriamo il programma (eventualmente impostando variabili globali o altre configurazioni)
    config.configure(user_config)
    
    # Creiamo l'istanza dello Scraper con i link e le feature specificate
    scraper_instance = scraper.Scraper(user_config['links'], user_config['features'])
    
    # Eseguiamo lo scraping in modalità asincrona
    await scraper_instance.run_async()
    
    # Logica di prova per il download del video (se 'video' è selezionato)
    if 'video' in user_config['features'] and user_config['links']:
        print("[Scraper] Esecuzione della logica di prova per il download del video...")
        url = user_config['links'][0]
        
        # Verifica se l'URL è un video di YouTube
        if "youtube.com" in url or "youtu.be" in url:
            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download([url])
                if error_code == 0:
                    print("[Scraper] Download completato con successo!")
                else:
                    print("[Scraper] Errore durante il download di prova.")
            except yt_dlp.utils.DownloadError as e:
                print(f"[Scraper] Errore durante il download: {e}")
            except Exception as e:
                print(f"[Scraper] Errore inaspettato: {e}")
        else:
            print("[Scraper] L'URL non sembra essere un video di YouTube valido.")
    else:
        print("[Scraper] La feature 'video' non è stata selezionata o non è stato fornito un URL, logica di prova non eseguita.")

def run_scraper(link):
    """
    Wrapper sincrono per l'esecuzione dell'async main dello scraper.
    """
    asyncio.run(scraper_main(link))

def main():
    # Verifica che l'URL di partenza sia stato passato come argomento
    if len(sys.argv) < 2:
        print("Errore: Devi fornire un URL di partenza come argomento.")
        print("Esempio di utilizzo: python script.py https://www.example.com")
        sys.exit(1)
    
    start_url = sys.argv[1]
    
    # Creiamo due thread: uno per lo scraper e uno per il crawler
    scraper_thread = threading.Thread(target=run_scraper, args=(start_url,))
    crawler_thread = threading.Thread(target=crawler_main, args=(start_url,))
    
    # Avviamo entrambi i thread
    scraper_thread.start()
    crawler_thread.start()
    
    # Attendiamo la terminazione di entrambi i thread
    scraper_thread.join()
    crawler_thread.join()

if __name__ == "__main__":
    main()
