from pyrogram import Client
from dotenv import load_dotenv
from pyrogram.types import BotCommand

# Carga los valores del archivo .env
load_dotenv()
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from plugins.commands.get_youtube import get_video_command

import asyncio
import pytz
import os

# Create a new Pyrogram client
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

user_api_id = os.getenv('USER_API_ID')
user_api_hash = os.getenv('USER_API_HASH')
#from logging import basicConfig, INFO
#basicConfig(format="*%(levelname)s %(message)s", level=INFO, force=True)


plugins = dict(root="plugins")
user_plugins = dict(root="user_plugins")
#
#bolita
app = Client('my_bot',api_id=api_id, api_hash=api_hash, bot_token=bot_token, plugins=plugins)
user_app = Client('user_bot', api_id=user_api_id, api_hash=user_api_hash, plugins=user_plugins)

#Función para iniciar el Bot
async def main():
    await app.start()
    await user_app.start()
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
scheduler.start()

#Iniciar Proceso de la función main()
print("Bot Starting")
loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()
loop.create_task(main())
loop.run_forever()