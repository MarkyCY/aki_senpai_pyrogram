from pyrogram import Client
from pyrogram.types import Message
from pyrogram import filters
from pyrogram import enums


@Client.on_message(filters.command('rules'))
async def rules_command(app: Client, message: Message):

    if message.chat.id == -1002094390065:
        return

    text= """<b>Normas del Grupo </b>

1. Mantener en todo momento un comportamiento respetuoso con el resto de usuarios del grupo.

2. No se permite contenido hentai o ecchi.

3. No se permite ningún contenido contrarrevolucionario ni de política 

4. Pedir permiso para escribir al pv a la persona en cuestión. Esto no aplica para los admins, no hay que pedirles permiso para escribirles al pv.

5. El acercamiento descortés y vulgar con fines románticos y/o reproductivos (Tiburoneo) sera penalizado. Si quieres decirle a alguien que te gusta, no le cantes una canción de reggaetón. Promovamos relaciones sanas y saludables. 

6. No se permiten palabras obscenas, ni siquiera censuradas.

7. No hacer promoción de grupos, de compra y venta o cualquier tipo de enlace que no este relacionado con la temática del grupo.

8. Prohibidos los spoilers sobre los animes en transmisión y sobre cualquier contenido proveniente de la obra original (manga, novela ligera, etc) de cualquier anime en cualquier tópico que no sea el designado para esto. 
Excepción para animes cancelados o con 0 posibilidades de continuación en formato anime. 

9. En caso de no haber un regla escrita, quedará a discreción de los administradores mantener el orden dentro del grupo.

NOTA: Los admins no debemos explicaciones.
"""
    await message.reply_text(text=text, parse_mode=enums.ParseMode.HTML)