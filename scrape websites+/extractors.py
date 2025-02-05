import re
import os
import utils
import downloader
from bs4 import BeautifulSoup
import asyncio
import yt_dlp

class TextExtractor:
    def __init__(self, soup, link):
        self.soup = soup
        self.link = link
        self.methods = [
            self._extract_with_beautifulsoup,
            self._extract_with_regex,  # Aggiungi altri metodi di estrazione del testo
            # ...
        ]

    def extract_sync(self):
        """Estrae il testo in modalità sincrona, provando diversi metodi."""
        text = ""
        for method in self.methods:
            try:
                text = method()
                if text:
                    return text # Restituisci il testo non appena è disponibile
            except Exception as e:
                print(f"Errore con il metodo {method.__name__} per il testo: {e}")

        return text

    async def extract_async(self):
        """Estrae il testo in modalità asincrona, provando diversi metodi in parallelo."""
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, method) for method in self.methods]
        results = await asyncio.gather(*tasks)
        for text in results:
            if text:
                return text # Restituisci il testo non appena è disponibile

        return ""

    def _extract_with_beautifulsoup(self):
        """Estrae il testo usando BeautifulSoup."""
        text = self.soup.get_text(separator=' ', strip=True)
        return text

    def _extract_with_regex(self):
      """Estrae il testo usando espressioni regolari (esempio)."""
      text = ""
      for tag in self.soup.find_all(text=True):
          if tag.parent.name not in ['script', 'style']:  # Escludi script e style
              content = tag.strip()
              if content:
                  text += content + " "
      return text.strip()

class ImageExtractor:
    def __init__(self, soup, link):
        self.soup = soup
        self.link = link
        self.methods = [
            self._extract_with_beautifulsoup,
            # Aggiungi altri metodi di estrazione immagini
            # ...
        ]
        self.download_folder = 'downloaded_images'

    def extract_sync(self):
        """Estrae le immagini in modalità sincrona."""
        image_urls = []
        for method in self.methods:
            try:
                urls = method()
                if urls:
                    image_urls.extend(urls)
            except Exception as e:
                print(f"Errore con il metodo {method.__name__} per le immagini: {e}")
        
        # Scarica le immagini
        if image_urls:
          downloader.download_files(image_urls, self.download_folder, self.link)
        return list(set(image_urls)) # Rimuovi duplicati

    async def extract_async(self):
        """Estrae le immagini in modalità asincrona."""
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, method) for method in self.methods]
        results = await asyncio.gather(*tasks)
        image_urls = []
        for urls in results:
            if urls:
                image_urls.extend(urls)

        # Scarica le immagini
        if image_urls:
          await downloader.download_files_async(image_urls, self.download_folder, self.link)
        return list(set(image_urls)) # Rimuovi duplicati

    def _extract_with_beautifulsoup(self):
        """Estrae gli URL delle immagini usando BeautifulSoup."""
        image_urls = []
        for img_tag in self.soup.find_all('img'):
            src = img_tag.get('src')
            data_src = img_tag.get('data-src')  # Gestisci anche data-src
            
            if src:
              image_urls.append(utils.make_absolute_url(src, self.link))
            if data_src:
              image_urls.append(utils.make_absolute_url(data_src, self.link))
        return image_urls

class LinkExtractor:
    def __init__(self, soup):
        self.soup = soup
        self.methods = [
            self._extract_with_beautifulsoup,
            # Aggiungi altri metodi
            # ...
        ]

    def extract_sync(self):
        """Estrae i link in modalità sincrona."""
        links = []
        for method in self.methods:
            try:
                extracted_links = method()
                if extracted_links:
                    links.extend(extracted_links)
            except Exception as e:
                print(f"Errore con il metodo {method.__name__} per i link: {e}")
        return list(set(links)) # Rimuovi duplicati

    async def extract_async(self):
      """Estrae i link in modalità asincrona"""
      loop = asyncio.get_event_loop()
      tasks = [loop.run_in_executor(None, method) for method in self.methods]
      results = await asyncio.gather(*tasks)
      links = []
      for extracted_links in results:
          if extracted_links:
              links.extend(extracted_links)
      return list(set(links)) # Rimuovi duplicati

    def _extract_with_beautifulsoup(self):
        """Estrae i link usando BeautifulSoup."""
        links = []
        for a_tag in self.soup.find_all('a', href=True):
            links.append(a_tag['href'])
        return links

class VideoExtractor:
    def __init__(self, soup, link):
        self.soup = soup
        self.link = link
        self.methods = [
            self._extract_with_beautifulsoup,
            # Aggiungi altri metodi di estrazione video se necessario
            # ...
        ]
        self.download_folder = 'downloaded_videos'

    def extract_sync(self):
        """Estrae i video in modalità sincrona."""
        video_urls = []
        for method in self.methods:
            try:
                urls = method()
                if urls:
                    video_urls.extend(urls)
            except Exception as e:
                print(f"Errore con il metodo {method.__name__} per i video: {e}")

        if video_urls:
            self.download_videos_with_ytdlp(video_urls)  # Usa yt-dlp
        return list(set(video_urls))

    async def extract_async(self):
        """Estrae i video in modalità asincrona."""
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, method) for method in self.methods]
        results = await asyncio.gather(*tasks)
        video_urls = []
        for urls in results:
            if urls:
                video_urls.extend(urls)

        if video_urls:
            await self.download_videos_with_ytdlp_async(video_urls)  # Usa yt-dlp
        return list(set(video_urls))

    def _extract_with_beautifulsoup(self):
        """Estrae gli URL dei video usando BeautifulSoup."""
        video_urls = []
        for video_tag in self.soup.find_all('video'):
            src = video_tag.get('src')
            if src:
                video_urls.append(utils.make_absolute_url(src, self.link))
            for source_tag in video_tag.find_all('source'):
                src = source_tag.get('src')
                if src:
                    video_urls.append(utils.make_absolute_url(src, self.link))

        # iframe (e.g., YouTube, Vimeo, Dailymotion)
        for iframe_tag in self.soup.find_all('iframe'):
            src = iframe_tag.get('src')
            if src and any(domain in src for domain in ['youtube.com', 'vimeo.com', 'dailymotion.com']):
                video_urls.append(utils.make_absolute_url(src, self.link))

        # Link diretti (es. tag 'a' con href a .mp4, .webm, etc.)
        for a_tag in self.soup.find_all('a', href=True):
            if any(a_tag['href'].endswith(ext) for ext in ['.mp4', '.webm', '.ogg', '.mov']):
                video_urls.append(utils.make_absolute_url(a_tag['href'], self.link))

        return video_urls

    def download_videos_with_ytdlp(self, video_urls):
        """Scarica i video usando yt-dlp in modalità sincrona."""
        os.makedirs(self.download_folder, exist_ok=True)  # Crea la cartella se non esiste
        ydl_opts = {
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,  # Ignora i video che fanno parte di playlist
            # Aggiungi altre opzioni yt-dlp se necessario
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(video_urls)
            if error_code != 0:
                print(f"Errore durante il download con yt-dlp per alcuni video")

    async def download_videos_with_ytdlp_async(self, video_urls):
        """Scarica i video usando yt-dlp in modalità asincrona."""
        os.makedirs(self.download_folder, exist_ok=True)  # Crea la cartella se non esiste

        async def download_single_video(url):
            """Scarica un singolo video usando yt-dlp."""
            ydl_opts = {
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                'noplaylist': True,
                # Aggiungi altre opzioni yt-dlp se necessario
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    await loop.run_in_executor(None, lambda: ydl.download([url]))
                except Exception as e:
                    print(f"Errore durante il download di {url}: {e}")

        loop = asyncio.get_event_loop()
        tasks = [download_single_video(url) for url in video_urls]
        await asyncio.gather(*tasks)

class EmailExtractor:
    def __init__(self, soup):
        self.soup = soup
        self.methods = [
            self._extract_with_regex,
            # Aggiungi altri metodi
            # ...
        ]

    def extract_sync(self):
        """Estrae le email in modalità sincrona."""
        emails = []
        for method in self.methods:
            try:
                extracted_emails = method()
                if extracted_emails:
                    emails.extend(extracted_emails)
            except Exception as e:
                print(f"Errore con il metodo {method.__name__} per le email: {e}")
        return list(set(emails))

    async def extract_async(self):
      """Estrae le email in modalità asincrona"""
      loop = asyncio.get_event_loop()
      tasks = [loop.run_in_executor(None, method) for method in self.methods]
      results = await asyncio.gather(*tasks)
      emails = []
      for extracted_emails in results:
          if extracted_emails:
              emails.extend(extracted_emails)
      return list(set(emails))

    def _extract_with_regex(self):
        """Estrae le email usando espressioni regolari."""
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, self.soup.get_text())
        return emails

class PhoneNumberExtractor:
    def __init__(self, soup):
        self.soup = soup
        self.methods = [
            self._extract_with_regex,
            # Aggiungi altri metodi
            # ...
        ]

    def extract_sync(self):
      """Estrae i numeri di telefono in modalità sincrona."""
      phone_numbers = []
      for method in self.methods:
          try:
              extracted_numbers = method()
              if extracted_numbers:
                  phone_numbers.extend(extracted_numbers)
          except Exception as e:
              print(f"Errore con il metodo {method.__name__} per i numeri di telefono: {e}")
      return list(set(phone_numbers))

    async def extract_async(self):
      """Estrae i numeri di telefono in modalità asincrona"""
      loop = asyncio.get_event_loop()
      tasks = [loop.run_in_executor(None, method) for method in self.methods]
      results = await asyncio.gather(*tasks)
      phone_numbers = []
      for extracted_numbers in results:
          if extracted_numbers:
              phone_numbers.extend(extracted_numbers)
      return list(set(phone_numbers))

    def _extract_with_regex(self):
        """Estrae i numeri di telefono usando espressioni regolari."""
        phone_patterns = [
            r"\+?\d[\d -]{8,12}\d",  # Numeri internazionali e nazionali
            # Aggiungi altri pattern per altri formati se necessario
            # ...
        ]
        phone_numbers = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, self.soup.get_text())
            phone_numbers.extend(matches)
        return phone_numbers

class DocumentExtractor:
    def __init__(self, soup, link):
        self.soup = soup
        self.link = link
        self.methods = [
            self._extract_with_beautifulsoup,
            # Aggiungi altri metodi
            # ...
        ]
        self.download_folder = 'downloaded_documents'

    def extract_sync(self):
        """Estrae i documenti in modalità sincrona."""
        document_urls = []
        for method in self.methods:
            try:
                urls = method()
                if urls:
                    document_urls.extend(urls)
            except Exception as e:
                print(f"Errore con il metodo {method.__name__} per i documenti: {e}")

        if document_urls:
          downloader.download_files(document_urls, self.download_folder, self.link)
        return list(set(document_urls))

    async def extract_async(self):
        """Estrae i documenti in modalità asincrona."""
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(None, method) for method in self.methods]
        results = await asyncio.gather(*tasks)
        document_urls = []
        for urls in results:
            if urls:
                document_urls.extend(urls)

        if document_urls:
          await downloader.download_files_async(document_urls, self.download_folder, self.link)
        return list(set(document_urls))

    def _extract_with_beautifulsoup(self):
        """Estrae gli URL dei documenti usando BeautifulSoup."""
        document_urls = []
        for a_tag in self.soup.find_all('a', href=True):
            href = a_tag['href']
            if any(href.endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.txt']):
                document_urls.append(utils.make_absolute_url(href, self.link))
        return document_urls