import os
import re
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters
import m3u8
import requests
from PIL import Image
from io import BytesIO


def load_playlist(source: str) -> m3u8.M3U8:
    if source.startswith('http'):
        return m3u8.load(source)
    else:
        return m3u8.loads(source)


def select_best_stream(playlist: m3u8.M3U8) -> m3u8.Playlist:
    best = None
    max_bw = 0
    for variant in playlist.playlists:
        bw = variant.stream_info.bandwidth
        if bw > max_bw:
            max_bw = bw
            best = variant
            #print(f"Seleccionado: {bw} bps, Resolución: {width}x{height}")
    return best


def select_media(playlist: m3u8.M3U8, media_type: str, langs: list[str]) -> m3u8.Media:
    medias = [m for m in playlist.media if m.type == media_type]
    for lang in langs:
        for m in medias:
            if m.language and m.language.lower().startswith(lang.lower()):
                return m
    return None


def build_ffmpeg_command(video_uri: str, audio_uri: str | None = None,
                        subtitle_uri: str | None = None,
                        output_file: str = 'output.mp4') -> list[str]:
    cmd = ['ffmpeg', '-y']
    cmd += ['-i', video_uri]
    if audio_uri:
        cmd += ['-i', audio_uri]
    if subtitle_uri:
        cmd += ['-i', subtitle_uri]
    cmd += ['-map', '0:v:0']
    if audio_uri:
        cmd += ['-map', '1:a:0']
    if subtitle_uri:
        cmd += ['-map', '2:s:0']
    cmd += ['-c', 'copy', output_file]
    return cmd

async def get_duration(uri: str) -> float:
    """Obtiene la duración del video en segundos usando ffprobe."""
    proc = await asyncio.create_subprocess_exec(
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', uri,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    out, _ = await proc.communicate()
    return float(out.strip()) if out else 0.0

async def download(app: Client, message: Message, cmd: list[str]):
    chat_id = message.chat.id
    msg = await app.send_message(chat_id, "Descargando - 0%", reply_parameters=ReplyParameters(message_id=message.id))

    # Obtener duración total
    video_uri = cmd[cmd.index('-i') + 1]
    total_secs = await get_duration(video_uri)

    # Lanzar ffmpeg con progreso por pipe
    proc = await asyncio.create_subprocess_exec(
        *cmd, '-progress', 'pipe:1', '-nostats',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )

    pattern = re.compile(r'out_time_ms=(\d+)')
    out_time_ms = 0
    last_update = time.time()

    # Leer progreso
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        text = line.decode().strip()
        m = pattern.match(text)
        if m:
            out_time_ms = int(m.group(1))
        if time.time() - last_update >= 3:
            percent = min(100, int((out_time_ms / 1_000_000) / total_secs * 100)) if total_secs > 0 else 0
            bar_length = 20  # longitud de la barra
            filled_length = int(bar_length * percent // 100)
            bar = '█' * filled_length + '─' * (bar_length - filled_length)

            await app.edit_message_text(chat_id, msg.id, f"Descargando\n{percent}% [{bar}]")
            last_update = time.time()

    await proc.wait()
    # Actualizar a 100% al finalizar
    await app.edit_message_text(chat_id, msg.id, "Descarga completa - 100%")

    return True

@Client.on_message(filters.command('download'))
async def angel_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")

    args = message.text.split(maxsplit=3)
    if len(args) < 2:
        return await message.reply_text("Proporciona un enlace.")

    link = args[1].strip()
    playlist = load_playlist(link)
    best = select_best_stream(playlist)

    if not best:
        return await message.reply_text("No se encontró un stream de video.")
    
    # Obtener resolución
    stream_info = best.stream_info
    width = stream_info.resolution[0] if stream_info.resolution else None
    height = stream_info.resolution[1] if stream_info.resolution else None
    print(f"Resolución seleccionada: {width}x{height}")

    # audio = select_media(playlist, 'AUDIO', ['es', 'en'])
    audio = select_media(playlist, 'AUDIO', ['es'])
    subtitles = select_media(playlist, 'SUBTITLES', ['es', 'en'])

    video_uri = best.uri
    audio_uri = audio.uri if audio else None
    subtitle_uri = subtitles.uri if subtitles else None

    ffmpeg_cmd = build_ffmpeg_command(video_uri, audio_uri, None)
    downld = await download(app, message, ffmpeg_cmd)

    # Miniatura para el video
    thumbnail = 'https://images.angelstudios.com/image/upload/b_rgb:000000,h_630,w_1200,c_fill,g_north/l_v1652712203:angel-studios:one_pixel,/fl_relative,w_1.0,h_1.0,c_scale,e_colorize,co_black,o_50/fl_layer_apply/l_v1632350973:angel-app:tuttle-twins:discovery_images:logo/fl_relative,w_0.35,c_scale/fl_layer_apply,g_north_west,y_0.05,x_0.05,fl_relative/l_v1663942060:angel-studios:logos:Angel-Studios-Logo-White/w_0.25,c_scale,fl_relative/fl_layer_apply,g_south_east,y_0.05,x_0.05,fl_relative/,h_630,w_1200/v1736813449/studio-app/catalog/1f941545-0480-4fc4-b406-b9851cd0bbc6.webp'

    # Descargar el thumbnail
    response = requests.get(thumbnail)
    
    # Open image and resize keeping aspect ratio
    img = Image.open(BytesIO(response.content))
    # Calculate new size maintaining aspect ratio
    ratio = min(320/img.width, 320/img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Save as JPEG with quality adjustment to keep under 200KB
    quality = 85
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    thumb = output.getvalue()
    
    # If still over 200KB, reduce quality until it fits
    while len(thumb) > 200*1024:
        quality = int(quality * 0.9)
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        thumb = output.getvalue()


    if downld:
        # Enviar el archivo resultante
        try:
            await app.send_video(chat_id, 'output.mp4', thumb=thumb,
                                    caption="Aquí tienes el video descargado.",
                                    width=int(width) if width else 0, height=int(height) if height else 0,
                                    reply_parameters=ReplyParameters(message_id=message.id))
        except Exception as e:
            print(e)
            await app.send_video(chat_id, 'output.mp4',
                                    caption="Aquí tienes el video descargado.",
                                    width=int(width) if width else 0, height=int(height) if height else 0,
                                    reply_parameters=ReplyParameters(message_id=message.id))


def main():
    source = input("Introduce la URL o el texto del archivo M3U8: ").strip()
    playlist = load_playlist(source)
    best_stream = select_best_stream(playlist)
    print(best_stream)
    if not best_stream:
        print("No se encontró un stream de video.")
        return

    # Obtener resolución
    stream_info = best_stream.stream_info
    width = stream_info.resolution[0] if stream_info.resolution else None
    height = stream_info.resolution[1] if stream_info.resolution else None
    print(f"Resolución seleccionada: {width}x{height}")

    audio = select_media(playlist, 'AUDIO', ['es', 'en'])
    subtitles = select_media(playlist, 'SUBTITLES', ['es', 'en'])

    video_uri = best_stream.uri
    audio_uri = audio.uri if audio else None
    subtitle_uri = subtitles.uri if subtitles else None

    ffmpeg_cmd = build_ffmpeg_command(video_uri, audio_uri, subtitle_uri)

if __name__ == '__main__':
    main()
