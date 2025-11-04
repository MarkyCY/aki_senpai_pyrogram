from pyrogram import Client, filters, enums
from pyrogram.types import Message
import time

AppTimes = {}

def find_messages_by_bot(bot_type):
    return [
        message_id 
        for message_id, data in AppTimes.items()
        if data.get("bot") == bot_type
    ]

@Client.on_message(filters.photo & filters.group & filters.bot & filters.user(1964681186), group=1)
# @Client.on_message((filters.photo & filters.group), group=1)
async def husbando_is_out(app: Client, message: Message):
    # text = message.text or ""
    # args = text.split()
    # message_id = int(args[1])
    # print(f"Mensaje ID: {message_id}")
    
    print("husbando detectada en el grupo.")

    # Verificando que salga una husbando.
    text = message.caption.split(' ')
    if text[1] != "husbando":
        return

    # Usa el id del mensaje como clave
    message_id = getattr(message, "id", None)

    # Iniciamos el Contador
    start = AppTimes.get(message_id)

    if start is None:
        # Limpiamos los contadores anteriores por si acaso
        AppTimes.clear()

        # Iniciamos el contador nuevo
        AppTimes[message_id] = {
            "start_time": time.perf_counter(),
            "bot": "husbando",
            "users_time": {
                # Datos ficticios de ejemplo
                # 123456: 2000,
            }
        }
        print("Temporizador iniciado.")

# Seria cuando se detecta un /protecc
@Client.on_message(filters.command("protecc", prefixes=['/', '.']))
async def catch_capture(app: Client, message: Message = None):
    husbando_messages = find_messages_by_bot("husbando")

    if not husbando_messages:
        return
    
    data = AppTimes[husbando_messages[0]]
    AppTimes[husbando_messages[0]]["users_time"][message.from_user.id] = int((time.perf_counter() - data["start_time"]) * 1000)

    # Testing
    # AppTimes[husbando_messages[0]]["users_time"][123456] = int((time.perf_counter() - data["start_time"]) * 1000)


@Client.on_message(filters.group & filters.bot & filters.user(1964681186), group=2)
# @Client.on_message(filters.group, group=2)
async def husbando_captured(app: Client, message: Message = None):

    text = message.text.split(' ') 
    if text[1] != "OwO":
        return

    # ID del usuario que capturó el husbando
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else None
    name = message.reply_to_message.from_user.first_name if message.reply_to_message else "None"
    # user_id = 123456

    # Buscamos el id a traves del contador registrado
    husbando_messages = find_messages_by_bot("husbando")

    if not husbando_messages:
        return

    # Obtenemos los datos del mensaje husbando
    data = AppTimes[husbando_messages[0]] if husbando_messages else None

    if data and user_id:
        users = data.get("users_time", {})
        tiempo_ms = users[user_id] if user_id in users else None
        if tiempo_ms:
            await message.reply_text(f"El usuario <a href='tg://user?id={user_id}'>{name}</a> capturó el husbando en {tiempo_ms} ms.", parse_mode=enums.ParseMode.HTML)
            print(f"Mostrando todos los tiempos registrados:\n{users}")
            print(f"Tiempo total pasado desde el inicio: {int((time.perf_counter() - data['start_time']) * 1000)} ms")
            AppTimes.clear()
    """
    else:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        AppTimes.pop(message_id, None)
        await message.reply_text(f"Temporizador detenido. Duración: {elapsed_ms} ms")

    """

@Client.on_message(filters.group & filters.bot & filters.user(1964681186), group=3)
# @Client.on_message(filters.group, group=3)
async def husbando_dead(app: Client, message: Message = None):
    text = message.text.split(' ')
    if text[0] != "rip,":
        return
    
    print("El husbando ha muerto. Limpiando los contadores.")
    AppTimes.clear()
    print("Mostrando a versi quedan contadores.")
    print(AppTimes)