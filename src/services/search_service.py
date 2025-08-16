import requests
import os

# Hinweis: API-Schlüssel sollten sicher verwaltet werden, z.B. über Umgebungsvariablen
# Beispiel für die Verwendung von Umgebungsvariablen:
# YAHOO_API_KEY = os.environ.get('YAHOO_API_KEY')
# BING_API_KEY = os.environ.get('BING_API_KEY')

# Platzhalter für API-Endpunkte und Schlüssel
YAHOO_SEARCH_URL = "https://api.search.yahoo.com/search" # Dies ist ein Platzhalter, der tatsächliche Endpunkt kann abweichen
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search" # Beispiel Bing Search API v7

def search_yahoo(query):
    """
    Führt eine Suche über die Yahoo Search API durch.

    Args:
        query (str): Der Suchbegriff.

    Returns:
        dict: Die JSON-Antwort der API oder None im Fehlerfall.
    """
    # Bitte ersetzen Sie 'YOUR_YAHOO_API_KEY' durch Ihren tatsächlichen API-Schlüssel
    # und verwalten Sie ihn sicher (z.B. über Umgebungsvariablen).
    api_key = "YOUR_YAHOO_API_KEY" # Platzhalter

    headers = {
        # Header können je nach Yahoo Search API Spezifikation erforderlich sein
        # 'Authorization': f'Bearer {api_key}',
        # 'Accept': 'application/json'
    }

    params = {
        'q': query, # Der Suchbegriff
        # Weitere Parameter je nach API-Dokumentation (z.B. Region, Anzahl der Ergebnisse)
    }

    try:
        response = requests.get(YAHOO_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status() # Wirft eine HTTPError für schlechte Antworten (4xx oder 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei Yahoo Suche: {e}")
        return None

def search_bing(query):
    """
    Führt eine Suche über die Bing Search API durch.

    Args:
        query (str): Der Suchbegriff.

    Returns:
        dict: Die JSON-Antwort der API oder None im Fehlerfall.
    """
    # Bitte ersetzen Sie 'YOUR_BING_API_KEY' durch Ihren tatsächlichen API-Schlüssel
    # und verwalten Sie ihn sicher (z.B. über Umgebungsvariablen).
    # Die Bing Search API verwendet oft einen Ocp-Apim-Subscription-Key Header
    api_key = "YOUR_BING_API_KEY" # Platzhalter

    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Accept': 'application/json'
    }

    params = {
        'q': query, # Der Suchbegriff
        'mkt': 'de-DE' # Beispiel: Sprache und Region (Deutsch, Deutschland)
        # Weitere Parameter je nach API-Dokumentation
    }

    try:
        response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
        response.raise_for_status() # Wirft eine HTTPError für schlechte Antworten (4xx oder 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei Bing Suche: {e}")
        return None

if __name__ == "__main__":
    # Beispielaufrufe (dieser Code wird nur ausgeführt, wenn das Skript direkt ausgeführt wird)
    test_query = "KI Entwicklung"

    print(f"Suche auf Yahoo nach: {test_query}")
    # yahoo_results = search_yahoo(test_query)
    # if yahoo_results:
    #     print("Yahoo Ergebnisse (gekürzt):", yahoo_results.get('web', {}).get('results')[:3]) # Beispielhafte Anzeige
    # else:
    #     print("Keine Yahoo Ergebnisse erhalten.")

    print("-" * 20)

    print(f"Suche auf Bing nach: {test_query}")
    # bing_results = search_bing(test_query)
    # if bing_results:
    #     print("Bing Ergebnisse (gekürzt):", bing_results.get('webPages', {}).get('value')[:3]) # Beispielhafte Anzeige
    # else:
    #     print("Keine Bing Ergebnisse erhalten.")

    print("\nHinweis: Ersetzen Sie die Platzhalter-API-Schlüssel und -Endpunkte.")