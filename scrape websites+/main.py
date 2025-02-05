import config
import scraper
import asyncio
import yt_dlp

async def main():
    """
    Punto di ingresso del programma.
    """
    # 1. Ottieni l'input dell'utente (lista di link, feature da estrarre, modalità sincrona/asincrona)
    user_config = config.get_user_input()

    # 2. Configura il programma in base all'input dell'utente
    config.configure(user_config)

    # 3. Crea un'istanza dello Scraper
    scraper_instance = scraper.Scraper(user_config['links'], user_config['features'])

    # 4. Avvia il processo di scraping
    if user_config['mode'] == 'async':
        await scraper_instance.run_async()
    else:
        scraper_instance.run_sync()

    # 5. Logica di prova per il download del video (solo se "video" è selezionato e c'è almeno un URL)
    if 'video' in user_config['features'] and user_config['links']:
        print("Esecuzione della logica di prova per il download del video...")
        # Prendi solo il primo URL per la prova - CORRETTO
        url = user_config['links'][0]

        # Verifica se l'URL è un video di YouTube
        if "youtube.com" in url or "youtu.be" in url:
            ydl_opts = {
                'outtmpl': '%(title)s.%(ext)s',
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download([url])  # Usa l'URL preso dall'input

                if error_code == 0:
                    print("Download di prova completato con successo!")
                else:
                    print("Si è verificato un errore durante il download di prova.")
            except yt_dlp.utils.DownloadError as e:
                print(f"Errore durante il download di prova: {e}")
            except Exception as e:
                print(f"Errore inaspettato: {e}")
        else:
            print("L'URL fornito non sembra essere un video di YouTube valido per la prova.")
    else:
        print("L'utente non ha selezionato 'video' o non ha fornito URL, la logica di prova non verrà eseguita.")

if __name__ == "__main__":
    asyncio.run(main())