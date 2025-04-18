from pyrogram import Client
from pyrogram.types import Message, ReactionTypeEmoji, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from pyrogram import filters
from datetime import datetime, timedelta

import random
from database.mongodb import get_db

# Definimos una lista de mensajes de bienvenida por defecto
default_welcome_messages = [
    "¡Bienvenido! En Otaku Senpai siempre hay espacio para más locos del anime y el manga.",
    "¡Hola, nuevo! Prepárate para vivir emociones fuertes y descubrir nuevas series que te van a encantar.",
    "¡Bienvenido al paraíso otaku! Aquí encontrarás todo lo que necesitas para alimentar tu obsesión por el anime y el manga.",
    "¡Hola, nuevo miembro! En Otaku Senpai somos una gran familia de amantes del anime y el manga. ¡Únete a nosotros!",
    "¡Bienvenido a nuestra comunidad otaku! Prepárate para conocer a gente con tus mismos gustos y disfrutar de la cultura japonesa.",
    "¡Hola, nuevo! Aquí en Otaku Senpai no hay límites para nuestra pasión por el anime y el manga. ¡Únete a la locura!",
    "¡Bienvenido al mundo otaku! En Otaku Senpai encontrarás un lugar donde ser tú mismo y disfrutar de lo que más te gusta.",
    "¡Hola, nuevo miembro! Prepárate para descubrir nuevas series, hacer amigos y compartir tus opiniones sobre el anime y el manga.",
    "¡Bienvenido a Otaku Senpai, la comunidad más otaku de todas! Aquí encontrarás todo lo que necesitas para saciar tu sed de anime y manga.",
    "¡Hola, nuevo! En Otaku Senpai somos una familia de otakus apasionados. Prepárate para vivir momentos épicos y hacer amigos para toda la vida."
]

# Definimos una lista de mensajes de bienvenida los lunes
monday_welcome_messages = [
    "Bienvenido, nuevo miembro. Prepárate para pasar horas y horas pegado a la pantalla.",
    "¿Qué tal, nuevo? Espero que estés listo para sumergirte en el mundo otaku con nosotros.",
    "¡Hola, bienvenido a Otaku Senpai! Si necesitas recomendaciones de anime, ¡no dudes en preguntar!",
    "Bienvenido, nuevo. Aquí encontrarás gente con la que compartir tu amor por el anime y el manga. Oh alguien creó un tópico de videojuegos. Espera ¡¿Qué?!",
    "¡Hola, nuevo! ¿Estás preparado para discutir teorías de anime hasta altas horas de la noche?",
    "Bienvenido a Otaku Senpai, donde la vida real se queda atrás y la fantasía toma el control.",
    "¡Hola, nuevo miembro! Esperamos que disfrutes de tu estancia en nuestro pequeño paraíso otaku.",
    "Bienvenido, nuevo. Aquí encontrarás un hogar para tus obsesiones otaku.",
    "¡Hola, bienvenido al club de los otakus! Prepárate para compartir tus experiencias y opiniones con otros fans.",
    "Bienvenido, nuevo miembro. No te preocupes, aquí todos estamos un poco locos por el anime y el manga."
]

# Definimos una lista de mensajes de bienvenida para el fin de semana
weekend_welcome_messages = [
    "¡Bienvenido! ¡Qué bueno tenerte aquí wiiiiijaaaaa!",
    "¡Hola! ¡Bienvenido al grupo! ¡Es un buen día para unirse a nuestra comunidad!",
    "¡Yay! ¡Otro miembro se une a la diversión del fin de semana! Bienvenido al grupo.",
    "¡Buenas noticias! ¡Otro miembro acaba de unirse a nuestro grupo increíble! Bienvenido.",
    "¡Bienvenido! ¡Es genial tenerte aquí con nosotros en este fin de semana lleno de diversión!",
    "¡Otro miembro se une al grupo! ¡Bienvenido a nuestra familia del fin de semana!",
    "¡Hola! ¡Bienvenido al grupo! ¡Espero que estés disfrutando de este fin de semana tanto como nosotros!",
    "¡Bienvenido! ¡Este es un lugar genial para pasar tu fin de semana!",
    "¡Hola! ¡Bienvenido al grupo! ¡Espero que disfrutes de tu tiempo aquí durante este fin de semana!",
    "¡Bienvenido! ¡Esperamos que te unas a nosotros para disfrutar juntos de este fin de semana!"
]

monday_welcome_messages_christmas = [
    "¡Bienvenido! ¡Casi Es Navidad!",
    "¡Hola! ¡Bienvenido al grupo! ¡Es un buen día para unirse a nuestra comunidad! ¡Casi Es Navidad!",
    "¡Yay! ¡Otro miembro se une a la diversión del fin de semana! Bienvenido al grupo. ¡Casi Es Navidad siiiii!",
    "¡Buenas noticias! ¡Otro miembro acaba de unirse a nuestro grupo increíble! Bienvenido. ¡Casi estamos en Navidad!",
    "¡Bienvenido! ¡Es genial tenerte aquí con nosotros en este fin de semana lleno de diversión! ¡Mira mi gorrito!",
    "¡Otro miembro se une al grupo! ¡Bienvenido a nuestra familia del fin de semana! ¡Que gorrito mas lindo tengo!",
    "¡Hola! ¡Bienvenido al grupo! ¡Espero que estés disfrutando de este fin de semana tanto como nosotros! ¡Casi Es Navidad!",
    "¡Bienvenido! ¡Este es un lugar genial para pasar tu fin de semana! ¡Navidaaad, navidaaaaad!",
    "¡Hola! ¡Bienvenido al grupo! ¡Espero que disfrutes de tu tiempo aquí durante este fin de semana! ¡Casi Es Navidad!",
    "¡Bienvenido! ¡Esperamos que te unas a nosotros para disfrutar juntos de este fin de semana! ¡Ya quiero mi cerdo de 31 de diciembre!"
]

# Constantes
DECEMBER = 12
MONDAY = 0
WEEKEND_START = 5


permissions = ChatPermissions(
can_send_messages = True,
can_send_audios = True,
can_send_documents = False,
can_send_photos = True,
can_send_videos = False,
can_send_video_notes = False,
can_send_voice_notes = False,
can_send_polls = False,
can_send_other_messages = True, #Stickers, Juegos Etc.
can_add_web_page_previews = False,
can_change_info = False,
can_invite_users = True,
can_pin_messages = False,
can_manage_topics = False,
can_send_media_messages = True,
)

@Client.on_message(filters.new_chat_members)
async def send_welcome_event(app: Client, message: Message):
    
    if message.chat.id != -1001485529816:
        return
    
    # Conectar a la base de datos
    db = await get_db()
    users = db.users
    # Obtenemos el nombre de usuario de la persona que se unio al grupo
    chat_id = message.chat.id
    #message_id = message.id
    new_user_id = message.new_chat_members[0].id

    current_date = datetime.today()
    current_month = current_date.month
    current_weekday = current_date.weekday()

    if current_month == DECEMBER and current_weekday == MONDAY:
        welcome_message = random.choice(monday_welcome_messages_christmas)
    elif current_weekday == MONDAY:
        welcome_message = random.choice(monday_welcome_messages)
    elif current_weekday >= WEEKEND_START:  # Si es fin de semana
        welcome_message = random.choice(weekend_welcome_messages)
    else:
        welcome_message = random.choice(default_welcome_messages)

    # Enviamos el mensaje de bienvenida al grupo
    reply_markup=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📏 Leer las Reglas",
                    url="https://t.me/Akira_Senpai_bot?start=rules"
                ),
                InlineKeyboardButton(
                    "🏆 Concursos",
                    url="https://t.me/Akira_Senpai_bot?start=contests"
                )
            ],
            [
                InlineKeyboardButton(
                    "📱 MiniApp",
                    url="https://t.me/Akira_Senpai_bot?startapp"
                ),
            ],
        ]
    )
    msg = await message.reply_text(text=f"{welcome_message}", reply_markup=reply_markup)
    await app.set_reaction(chat_id, msg.id, reaction=[ReactionTypeEmoji(emoji="😁")])

    #until_date=utils.zero_datetime()
    until_date = datetime.now() + timedelta(days=10) # Establecer until_date a 10 días a partir del momento actual

    user = await users.find_one({"user_id": new_user_id})
    if user is None:
        timestamp = datetime.now().timestamp()
        await users.insert_one({"user_id": new_user_id, "enter_date": timestamp})
        try:
            await app.restrict_chat_member(chat_id, new_user_id, permissions, until_date=until_date)
        except Exception as e:
            print(e)