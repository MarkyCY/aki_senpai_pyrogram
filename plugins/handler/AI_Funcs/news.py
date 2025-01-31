import json
import requests
import re
import xml.etree.ElementTree as ET

def buscar_noticias():
    response = requests.get("https://www.animenewsnetwork.com/this-week-in-anime/atom.xml?ann-edition=w")
    xml_data = response.text
    
    root = ET.fromstring(xml_data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    entries = []
    # Obtén todos los elementos 'atom:entry'
    all_entries = root.findall('atom:entry', ns)
    # Itera desde el final hacia el principio, tomando los últimos 10 elementos
    for entry in all_entries[:5]:

        title = entry.find('atom:title', ns).text
        title_clean = re.sub(r"This Week in Anime - ", "", title)

        link = entry.find('atom:link', ns).attrib['href']
        summary = entry.find('atom:summary', ns).text

        published = entry.find('atom:published', ns).text
        updated = entry.find('atom:updated', ns).text
        categories = entry.findall('atom:category', ns) 

        entries.append({
            'title': title_clean.replace('"', "").replace("'", ""),
            'link': link,
            'published': published,
            'updated': updated,
            'summary': summary.replace('"', "").replace("'", ""),
        })

    return json.dumps(entries, ensure_ascii=False).replace('"', "'")