import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import time
import extractors
import utils

class Scraper:
    def __init__(self, links, features):
        self.links = links
        self.features = features
        self.results = {}  # Per salvare i risultati
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

    def run_sync(self):
        """
        Esegue lo scraping in modalità sincrona.
        """
        for link in self.links:
            self.results[link] = self.scrape_page(link)

        utils.save_results(self.results)

    async def run_async(self):
        """
        Esegue lo scraping in modalità asincrona.
        """
        tasks = [self.scrape_page_async(link) for link in self.links]
        results_list = await asyncio.gather(*tasks)

        for i, link in enumerate(self.links):
            self.results[link] = results_list[i]

        utils.save_results(self.results)

    def scrape_page(self, link):
        """
        Esegue lo scraping di una singola pagina in modalità sincrona.
        """
        page_data = {}
        try:
            response = requests.get(link, headers=self.headers)
            response.raise_for_status()  # Gestione degli errori HTTP

            soup = BeautifulSoup(response.content, 'html.parser')

            for feature in self.features:
                if feature == 'testo':
                    extractor = extractors.TextExtractor(soup, link)
                    page_data['testo'] = extractor.extract_sync()
                elif feature == 'immagini':
                    extractor = extractors.ImageExtractor(soup, link)
                    page_data['immagini'] = extractor.extract_sync()
                elif feature == 'link':
                    extractor = extractors.LinkExtractor(soup)
                    page_data['link'] = extractor.extract_sync()
                elif feature == 'video':
                    extractor = extractors.VideoExtractor(soup, link)
                    page_data['video'] = extractor.extract_sync()
                elif feature == 'email':
                    extractor = extractors.EmailExtractor(soup)
                    page_data['email'] = extractor.extract_sync()
                elif feature == 'numeri_telefono':
                    extractor = extractors.PhoneNumberExtractor(soup)
                    page_data['numeri_telefono'] = extractor.extract_sync()
                elif feature == 'documenti':
                    extractor = extractors.DocumentExtractor(soup, link)
                    page_data['documenti'] = extractor.extract_sync()

                # ... altri casi per altre feature ...
            time.sleep(1) # Rate limiting
        except requests.exceptions.RequestException as e:
            print(f"Errore durante la richiesta a {link}: {e}")
            page_data['error'] = str(e)
        except Exception as e:
            print(f"Errore durante l'estrazione da {link}: {e}")
            page_data['error'] = str(e)
        return page_data

    async def scrape_page_async(self, link):
        """
        Esegue lo scraping di una singola pagina in modalità asincrona.
        """
        page_data = {}
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(link) as response:
                    response.raise_for_status()
                    html_content = await response.text()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Esecuzione asincrona degli estrattori per una singola pagina
                tasks = []
                for feature in self.features:
                    if feature == 'testo':
                        extractor = extractors.TextExtractor(soup, link)
                        tasks.append(extractor.extract_async())
                    elif feature == 'immagini':
                        extractor = extractors.ImageExtractor(soup, link)
                        tasks.append(extractor.extract_async())
                    elif feature == 'link':
                        extractor = extractors.LinkExtractor(soup)
                        tasks.append(extractor.extract_async())
                    elif feature == 'video':
                        extractor = extractors.VideoExtractor(soup, link)
                        tasks.append(extractor.extract_async())
                    elif feature == 'email':
                        extractor = extractors.EmailExtractor(soup)
                        tasks.append(extractor.extract_async())
                    elif feature == 'numeri_telefono':
                        extractor = extractors.PhoneNumberExtractor(soup)
                        tasks.append(extractor.extract_async())
                    elif feature == 'documenti':
                        extractor = extractors.DocumentExtractor(soup, link)
                        tasks.append(extractor.extract_async())
                    # ... aggiungi altri estrattori ...

                results = await asyncio.gather(*tasks)

                # Assegna i risultati al dizionario page_data
                for i, feature in enumerate(self.features):
                    page_data[feature] = results[i]

                await asyncio.sleep(1) # Rate limiting
        except aiohttp.ClientError as e:
            print(f"Errore durante la richiesta a {link}: {e}")
            page_data['error'] = str(e)
        except Exception as e:
            print(f"Errore durante l'estrazione da {link}: {e}")
            page_data['error'] = str(e)
        return page_data