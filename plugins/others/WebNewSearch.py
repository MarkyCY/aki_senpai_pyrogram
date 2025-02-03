import os
import sys
import requests
import time
# import tldextract

from bs4 import BeautifulSoup
# from typing import List, Dict, Any
from urllib.parse import urljoin

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# from agents.Base_Agent import Base_Agent
# from providers.provider_factory import ProviderFactory

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


def web_new_search(query: str, premium):
        if premium is False:
            print("Solo usuarios premium pueden buscar en internet.")
            return "Notification: Este usuario no es Premium"
        #Numero de resultados a devolver
        num_results = 5
        
        # encoded_query = quote_plus(query)
        base_url = f'https://www.bing.com/news/search?q={query}&qft=interval%3d"9"&qft=sortbydate%3d"1" '
        
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',  # Indica que el idioma preferido es español
    }

        results = []
        page = 1
        while len(results) < num_results:
            url = f"{base_url}&count={min(30, num_results - len(results))}&first={(page-1)*30+1}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                news_cards = soup.find_all('div', class_='news-card')
                
                if not news_cards:
                    break  # No more results found
                
                for card in news_cards:
                    if len(results) >= num_results:
                        break
                    
                    title_elem = card.find('a', class_='title')
                    if title_elem:
                        title = title_elem.text.strip()
                        url = urljoin("https://www.bing.com", title_elem.get('href', ''))
                        
                        snippet_elem = card.find('div', class_='snippet')
                        description = snippet_elem.text.strip() if snippet_elem else ''
                        
                        source_elem = card.find('div', class_='source')
                        source = source_elem.text.strip() if source_elem else ''
                        
                        timestamp_elem = card.find('span', attrs={'aria-label': True})
                        timestamp = timestamp_elem['aria-label'] if timestamp_elem else ''
                        
                        # Extract the root domain from the URL
                        # ext = tldextract.extract(url)
                        # root_domain = f"{ext.domain}.{ext.suffix}"
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "description": description,
                            # "source": root_domain,  # Use the root domain as the source
                            "timestamp": timestamp
                        })
                
                page += 1
                time.sleep(1)  # Add a small delay between requests to avoid rate limiting
            except Exception as e:
                print(f"Error in _perform_news_search: {str(e)}")
                break

        print(f"News search completed successfully. Number of results: {len(results)}")

        if len(results) == 0:
            return "No hay noticias recientes, notifica al usuario que no hay noticias por ahora."
        
        return str(results)