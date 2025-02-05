# --- START OF FILE web_viewer.py ---
from flask import Flask, render_template
import sqlite3

DATABASE_NAME = 'search_results.db'

app = Flask(__name__)

def get_search_results_from_db():
    """
    Recupera i risultati della ricerca e i dettagli dal database SQLite e li organizza.
    """
    conn = None
    results_by_query_script_engine = {}
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        print("Database connection successful.")  # Debug print

        cursor = conn.cursor()

        # Query per recuperare link e dettagli correlati in un'unica query (più efficiente)
        cursor.execute('''
            SELECT
                l.query,
                l.search_engine,
                l.link_url,
                ld.detail_type,
                ld.detail_value
            FROM links l
            LEFT JOIN link_details ld ON l.id = ld.link_id
            ORDER BY l.query, l.search_engine, l.link_url, ld.detail_type
        ''')
        rows = cursor.fetchall()
        print(f"Number of rows fetched: {len(rows)}")  # Debug print

        for row in rows:
            query, search_engine, link_url, detail_type, detail_value = row

            if query not in results_by_query_script_engine:
                results_by_query_script_engine[query] = {}
            if search_engine not in results_by_query_script_engine[query]:
                results_by_query_script_engine[query][search_engine] = []

            link_entry = None
            for entry in results_by_query_script_engine[query][search_engine]:
                if entry['url'] == link_url:
                    link_entry = entry
                    break
            if link_entry is None:
                link_entry = {'url': link_url, 'details': {}}
                results_by_query_script_engine[query][search_engine].append(link_entry)

            if detail_type:
                link_entry['details'][detail_type] = detail_value

        print("Data processing complete.")  # Debug print
        return results_by_query_script_engine

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

@app.route('/')
def display_search_results():
    results = get_search_results_from_db()
    if results:
        print("Rendering template with results.")  # Debug print
        return render_template('results.html', results=results)
    else:
        print("No results to display or database error.")  # Debug print
        return "Errore nel recupero dei risultati dal database."

if __name__ == '__main__':
    print("Starting Flask app in debug mode.")  # Debug print
    app.run(debug=True)
# --- END OF FILE web_viewer.py ---