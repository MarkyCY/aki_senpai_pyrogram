import requests
from bs4 import BeautifulSoup

def get_mh_rooms(server_code: str, show_all: bool = False) -> str:
    """
    Obtiene las salas de Monster Hunter de un servidor concreto.

    :param server_code: 'FU' para MHFU, 'P3' para MHP3rd, 'F1' para F1.
    :param show_all: False (por defecto) → solo salas vacías; True → todas las salas + nombres.
    :return: mensaje formateado con nombre del juego y lista de salas.
    """
    # Mapeo de código → texto tal como aparece en la etiqueta GameName
    server_map = {
        'FU': 'MHFU',
        'P3': 'MHP3rd',
        'F1': 'F1'
    }
    server_code = server_code.upper()
    if server_code not in server_map:
        raise ValueError(f"Código de servidor inválido. Usa uno de: {', '.join(server_map)}")

    url = "https://hunstermonter.net/new_gh_getter.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'es-ES,es;q=0.9',
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, 'html.parser')
    # Buscamos el bloque del juego elegido
    games = soup.find_all('div', class_='EntireGame')
    target = None
    for g in games:
        name = g.find('div', class_='GameName').get_text(strip=True)
        if name.startswith(server_map[server_code]):
            target = g
            break

    if not target:
        return f"⚠️ No se encontró información para el servidor «{server_map[server_code]}»."

    title = target.find('div', class_='GameName').get_text(strip=True)
    lines = [f"🎮 **{title}**"]

    # Todas las salas (vacías y ocupadas)
    room_divs = target.find_all('div', class_=['FullGH', 'emptyGHClass'])
    for room in room_divs:
        is_empty = 'emptyGHClass' in room.get('class', [])
        # Si no pedimos todas y la sala está ocupada, la saltamos
        if not show_all and not is_empty:
            continue

        wrapper = room.find('div', class_='GHWrapper')
        b_tags = wrapper.find_all('b')
        code = b_tags[0].get_text(strip=True)     # ej. "GH01A"
        pop  = b_tags[1].get_text(strip=True)     # ej. "[0/4]"

        # Línea base
        prefix = "✅" if is_empty else "❌"
        line = f"{prefix} {code} {pop}"

        # Si pedimos todas, añadimos lista de cazadores
        if show_all:
            hunters = [h.get_text(strip=True).rstrip(',') 
                       for h in wrapper.find_all('div', class_='Hunter')]
            if hunters:
                line += ": " + ", ".join(hunters)

        lines.append(line)

    # Si no hay salas (por ejemplo, servidor vacío), damos aviso
    if len(lines) == 1:
        lines.append("— No hay salas para mostrar.")

    return "\n".join(lines)



if __name__ == "__main__":
    # import sys
    # if len(sys.argv) != 2:
    #     print("Usage: WebGetContents_Tool.py <URL>")
    #     sys.exit(1)

    # url = sys.argv[1]
    content = get_mh_rooms( server_code='P3', show_all=True )
    if content:
        print(content)  # Print first 500 characters
    else:
        print("Failed to retrieve content")