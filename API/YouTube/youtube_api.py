from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import os
import pytz
import pickle
import asyncio

from datetime import datetime, timezone

async def authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Cargar credenciales desde un archivo pickle si existe
    if os.path.exists("API/YouTube/youtube_token.pickle"):
        with open("API/YouTube/youtube_token.pickle", "rb") as token:
            creds = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "API/YouTube/credentials.json", scopes=scopes
        )
        creds = await asyncio.get_event_loop().run_in_executor(None, flow.run_local_server, 0)

        # Guardar las credenciales en un archivo pickle para futuras ejecuciones
        with open("API/YouTube/youtube_token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

async def authenticate_calendar():
    # Definir los ámbitos de autorización necesarios para Google Calendar
    scopes = ["https://www.googleapis.com/auth/calendar"]

    # Cargar credenciales desde un archivo pickle si existe
    if os.path.exists("API/YouTube/calendar_token.pickle"):
        with open("API/YouTube/calendar_token.pickle", "rb") as token:
            creds = pickle.load(token)
    else:
        # Autenticar usando el archivo de credenciales de cliente
        flow = InstalledAppFlow.from_client_secrets_file(
            "API/YouTube/credentials.json", scopes=scopes
        )
        creds = await asyncio.get_event_loop().run_in_executor(None, flow.run_local_server)

        # Guardar las credenciales en un archivo pickle para futuras ejecuciones
        with open("API/YouTube/calendar_token.pickle", "wb") as token:
            pickle.dump(creds, token)

    # Construir el servicio de Google Calendar con las credenciales autenticadas
    return build("calendar", "v3", credentials=creds)

async def get_latest_videos(youtube, channel_id):
    videos_data = []
    
    # Realizar la solicitud para obtener los últimos videos del canal
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        type="video",
        maxResults=5
    )
    
    response = await asyncio.get_event_loop().run_in_executor(None, request.execute)

    # Imprimir los títulos de los últimos videos
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        thumbnails = item["snippet"]["thumbnails"]
        published_at = item["snippet"]["publishedAt"]

        # Obtener más detalles del video
        video_details = youtube.videos().list(
            part="contentDetails",
            id=video_id
        )
        content_details = await asyncio.get_event_loop().run_in_executor(None, video_details.execute)
        content_details = content_details["items"][0]["contentDetails"]

        # Crear un diccionario con los datos del video
        video_data = {
            "IDVideo": video_id,
            "Title": title,
            "Description": description,
            "Thumbnails": thumbnails,
            "Published At": published_at,
            "Content Details": content_details
        }

        # Agregar el diccionario a la lista
        videos_data.append(video_data)

    videos_data.reverse()

    return videos_data

async def list_calendars(service):
    # Llamar al método list() del servicio de Google Calendar para obtener la lista de calendarios
    calendar_list = await asyncio.get_event_loop().run_in_executor(None, service.calendarList().list().execute)

    # Iterar sobre todos los calendarios y imprimir sus detalles
    for calendar in calendar_list.get('items', []):
        print('Id del calendario:', calendar['id'])
        print('Nombre del calendario:', calendar['summary'])

def convert_date(fecha_iso):
    fecha_obj = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
    zona_cuba = pytz.timezone('America/Havana')
    fecha_cuba = fecha_obj.astimezone(zona_cuba)

    fecha_formateada = fecha_cuba.strftime('%d/%m/%y %I:%M %p')

    return fecha_formateada

async def list_events(service):
    now = datetime.now(tz=pytz.utc).isoformat()

    event_list = await asyncio.get_event_loop().run_in_executor(
        None,
        service.events().list(
            calendarId='5973845fcbada1fcf6c7fc498948df9091a15b37de9a014772641164c9e05db8@group.calendar.google.com',
            timeMin=now,  # Establecer la fecha mínima para eventos a partir de ahora
            maxResults=3,  # Limitar el número de eventos a 10
            singleEvents=True,  # Expandir eventos recurrentes en eventos individuales
            orderBy='startTime'  # Ordenar los eventos por su hora de inicio
        ).execute
    )
    data = "<b>Próximos programas:</b>\n"
    # Iterar sobre todos los calendarios y imprimir sus detalles
    for event in event_list.get('items', []):
        #print(event)
        data += f"""
<b>Título:</b> <code>{event['summary'].replace("OtkSen: ", "")}</code>
<b>Descripción:</b> {event['description']}
<b>Fecha:</b> <code>{convert_date(event['start']['dateTime'])}</code>
"""

    return data