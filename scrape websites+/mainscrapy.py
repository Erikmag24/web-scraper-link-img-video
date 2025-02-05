import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor

class LinkExtractorSpider(scrapy.Spider):
    name = "linkextractor"  # Nome univoco per lo spider
    # start_urls sarà definito dinamicamente nell'esecuzione

    def __init__(self, *args, **kwargs):
        # Recupera l'URL di partenza dagli argomenti (passato da CrawlerProcess)
        self.start_urls = [kwargs.get('start_url')]
        if not self.start_urls or not self.start_urls[0]:
            raise ValueError("Devi fornire uno start_url come argomento allo spider.")
        super(LinkExtractorSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
        """
        Funzione di callback principale per analizzare la pagina web e estrarre i link.
        """
        link_extractor = LinkExtractor()  # Inizializza LinkExtractor
        links = link_extractor.extract_links(response) # Estrai i link dalla risposta

        for link in links:
            yield { # Genera un dizionario (item) per ogni link
                'url': link.url,
                'text': link.text,
            }

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Utilizzo: python main.py <URL_PAGINA_DA_SCRAPARE>")
        sys.exit(1)

    start_url = sys.argv[1] # Ottieni l'URL dalla linea di comando

    process = CrawlerProcess({
        'FEED_FORMAT': 'jsonlines',   # Formato di output: JSON Lines
        'FEED_URI': 'links.jsonl',    # File di output: links.jsonl
        'LOG_LEVEL': 'INFO',         # Livello di log: INFO (solo informazioni importanti)
    })

    process.crawl(LinkExtractorSpider, start_url=start_url) # Avvia lo spider, passando l'URL
    process.start() # Avvia il processo di crawling (bloccante)

    print(f"Link salvati nel file: links.jsonl")