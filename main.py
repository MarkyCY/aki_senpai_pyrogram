from pyrogram import Client
from dotenv import load_dotenv

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

print("API_ID:", api_id)
print("API_HASH:", api_hash)
print("BOT_TOKEN:", bot_token)

from logging import basicConfig, INFO
basicConfig(format="*%(levelname)s %(message)s", level=INFO, force=True)


plugins = dict(root="plugins")
#my_bot
#AkiraS
app = Client('my_bot',api_id=api_id, api_hash=api_hash, bot_token=bot_token, plugins=plugins)

#Función para iniciar el Bot
async def main():
    await app.start()
    print('*Bot Online.')
    await app.send_message(873919300, text='Aki está lista')

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