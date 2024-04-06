from deep_translator import GoogleTranslator
import asyncio

async def async_translate(description, source_language, target_language):
    loop = asyncio.get_event_loop()
    # Ejecuta la función translate de manera asíncrona
    translated_description = await loop.run_in_executor(
        None,  # None utiliza el executor por defecto
        lambda: GoogleTranslator(source=source_language, target=target_language).translate(text=description)
    )
    return translated_description