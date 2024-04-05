from pyrogram import Client
from pyrogram.types import Message, ReplyParameters
from pyrogram import enums, errors
from pyrogram import filters
from pyrogram.file_id import FileId
from pyrogram.raw.functions.stickers import RemoveStickerFromSet, AddStickerToSet, CreateStickerSet
from pyrogram.raw.functions.messages import GetStickerSet, UploadMedia
from pyrogram.raw.types import InputStickerSetShortName, InputDocument, InputStickerSetShortName, InputStickerSetItem, InputMediaUploadedDocument, DocumentAttributeFilename
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image
import math
import os

@Client.on_message(filters.command('sticker_info'))
async def sticker_info_command(app: Client, message: Message):
    chat_id = message.chat.id
    # Si el mensaje tiene un reply y es un sticker
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker_id = message.reply_to_message.sticker.file_id
        await app.send_message(chat_id, text=f"El ID del sticker es: <code>{sticker_id}</code>", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id), parse_mode=enums.ParseMode.HTML)

    # Si el mensaje tiene un reply pero no es un sticker
    elif message.reply_to_message and not message.reply_to_message.sticker:
        await app.send_message(chat_id, text="Este comando solo puede ser usado con stickers. Por favor, haz reply a un sticker.", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id))

    # Si el mensaje no tiene un reply
    else:
        await app.send_message(chat_id, text="Por favor, haz reply a un sticker para obtener su ID.")

@Client.on_message(filters.command('del_sticker'))
async def del_sticker_command(app: Client, message: Message):
    chat_id = message.chat.id
    
    if not (message.reply_to_message and message.reply_to_message.sticker):
        await app.send_message(chat_id, text="Por favor, haz reply a un sticker para obtener su ID.")
        return
    

    sticker_id = message.reply_to_message.sticker.file_id
    decoded = FileId.decode(sticker_id)


    try:
        sticker_to_remove = InputDocument(
            id=decoded.media_id,
            access_hash=decoded.access_hash,
            file_reference=decoded.file_reference,
        )
        result = await app.invoke(RemoveStickerFromSet(sticker=sticker_to_remove))
        
        if result:
            await app.send_message(chat_id, text="El sticker se ha eliminado del pack.", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id))
    except Exception as e:
        print(e)
        await app.send_message(chat_id, text="No se pudo eliminar el sticker.", reply_parameters=ReplyParameters(message_id=message.reply_to_message_id))


    ## Obtener el conjunto de stickers
    #stickerset = await app.invoke(GetStickerSet(
    #    stickerset=InputStickerSetShortName(short_name=packname),
    #    hash=0
    #))
    #
    #delete = {}
    #for s in stickerset.documents:
    #    # Guardamos una tupla con el id, access_hash y file_reference
    #    delete[s.attributes[1].alt] = (s.id, s.access_hash, s.file_reference)

    #sticker_id, access_hash, file_reference = delete[emoji]
    #print(sticker_id)
    #print(access_hash)
    #print(file_reference)


@Client.on_message(filters.command('steal'))
async def steal_sticker_command(app: Client, message: Message):
    msg = message
    user = msg.from_user
    args = message.text.split(None, 1)
    packnum = 0
    packname = "f" + str(user.id) + "_by_labolitacu_bot"
    
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            stickerset = await app.invoke(GetStickerSet(
                stickerset=InputStickerSetShortName(short_name=packname),
                hash=0
            ))
            
            if len(stickerset.documents) >= max_stickers:
                packnum += 1
                packname = ("f" + str(packnum) + "_" + str(user.id) + "_by_labolitacu_bot")
            else:
                packname_found = 1
        except errors.StickersetInvalid as e:
            if e.ID == "STICKERSET_INVALID":
                packname_found = 1
    stealsticker = "stealsticker.webp"
    is_animated = False
    is_video = False
    is_photo = False
    file_id = ""
    
    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            if msg.reply_to_message.sticker.is_video is True:
                is_video = True
            file_id = msg.reply_to_message.sticker.file_id

        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo.file_id
            is_photo = True
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            await message.reply_text(text="No puedo robar eso.")
        

        if is_animated:
            await app.download_media(file_id, file_name="./stealsticker.tgs")
        elif is_video:
            await app.download_media(file_id, file_name="./stealsticker.webm")
        else:
            await app.download_media(file_id, file_name="./stealsticker.webp")

        if len(args) >= 2:
            sticker_emoji = str(args[1])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"

        if not is_animated:
            try:
                im = Image.open(stealsticker)
                maxsize = (512, 512)
                if (im.width and im.height) < 512:
                    size1 = im.width
                    size2 = im.height
                    if im.width > im.height:
                        scale = 512 / size1
                        size1new = 512
                        size2new = size2 * scale
                    else:
                        scale = 512 / size2
                        size1new = size1 * scale
                        size2new = 512
                    size1new = math.floor(size1new)
                    size2new = math.floor(size2new)
                    sizenew = (size1new, size2new)
                    im = im.resize(sizenew)
                else:
                    im.thumbnail(maxsize)
                if not msg.reply_to_message.sticker:
                    im.save(stealsticker, "WEBP")


                if is_photo is False:
                    sticker_id = message.reply_to_message.sticker.file_id
                    decoded = FileId.decode(sticker_id)

                    sticker_to_add = InputDocument(
                        id=decoded.media_id,
                        access_hash=decoded.access_hash,
                        file_reference=decoded.file_reference,
                    )

                    sticker=InputStickerSetItem(
                                document = sticker_to_add,
                                emoji=sticker_emoji  # El emoji asociado al sticker
                            )
                    
                    sticker_set = InputStickerSetShortName(
                        short_name=packname
                    )

                elif is_photo is True:
                    file_path = f"./{stealsticker}"
                    file_name = stealsticker
                    media = await app.invoke(
                        UploadMedia(
                            peer=await app.resolve_peer(msg.chat.id),
                            media=InputMediaUploadedDocument(
                                mime_type=app.guess_mime_type(file_path) or "application/zip",
                                file=await app.save_file(file_path),
                                attributes=[DocumentAttributeFilename(file_name=file_name)]
                            )
                        )
                    )
                    
                    sticker_set = InputStickerSetShortName(
                        short_name=packname
                    )

                    sticker_to_add = InputDocument(
                        id=media.document.id,
                        access_hash=media.document.access_hash,
                        file_reference=media.document.file_reference,
                    )

                    sticker=InputStickerSetItem(
                                document = sticker_to_add,
                                emoji=sticker_emoji  # El emoji asociado al sticker
                            )
                
                await app.invoke(
                    AddStickerToSet(
                        stickerset=sticker_set,
                        sticker=sticker
                    )
                )

                keyb = [[InlineKeyboardButton('Pack Robao', url=f'https://t.me/addstickers/{packname}')]]
                await message.reply_text(
                    text=f"Sticker agregado a tu Pack de Stickers."
                    + f"\nEl emoji es: {sticker_emoji}",
                    parse_mode=enums.ParseMode.HTML, 
                    reply_markup=InlineKeyboardMarkup(keyb)
                )

            except OSError as e:
                await msg.reply_text(text="Solo puedo robar imágenes.")
                print(e)
                return
            
            except errors.StickersetInvalid as e:
                if e.ID == "STICKERSET_INVALID":
                    input_user = await app.resolve_peer(user.id)
                    await makepack_internal(
                        app,
                        msg,
                        user,
                        input_user,
                        packname,
                        packnum,
                        png_sticker=sticker
                    )

                elif e.result_json['description'] == "Bad Request: can't parse sticker: expected a Unicode emoji":
                        await msg.reply_text(text="Emoji no válido.")
    
async def makepack_internal(
    app,
    msg,
    user,
    input_user,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
):
    name = user.first_name
    name = name[:50]
    
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = " " + str(packnum)
        if png_sticker:
            success = await app.invoke(CreateStickerSet(
                user_id = input_user,
                short_name = packname,
                title = f"{name} Steal Pack" + extra_version,
                stickers = [png_sticker]
            ))
        if tgs_sticker:
            success = await app.invoke(CreateStickerSet(
                user_id = input_user,
                short_name = packname,
                title = f"{name} Steal Pack" + extra_version,
                stickers = [tgs_sticker]
            ))
    except Exception as e:
        print(e)
        return
        if e.message == "El nombre del stickerpack ya está ocupado":
            await msg.reply_text(
                text="Nuevo paquete de sticker creado. Miralo [aquí](https://t.me/addstickers/%s" % packname,
                parse_mode=enums.ParseMode.MARKDOWN,
            )
        elif e.message in ("Peer_id_invalid", "El bot ha sido bloqueado por el usuario"):
            await msg.reply_text(
                text="Contáctame en privado primero.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        text="Iniciar", url=f"t.me/Akira_Senpai_bot")
                ]]),
            )
        elif e.message == "Internal Server Error: created sticker set not found (500)":
            await msg.reply_text(
            text="Paquete de sticker creado siuuu. Miralo [aquí](https://t.me/addstickers/%s" % packname,
            parse_mode=enums.ParseMode.MARKDOWN,
        )  
        return

    if success:
        await msg.reply_text(
            text="Paquete de sticker creado siuuu. Miralo [aquí](https://t.me/addstickers/%s" % packname,
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await msg.reply_text(
            text="No pude crear el Pack de Stickers :(")