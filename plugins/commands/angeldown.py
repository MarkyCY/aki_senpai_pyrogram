import asyncio
import os, time
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram import filters

import m3u8, requests, re, os

thumb = 'https://images.angelstudios.com/image/upload/b_rgb:000000,h_630,w_1200,c_fill,g_north/l_v1652712203:angel-studios:one_pixel,/fl_relative,w_1.0,h_1.0,c_scale,e_colorize,co_black,o_50/fl_layer_apply/l_v1632350973:angel-app:tuttle-twins:discovery_images:logo/fl_relative,w_0.35,c_scale/fl_layer_apply,g_north_west,y_0.05,x_0.05,fl_relative/l_v1663942060:angel-studios:logos:Angel-Studios-Logo-White/w_0.25,c_scale,fl_relative/fl_layer_apply,g_south_east,y_0.05,x_0.05,fl_relative/,h_630,w_1200/v1736813449/studio-app/catalog/1f941545-0480-4fc4-b406-b9851cd0bbc6.webp'

def load_playlist(source):
    if source.startswith('http'):
        return m3u8.load(source)
    else:
        return m3u8.loads(source)

def select_best_stream(playlist):
    best_stream = None
    max_bandwidth = 0
    for variant in playlist.playlists:
        bandwidth = variant.stream_info.bandwidth
        if bandwidth > max_bandwidth:
            max_bandwidth = bandwidth
            best_stream = variant
    return best_stream

def select_media(playlist, media_type, preferred_languages):
    medias = [m for m in playlist.media if m.type == media_type]
    for lang in preferred_languages:
        for m in medias:
            if m.language and m.language.lower().startswith(lang.lower()):
                return m
    return None

def build_ffmpeg_command(video_uri, audio_uri=None, subtitle_uri=None, output_file='output.mkv'):
    cmd = ['ffmpeg']
    cmd += ['-i', f'"{video_uri}"']
    if audio_uri:
        cmd += ['-i', f'"{audio_uri}"']
    if subtitle_uri:
        cmd += ['-i', f'"{subtitle_uri}"']
    cmd += ['-map', '0:v:0']
    if audio_uri:
        cmd += ['-map', '1:a:0']
    if subtitle_uri:
        cmd += ['-map', '2:s:0']
    cmd += ['-c', 'copy', '-y', output_file]
    return ' '.join(cmd)

async def get_duration(uri: str) -> float:
    """Usa ffprobe para obtener la duración total en segundos."""
    proc = await asyncio.create_subprocess_exec(
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        uri,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    out, _ = await proc.communicate()
    return float(out.strip())

async def download(app: Client, message, ffmpeg_cmd: list):
    chat_id = message.chat.id
    msg = await app.send_message(chat_id, "Descargando - 0%", reply_to_message_id=message.id)

    # Extraemos la URI de video del comando para calcular duración
    video_uri = ffmpeg_cmd[ffmpeg_cmd.index('-i') + 1].strip('"')
    total_secs = await get_duration(video_uri)

    # Arrancamos ffmpeg con pipe de progreso
    proc = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        '-progress', 'pipe:1', '-nostats',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )

    out_time_ms = 0
    last_update = time.time()
    pattern = re.compile(r'out_time_ms=(\d+)')

    # Leemos línea a línea la salida de progreso
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        line = line.decode().strip()
        m = pattern.match(line)
        if m:
            out_time_ms = int(m.group(1))
        # Cada 3 segundos, calculamos y actualizamos
        if time.time() - last_update >= 3:
            percent = min(100, int((out_time_ms / 1_000_000) / total_secs * 100))
            await app.edit_message_text(chat_id, msg.message_id, f"Descargando - {percent}%")
            last_update = time.time()

    await proc.wait()
    # Aseguramos 100% al final
    await app.edit_message_text(chat_id, msg.message_id, "Descarga completa - 100%")

    # Enviamos el archivo
    await app.send_document(chat_id, 'output.mkv', thumb=thumb,
                            caption="Aquí tienes el video descargado.",
                            reply_to_message_id=message.id)

@Client.on_message(filters.command('download'))
async def angel_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    args = message.text.split()

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")
    
    if len(args) > 1:
        link = args[1].strip()
    else:
        return await message.reply_text("Proporciona un enlace.")
    
    playlist = load_playlist(link)
    best_stream = select_best_stream(playlist)
    if not best_stream:
        return await message.reply_text("No se encontró un stream de video.")
    
    audio = select_media(playlist, 'AUDIO', ['es', 'en'])
    subtitles = select_media(playlist, 'SUBTITLES', ['es', 'en'])

    video_uri = best_stream.uri
    audio_uri = audio.uri if audio else None
    subtitle_uri = subtitles.uri if subtitles else None

    ffmpeg_cmd = build_ffmpeg_command(video_uri, audio_uri, subtitle_uri)

    await download(app, message, ffmpeg_cmd)

    # await app.send_document(chat_id, 'output.mkv', thumb=thumb, caption="Aquí tienes el video descargado.", reply_to_message_id=message.id)