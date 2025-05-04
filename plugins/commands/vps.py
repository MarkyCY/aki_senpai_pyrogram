from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import psutil

@Client.on_message(filters.command('vps'))
async def vps_info_command(app: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_id != 873919300:
        return await message.reply_text("No tienes permisos para usar este comando.")
    
    # Obtener información de la RAM
    mem = psutil.virtual_memory()
    uso_ram = mem.percent
    
    # Obtener información del CPU
    uso_cpu_total = psutil.cpu_percent(interval=1)  # Uso total del CPU
    uso_cpu_por_nucleo = psutil.cpu_percent(interval=1, percpu=True)  # Uso por núcleo
    
    # Formatear el mensaje
    mensaje = (
        f"**Uso de RAM:** {uso_ram:.2f}%\n"
        f"**Uso total del CPU:** {uso_cpu_total:.2f}%\n"
        "**Uso por núcleo:**\n"
    )
    
    # Agregar el uso de cada núcleo al mensaje
    for i, uso in enumerate(uso_cpu_por_nucleo, start=1):
        mensaje += f"  - Núcleo {i}: {uso:.2f}%\n"
    
    await message.reply_text(mensaje)