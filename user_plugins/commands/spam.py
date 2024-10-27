from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime

import time

stop_spam = False

@Client.on_message(filters.command("spam"))
def spam(app: Client, message: Message):

    if message.chat.id != -1001485529816:
        return message.reply_text("Este comando es exclusivo de Otaku Senpai")
    
    current_hour = datetime.now().hour
    if current_hour >= 0 and current_hour < 5:
        pass
    else:
        return message.reply_text("Solo se puede hacer spam en horario de la madrugada.")
    
    global stop_spam
    stop_spam = False

    messages = []

    for i in range(101):
        if stop_spam:
            app.delete_messages(message.chat.id, messages)
            messages = []
            break
        
        msg = app.send_message(message.chat.id, f"Spam {i}", message_thread_id=252001)
        messages.append(msg.id)

        if i % 5 == 0:
            time.sleep(3)
            app.delete_messages(message.chat.id, messages)
            messages = []

    app.delete_messages(message.chat.id, messages)

@Client.on_message(filters.command("stop"))
def stopspam(app: Client, message: Message):
    if message.chat.id != -1001485529816:
        return message.reply_text("Este comando es exclusivo de Otaku Senpai")
    global stop_spam
    stop_spam = True

@Client.on_message(filters.photo & filters.group & filters.bot & filters.user(1733263647))
def spam_handler(app: Client, message: Message):
    global stop_spam
    text = message.caption.split(' ')

    if text[1] != "waifu":
        return
    
    stop_spam = True

@Client.on_message(filters.photo & filters.group & filters.bot & filters.user(1964681186))
def spam_handler_husband(app: Client, message: Message):
    global stop_spam
    text = message.caption.split(' ')

    if text[1] != "husbando":
        return
    
    stop_spam = True
    