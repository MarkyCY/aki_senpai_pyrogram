from pyrogram import Client
from dotenv import load_dotenv
from pyrogram.types import BotCommand

from user_plugins.funcs.group_stats import stats_show

# Carga los valores del archivo .env
load_dotenv()
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from plugins.commands.get_youtube import get_video_command
from user_plugins.core.user_bot import pytgcalls, user_app
from plugins.others.ram_verif import verif_ram

import asyncio
import pytz
import os

# Create a new Pyrogram client
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

user_api_id = os.getenv('USER_API_ID')
user_api_hash = os.getenv('USER_API_HASH')
from logging import basicConfig, INFO
basicConfig(format="*%(levelname)s %(message)s", level=INFO, force=True)


plugins = dict(root="plugins")
user_plugins = dict(root="user_plugins")
#my_bot
#bolita
app = Client('my_bot',api_id=api_id, api_hash=api_hash, bot_token=bot_token, plugins=plugins)

#Función para iniciar el Bot
async def main():
    await app.start()
    await user_app.start()
    await pytgcalls.start()
    print('*Bots Online.')
    await app.send_message(873919300, text='Aki está lista')
    await user_app.send_message(873919300, text='UserBot está listo')
    await app.set_bot_commands([
        BotCommand("anime", "Buscar información sobre un anime"),
        BotCommand("manga", "Buscar información sobre un manga"),
        BotCommand("game", "Buscar información sobre videojuegos"),
        BotCommand("character", "Buscar información sobre un personaje"),
        BotCommand("afk", "Modo afk"),
        BotCommand("steal", "Obtener Stickers"),
        BotCommand("del_sticker", "Eliminar Sticker del Pack"),
        BotCommand("set_bio", "Poner descripción"),
        BotCommand("info", "Ver la información de un usuario"),
        BotCommand("tr", "Traducir elementos"),
        BotCommand("add_anime", "Agregar anime a la base de datos"),
        BotCommand("del_anime", "Eliminar anime de la base de datos"),
        BotCommand("staff", "Listado del Staff del grupo"),
        BotCommand("programas", "Próximos programas en emisión"),
        BotCommand("concursos", "Ver los concursos del grupo"),
        BotCommand("create", "Crear un concurso"),
        BotCommand("ban", "Banear a un usuario"),
        BotCommand("unban", "Desbanear a un usuario"),
        BotCommand("mute", "Silenciar a un usuario"),
        BotCommand("unmute", "Desilenciar a un usuario"),
        BotCommand("warn", "Advertir a un usuario"),
    ])

    #Crear los horarios
    scheduler = AsyncIOScheduler()
    tz = pytz.timezone('Cuba')
    scheduler.add_job(get_video_command, CronTrigger(minute='*/30', timezone=tz), args=(app,))
    scheduler.add_job(verif_ram, CronTrigger(hour='*/2', timezone=tz), args=(90,))
    scheduler.add_job(stats_show, CronTrigger(hour='23', minute='55', timezone=tz), args=(user_app,))
    scheduler.start()

#Iniciar Proceso de la función main()
print("Bot Starting")
loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()
loop.create_task(main())
loop.run_forever()