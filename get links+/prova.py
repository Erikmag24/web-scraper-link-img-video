import threading
import asyncio
import time
import json
from datetime import datetime
import sqlite3
import os
import sys
from main import search_multiple_engines_limited_results
from serpapi_code import SearchConfig, SearchEngine, LinkExtractor
from unifiedscraper import gather_links

scrape_website_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scrape websites+'))
sys.path.append(scrape_website_path)
import database  # Import the database module
import scraper   # Import the scraper module

DATABASE_NAME = database.DB_FILE  # Use DB_FILE from database.py

def create_database_and_tables():
    """
    Crea il database SQLite e le tabelle necessarie se non esistono.
    Uses database.create_tables() from database.py
    """
    database.create_tables() # Call the function from database.py
    print("Database and tables created or already exist (using database.py).")


def save_results_to_db(results_dict, script_name, query):
    """
    Salva i risultati della ricerca nel database SQLite using database.insert_search_results.
    """
    saved_links_info = []
    print(f"\n--- save_results_to_db called for script: {script_name} ---") # Debugging: function entry
    print(f"results_dict: {results_dict}") # Debugging: print results_dict

    if not results_dict: # Check if results_dict is empty
        print("**Warning: results_dict is empty. No links to save.**")
        return [] # Return empty list if no results

    for engine_name, links in results_dict.items():
        print(f"  Processing engine: {engine_name}") # Debugging: engine loop
        if not links: # Check if links list is empty for this engine
            print(f"  **Warning: No links found for engine: {engine_name}. Skipping.**")
            continue # Skip to the next engine if no links

        print(f"  Saving results for engine: {engine_name} from {script_name}...") # Added logging
        for link in links:
            print(f"    Attempting to save link: {link} from engine: {engine_name}") # Debugging log
            # Insert each link and get back link_info which contains link_id and link_url
            link_info_list = database.insert_search_results(query, f"{script_name}-{engine_name}", [link]) # Note: insert_search_results expects a list of links, even if it's one.
            print(f"    database.insert_search_results returned: {link_info_list}") # Debugging: print return value of insert_search_results

            if link_info_list: # Check if insertion was successful (returns a list if successful)
                link_info = link_info_list[0] # Extract the link_info dict from the list
                saved_links_info.append(link_info) # Append the link_info dict directly
                print(f"    Saved link: {link} with link_id: {link_info['link_id']}") # Detailed logging, accessing link_id from the returned dict
            else:
                print(f"    **Error: Failed to save link: {link}**") # Log failure to save

    print(f"Risultati da {script_name} salvati nel database.")
    print(f"  Returning saved_links_info: {saved_links_info}") # Debugging: return value
    print(f"--- save_results_to_db finished for script: {script_name} ---\n") # Debugging: function exit
    return saved_links_info


def run_main_search(query, num_results, all_results_dict):
    print("Starting search with main.py...")
    results_main = search_multiple_engines_limited_results(query, num_results)
    if results_main:
        print("\nResults from main.py:")
        for engine, links in results_main.items():
            print(f"- {engine}: Found {len(links)} links from {engine}") # Show link count
            for link in links:
                print(f"  - {link}")
        all_results_dict['main'] = results_main # Store results in the dictionary
    else:
        print("Error in main.py search or no results.")
        all_results_dict['main'] = {} # Store empty dict in case of error
    print("Finished search with main.py.\n")


def run_serpapi_search(query, num_results, engines_str, all_results_dict):
    print("Starting search with serpapi_code.py...")
    engines_serpapi = []
    valid_engines = [e.value for e in SearchEngine]
    for engine_name in engines_str:
        engine_name_upper = engine_name.upper()
        if engine_name_upper in [e.name for e in SearchEngine]:
             engines_serpapi.append(SearchEngine[engine_name_upper])
        else:
            print(f"Warning: Search engine '{engine_name}' is not valid for serpapi_code.py. Valid engines are: {valid_engines}")

    if not engines_serpapi:
        print("No valid search engines selected for serpapi_code.py. Skipping.")
        all_results_dict['serpapi'] = {} # Store empty dict if no valid engines
        return

    config_serpapi = SearchConfig(query=query, num_links=num_results, engines=engines_serpapi)
    extractor = LinkExtractor(config_serpapi)

    try:
        results_serpapi_async = extractor.extract_links()
        results_serpapi = asyncio.run(results_serpapi_async)

        print("\nResults from serpapi_code.py:")
        for engine, links in results_serpapi.items():
            print(f"- {engine}: Found {len(links)} links from {engine}") # Show link count
            for link in links:
                print(f"  - {link}")
        all_results_dict['serpapi'] = results_serpapi # Store results in the dictionary
    except Exception as e:
        print(f"Error in serpapi_code.py search: {e}")
        all_results_dict['serpapi'] = {} # Store empty dict in case of error

    print("Finished search with serpapi_code.py.\n")


def run_unifiedscraper_search(query, num_results, engines_str, all_results_dict):
    print("Starting search with unifiedscraper.py...")
    results_unified = {}
    for engine_name in engines_str:
        print(f"Searching with unifiedscraper.py - Engine: {engine_name}...")
        links = gather_links(query, engine_name, num_results)
        results_unified[engine_name] = links
        print(f"Results from unifiedscraper.py - Engine: {engine_name}: {len(links)} links found.")

    print("\nResults from unifiedscraper.py:")
    for engine, links in results_unified.items():
        print(f"- {engine}: Found {len(links)} links from {engine}") # Show link count
        for link in links:
            print(f"  - {link}")
    all_results_dict['unifiedscraper'] = results_unified # Store results in the dictionary
    print("Finished search with unifiedscraper.py.\n")

def extract_and_save_details(link_id, link_url, features, mode):
    """
    Extracts details from a link using scraper.py and saves them to the database.
    """
    print(f"Starting detail extraction ({mode}) for link ID: {link_id}, URL: {link_url}, Features: {features}") # Log start of extraction
    scraper_instance = scraper.Scraper([link_url], features)
    if mode == 'async':
        asyncio.run(scraper_instance.run_async())
    else:
        scraper_instance.run_sync()

    results = scraper_instance.results.get(link_url, {}) # Get results for the specific link
    print(f"Raw extraction results for link ID: {link_id}, URL: {link_url}: {results}") # Debugging: print raw results

    if results:
        print(f"Extraction results for link ID: {link_id}, URL: {link_url}: Features: {features}") # Log extraction results
        for feature_type, detail_value in results.items():
            if feature_type != 'error': # Don't save error details as features
                # Ensure detail_value is not None before saving
                if detail_value is not None:
                    print(f"  Attempting to save feature '{feature_type}': {str(detail_value)[:100]}... for link ID: {link_id}") # Debugging log
                    database.insert_link_details(link_id, feature_type, str(detail_value)) # Convert lists/dicts to string before saving
                    print(f"  Saved feature '{feature_type}': {str(detail_value)[:100]}... for link ID: {link_id}") # Log saved feature (truncated value)
                else:
                    print(f"  Feature '{feature_type}' is None, not saving for link ID: {link_id}") # Log if feature is None
            elif 'error' in results:
                print(f"  Attempting to save error: {str(results['error'])} for link ID: {link_id}") # Debugging log
                database.insert_link_details(link_id, 'error', str(results['error'])) # Save error if present
                print(f"  Saved error: {str(results['error'])} for link ID: {link_id}") # Log saved error
    else:
        # Save a general error if no results were obtained from scraping
        print(f"  Attempting to save general error for link ID: {link_id}") # Debugging log
        database.insert_link_details(link_id, 'error', "No details extracted or scraping failed.")
        print(f"**Warning: Detail extraction failed or no details found ({mode})** for link ID: {link_id}, URL: {link_url}") # Modified message
    print(f"Details extracted and saved ({mode}) for link ID: {link_id}, URL: {link_url}")


async def async_extract_and_save_details(link_id, link_url, features, mode): # Async version for better concurrency if needed
    """
    Asynchronous version of extract_and_save_details for concurrent extraction.
    """
    print(f"Starting detail extraction (async) for link ID: {link_id}, URL: {link_url}, Features: {features}") # Log start of async extraction
    scraper_instance = scraper.Scraper([link_url], features)
    await scraper_instance.run_async() # Force async run

    results = scraper_instance.results.get(link_url, {})
    print(f"Raw async extraction results for link ID: {link_id}, URL: {link_url}: {results}") # Debugging: print raw async results

    if results:
        print(f"Extraction results (async) for link ID: {link_id}, URL: {link_url}: Features: {features}") # Log async extraction results
        for feature_type, detail_value in results.items():
            if feature_type != 'error':
                if detail_value is not None: # Check for None value before saving
                    print(f"  Attempting to save feature '{feature_type}': {str(detail_value)[:100]}... (async) for link ID: {link_id}") # Debugging log
                    database.insert_link_details(link_id, feature_type, str(detail_value))
                    print(f"  Saved feature '{feature_type}': {str(detail_value)[:100]}... (async) for link ID: {link_id}") # Log saved feature (truncated value)
                else:
                    print(f"  Feature '{feature_type}' is None (async), not saving for link ID: {link_id}")
            elif 'error' in results:
                print(f"  Attempting to save error: {str(results['error'])} (async) for link ID: {link_id}") # Debugging log
                database.insert_link_details(link_id, 'error', str(results['error']))
                print(f"  Saved error: {str(results['error'])} (async) for link ID: {link_id}") # Corrected line, added missing parenthesis
    else:
        print(f"  Attempting to save general error (async) for link ID: {link_id}") # Debugging log
        database.insert_link_details(link_id, 'error', "No details extracted or scraping failed.")
        print(f"**Warning: Detail extraction failed or no details found (async)** for link ID: {link_id}, URL: {link_url}") # Modified message
    print(f"Details extracted and saved (async) for link ID: {link_id}, URL: {link_url}")


if __name__ == "__main__":
    create_database_and_tables() # Crea il database e le tabelle all'avvio dello script

    query = input("Enter your search query: ")
    num_results = int(input("Enter the number of results per engine: "))
    engines_input = input("Enter search engines (comma-separated, for main.py: Google, Bing, Yahoo, DuckDuckGo, Startpage, AOL, Dogpile, Ask, Mojeik, Brave, Torch; for serpapi_code.py: GOOGLE, BING, BAIDU, YANDEX, YAHOO, DUCKDUCKGO, NAVER, YELP; for unifiedscraper.py: google, bing, baidu, duckduckgo, yahoo, yandex, ask.  Enter 'all' for all engines from all scripts or specify engines): ").lower()
    features_input_str = input("Enter features to extract (comma-separated, e.g., testo,immagini,video,link,email,numeri_telefono,documenti): ") # Reduced feature list to supported ones for now
    features = [f.strip() for f in features_input_str.split(',')]
    mode = input("Enter mode for scraping details (sync/async): ").lower()


    if engines_input == 'all':
        engines_main = ["Google", "Bing", "Yahoo", "DuckDuckGo", "Startpage", "AOL", "Dogpile", "Ask", "Mojeik", "Brave", "Torch"]
        engines_serpapi_str = ["google", "bing", "yahoo", "duckduckgo", "naver", "yelp", "baidu", "yandex"] # Using string names for input processing, conversion to enum inside function
        engines_unified = ['google', 'bing', 'baidu', 'duckduckgo', 'yahoo', 'yandex', 'ask']
    else:
        engines_list = [engine.strip() for engine in engines_input.split(',')]
        engines_main = [e for e in engines_list if e in ["google", "bing", "yahoo", "duckduckgo", "startpage", "aol", "dogpile", "ask", "mojeik", "brave", "torch"]] # Keeping lowercase for main.py as function expects string names.
        engines_serpapi_str = [e for e in engines_list] # Let the function filter and validate for serpapi
        engines_unified = [e for e in engines_list if e in ['google', 'bing', 'baidu', 'duckduckgo', 'yahoo', 'yandex', 'ask']]

    all_results = {} # Dictionary to store results from all scripts
    saved_links_info = [] # To store link_id and link_url

    thread_main = threading.Thread(target=run_main_search, args=(query, num_results, all_results))
    thread_serpapi = threading.Thread(target=run_serpapi_search, args=(query, num_results, engines_serpapi_str, all_results))
    thread_unifiedscraper = threading.Thread(target=run_unifiedscraper_search, args=(query, num_results, engines_unified, all_results))

    start_time = time.time()

    thread_main.start()
    thread_serpapi.start()
    thread_unifiedscraper.start()

    thread_main.join()
    thread_serpapi.join()
    thread_unifiedscraper.join()

    end_time = time.time()
    print(f"\nTotal link extraction time: {end_time - start_time:.2f} seconds")
    print("All search tasks completed.")

    # Debugging: Print all_results before saving to db
    print("\n--- Debugging: all_results before saving ---")
    print(all_results)
    print("--- End Debugging all_results ---")


    # Salva i risultati nel database dopo che tutti i thread hanno finito e get link_ids
    if all_results.get('main'):
        saved_links_info.extend(save_results_to_db(all_results['main'], 'main.py', query))
    if all_results.get('serpapi'):
        saved_links_info.extend(save_results_to_db(all_results['serpapi'], 'serpapi_code.py', query))
    if all_results.get('unifiedscraper'):
        saved_links_info.extend(save_results_to_db(all_results['unifiedscraper'], 'unifiedscraper.py', query))

    print("\nSearch results saved to SQLite database.")

    # --- Debugging Prints ---
    print("\n--- Debugging: saved_links_info ---")
    print(saved_links_info)
    print("\n--- Debugging: Features to extract ---")
    print(features)
    print("--- End Debugging ---")

    # --- Start content extraction after saving links ---
    start_time_extraction = time.time()
    print("\nStarting content extraction for each link...")

    if mode == 'async': # Use asynchronous extraction
        async def run_async_extraction():
            extraction_tasks = [async_extract_and_save_details(link_info['link_id'], link_info['link_url'], features, mode) for link_info in saved_links_info]
            await asyncio.gather(*extraction_tasks)
        asyncio.run(run_async_extraction())

    else: # Use synchronous extraction
        for link_info in saved_links_info:
            extract_and_save_details(link_info['link_id'], link_info['link_url'], features, mode)

    end_time_extraction = time.time()
    print(f"\nContent extraction completed in {end_time_extraction - start_time_extraction:.2f} seconds.")
    print("\nIntegrated scraping process completed.");