from search_engines import Google, Bing, Yahoo, Duckduckgo, Startpage, Aol, Dogpile, Ask, Mojeek, Brave, Torch

def search_multiple_engines_limited_results(query, num_results):
    """
    Effettua una query su più motori di ricerca e restituisce i primi 'num_results' risultati per ciascuno.

    Args:
        query (str): La query di ricerca da eseguire.
        num_results (int): Il numero massimo di risultati da restituire per motore di ricerca.

    Returns:
        dict: Un dizionario dove le chiavi sono i nomi dei motori di ricerca e i valori sono liste
              dei primi 'num_results' link trovati.
              Restituisce None se si verifica un errore durante la ricerca.
    """
    engines = {
        "Google": Google(),
        "Bing": Bing(),
        "Yahoo": Yahoo(),
        "DuckDuckGo": Duckduckgo(),
        "Startpage": Startpage(),
        "AOL": Aol(),
        "Dogpile": Dogpile(),
        "Ask": Ask(),
        "Mojeek": Mojeek(),
        "Brave": Brave(),
        "Torch": Torch(),
    }

    all_results = {}

    for engine_name, engine_instance in engines.items():
        print(f"Esecuzione query su {engine_name}...")
        try:
            results = engine_instance.search(query)
            links = results.links()[:num_results]  # Prendi solo i primi 'num_results' link
            all_results[engine_name] = links
            print(f"Risultati da {engine_name}: {len(links)} link trovati.")
        except Exception as e:
            print(f"Errore durante la ricerca con {engine_name}: {e}")
            all_results[engine_name] = [] # In caso di errore, salva una lista vuota per questo motore

    return all_results

