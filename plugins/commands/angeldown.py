import os, time
from pyrogram import Client, enums
from pyrogram.types import Message
from pyrogram import filters

import m3u8, requests, re, os

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
    
    os.system(ffmpeg_cmd)
    await message.reply_text("Descarga completa.")
    
    await message.reply_document('output.mkv', caption="Aquí tienes el video descargado.")