import sqlite3
import os
from datetime import datetime

DB_FILE = 'scraper_database.db' # Nome del file del database SQLite

def create_tables():
    """
    Crea le tabelle 'search_results' e 'link_details' nel database se non esistono già.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_results (
        link_id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        search_engine_name TEXT,
        link_url TEXT UNIQUE,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS link_details (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_id INTEGER,
        feature_type TEXT,
        detail_value TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (link_id) REFERENCES search_results(link_id)
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database e tabelle create o già esistenti.")

def insert_search_results(query, search_engine_name, links):
    """
    Inserisce i risultati della ricerca (link) nella tabella 'search_results'.

    Args:
        query (str): La query di ricerca.
        search_engine_name (str): Il nome del motore di ricerca.
        links (list): Una lista di URL dei link trovati.

    Returns:
        list: Una lista di dizionari, ognuno contenente 'link_id' e 'link_url' per ogni link inserito con successo.
              Restituisce una lista vuota se nessun link viene inserito (o in caso di errore).
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    saved_links_info = []

    for link_url in links:
        try:
            cursor.execute("""
                INSERT INTO search_results (query, search_engine_name, link_url, timestamp)
                VALUES (?, ?, ?, ?)
            """, (query, search_engine_name, link_url, datetime.now()))
            link_id = cursor.lastrowid # Ottieni l'ID dell'ultima riga inserita
            conn.commit()
            saved_links_info.append({'link_id': link_id, 'link_url': link_url})
            print(f"Link salvato nel database: {link_url}") # Log di successo semplificato
        except sqlite3.IntegrityError:
            conn.rollback() # Rollback in caso di violazione di UNIQUE (link già esistente)
            print(f"Avviso: Link già presente nel database (UNIQUE constraint): {link_url}")
            cursor.execute("SELECT link_id FROM search_results WHERE link_url = ?", (link_url,))
            result = cursor.fetchone()
            if result:
                link_id = result[0]
                saved_links_info.append({'link_id': link_id, 'link_url': link_url})
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Errore SQLite durante l'inserimento del link {link_url}: {e}")
        except Exception as e:
            conn.rollback()
            print(f"Errore generico durante l'inserimento del link {link_url}: {e}")

    cursor.close()
    conn.close()
    return saved_links_info

def insert_link_details(link_id, feature_type, detail_value):
    """
    Inserisce i dettagli (feature) di un link nella tabella 'link_details'.

    Args:
        link_id (int): L'ID del link a cui sono associati i dettagli (chiave esterna da 'search_results').
        feature_type (str): Il tipo di feature estratta (es. 'testo', 'immagini', 'video').
        detail_value (str): Il valore della feature estratta (es. il testo, URL delle immagini, ecc.).
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO link_details (link_id, feature_type, detail_value)
            VALUES (?, ?, ?)
        """, (link_id, feature_type, detail_value))
        conn.commit()
        print(f"Dettaglio '{feature_type}' salvato per link_id: {link_id}") # Log di successo semplificato
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Errore SQLite durante l'inserimento dei dettagli del link (link_id: {link_id}, feature: {feature_type}): {e}")
    except Exception as e:
        conn.rollback()
        print(f"Errore generico durante l'inserimento dei dettagli del link (link_id: {link_id}, feature: {feature_type}): {e}")
    cursor.close()
    conn.close()

def fetch_link_details(link_id):
    """
    Recupera i dettagli di un link specifico dalla tabella 'link_details'.

    Args:
        link_id (int): L'ID del link di cui recuperare i dettagli.

    Returns:
        list: Una lista di tuple, dove ogni tupla contiene (feature_type, detail_value) per il link specificato.
              Restituisce una lista vuota se non vengono trovati dettagli.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT feature_type, detail_value FROM link_details WHERE link_id = ?", (link_id,))
        details = cursor.fetchall()
        print(f"Dettagli recuperati per link_id: {link_id}") # Log di successo semplificato
    except sqlite3.Error as e:
        print(f"Errore SQLite durante il recupero dei dettagli del link (link_id: {link_id}): {e}")
        details = [] # Restituisci una lista vuota in caso di errore
    except Exception as e:
        print(f"Errore generico durante il recupero dei dettagli del link (link_id: {link_id}): {e}")
        details = [] # Restituisci una lista vuota in caso di errore
    cursor.close()
    conn.close()
    return details

if __name__ == '__main__':
    create_tables() # Esempio di utilizzo: crea le tabelle se eseguito direttamente
    print("Funzioni del database definite nel file database.py")