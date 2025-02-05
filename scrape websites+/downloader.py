import os
import requests
import aiohttp
import asyncio
from urllib.parse import urlparse

async def download_files_async(urls, folder, base_url):
    """Scarica i file in modalità asincrona."""
    async with aiohttp.ClientSession() as session:
        tasks = [download_file_async(url, folder, base_url, session) for url in urls]
        await asyncio.gather(*tasks)

async def download_file_async(url, folder, base_url, session):
    """Scarica un singolo file in modalità asincrona."""
    try:
        # Crea la cartella se non esiste
        os.makedirs(folder, exist_ok=True)

        # Estrai il nome del file dall'URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        filepath = os.path.join(folder, filename)

        async with session.get(url) as response:
          if response.status == 200:
            with open(filepath, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024) # Leggi 1KB alla volta
                    if not chunk:
                        break
                    f.write(chunk)
          else:
            print(f"Errore {response.status} durante il download di {url}")

    except Exception as e:
        print(f"Errore durante il download di {url}: {e}")

def download_files(urls, folder, base_url):
    """Scarica i file in modalità sincrona."""
    for url in urls:
        download_file(url, folder, base_url)

def download_file(url, folder, base_url):
    """Scarica un singolo file in modalità sincrona."""
    try:
        # Crea la cartella se non esiste
        os.makedirs(folder, exist_ok=True)

        # Estrai il nome del file dall'URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        filepath = os.path.join(folder, filename)

        # Scarica il file
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Gestione degli errori HTTP

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download di {url}: {e}")
    except Exception as e:
        print(f"Errore durante il download di {url}: {e}")