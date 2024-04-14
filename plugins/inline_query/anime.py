from pyrogram import Client
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton)

from database.mongodb import get_db

@Client.on_inline_query()
async def answer(client, inline_query):
    db = await get_db()
    animes = db.animes

    args = inline_query.query.split(" ")
    if len(args) <= 1:
        await inline_query.answer(
            results = [
                InlineQueryResultArticle(
                    id="Anime",
                    title="Anime",
                    description="Buscar Anime",
                    input_message_content=InputTextMessageContent(
                        message_text="Buscar Anime",
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Buscar Anime",
                                    switch_inline_query_current_chat='<ANIME> '
                                )
                            ]
                        ]
                    )
                ),
                InlineQueryResultArticle(
                    id="Manga",
                    title="Manga",
                    description="Buscar Manga",
                    input_message_content=InputTextMessageContent(
                        message_text="Buscar Manga",
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Buscar Manga",
                                    switch_inline_query_current_chat='<MANGA> '
                                )
                            ]
                        ]
                    )
                ),
                InlineQueryResultArticle(
                    id="Videojuegos",
                    title="Videojuegos",
                    description="Buscar Videojuegos",
                    input_message_content=InputTextMessageContent(
                        message_text="Buscar Videojuegos",
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Buscar Videojuegos",
                                    switch_inline_query_current_chat='<GAMES> '
                                )
                            ]
                        ]
                    )
                ),
            ],
            cache_time=1
        )
    elif args[0] == "<ANIME>":
        results = []
        search = ' '.join(args[1:])
        async for anime in animes.find({'title': {'$regex': f'.*{search}.*', '$options': 'i'}}).limit(10):
            text=f"⛩️{anime['title']}"
            img="https://i.postimg.cc/Z5sHk6wJ/photo-2023-11-24-08-52-37.jpg"
            result = InlineQueryResultArticle(
                id=str(anime['_id']),  # El primer argumento ahora es 'id', no 'titulo'
                thumb_url=img,
                title=f"Anime: {anime['title']}",
                description=f"Nombre de Anime: {anime['title']}",
                url=anime['link'],
                input_message_content=InputTextMessageContent(
                    message_text=text
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Ir a ver",
                                url=anime['link']
                            )
                        ]
                    ]
                )
            )
            results.append(result)

        await inline_query.answer(
            results=results,
            cache_time=1
        )
    else:
        await inline_query.answer(
            results=[],
            cache_time=1
        )