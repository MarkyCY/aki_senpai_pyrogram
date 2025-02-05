import os
import sys
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin



sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

def web_search(query: str, premium):
    print("Buscando en internet la consulta: ", query)
    if premium is False:
        print("Solo usuarios premium pueden buscar en internet.")
        return "Notification: Este usuario no es Premium"
    
    num_results = 5
    base_url = f'https://www.bing.com/search?q={query}&qft=interval%3d"9"&qft=sortbydate%3d"1" '
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'es-ES,es;q=0.9',
    }

    results = []
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.select('#b_results > li.b_algo')
        
        for result in search_results[:num_results]:
            entry = {
                'titulo': None,
                'url': None,
                'descripcion': None,
                'dominio': None,
                'enlaces_profundos': [],
                'imagen': None
            }
            
            # Extraer título y URL
            title_tag = result.select_one('h2 a')
            if title_tag:
                entry['titulo'] = title_tag.get_text(strip=True)
                entry['url'] = urljoin(base_url, title_tag['href'])
            
            # Extraer descripción
            description_tag = result.select_one('.b_caption p')
            if description_tag:
                entry['descripcion'] = description_tag.get_text(strip=True)
            
            # Extraer dominio
            domain_tag = result.select_one('cite, .tptt')
            if domain_tag:
                entry['dominio'] = domain_tag.get_text(strip=True)
            
            # Extraer imagen
            img_tag = result.select_one('.tpic img')
            if img_tag:
                entry['imagen'] = img_tag.get('src', None)
            
            # Extraer enlaces profundos
            deep_links = result.select('.b_deep a')
            for link in deep_links:
                deep_entry = {
                    'titulo': link.get_text(strip=True),
                    'url': urljoin(base_url, link['href']),
                    'resumen': None
                }
                
                # Extraer resumen del párrafo siguiente
                next_p = link.find_next('p')
                if next_p:
                    deep_entry['resumen'] = next_p.get_text(strip=True)
                
                entry['enlaces_profundos'].append(deep_entry)
            
            results.append(entry)
        
        time.sleep(1)  # Espera entre solicitudes
        
    except Exception as e:
        print(f"Error en la búsqueda: {str(e)}")
        return f"Error en la búsqueda: {str(e)}"

    print(f"Búsqueda completada. Resultados obtenidos: {len(results)}")
    
    if not results:
        return "No se encontraron resultados de búsqueda."
    
    return str(results)

if __name__ == "__main__":
    # import sys
    # if len(sys.argv) != 2:
    #     print("Usage: WebSearch.py <query>")
    #     sys.exit(1)

    # query = sys.argv[1]
    resultados = web_search("Rudeus greyrat", premium=True)
    print(resultados)