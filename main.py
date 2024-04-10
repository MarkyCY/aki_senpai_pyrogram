from pyromod import Client

import asyncio
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
    #Iniciar Cliente
    await app.start()
    print('*Bot Online.')
    #Enviar un mensaje al Admin para avisar de que el Bot ya está Online
    await app.send_message(873919300, text='Aki está lista')

#Iniciar Proceso de la función main()
print("Bot Starting")
loop: asyncio.AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()
loop.create_task(main())
loop.run_forever()