def get_user_input():
    """
    Ottiene l'input dell'utente tramite input() o interfaccia grafica.
    Restituisce un dizionario con la configurazione.
    """
    links = input("Inserisci i link separati da virgola: ").split(',')
    features_str = input("Inserisci le feature da estrarre separate da virgola (es. testo,immagini,link): ").split(',')
    mode = input("Modalità sincrona o asincrona (sync/async): ")

    features = [f.strip() for f in features_str]

    return {
        'links': [link.strip() for link in links],
        'features': features,
        'mode': mode
    }

def configure(user_config):
    """
    Configura il programma in base all'input dell'utente.
    Ad esempio, imposta le variabili globali, carica le configurazioni da file, etc.
    """
    # Qui puoi implementare la logica di configurazione, ad esempio:
    global MODE
    MODE = user_config['mode']
    # ... altre configurazioni ...