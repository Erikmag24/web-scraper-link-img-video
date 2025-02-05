import os
import json
from urllib.parse import urljoin

def save_results(results):
    """
    Salva i risultati in un file JSON.
    """
    with open('results.json', 'a') as f:
        json.dump(results, f, indent=4)

def make_absolute_url(url, base_url):
    """Converte un URL relativo in un URL assoluto."""
    if url.startswith('http'):
        return url
    else:
        return urljoin(base_url, url)

# Aggiungi altre funzioni di utilità...