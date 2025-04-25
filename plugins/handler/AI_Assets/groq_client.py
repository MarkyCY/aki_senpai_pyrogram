import datetime
import os
import json
from typing import Any, Optional, List

from google import genai
from google.genai import types
from pyrogram.types import Message

from plugins.handler.AI_Assets.news import buscar_noticias
from plugins.handler.AI_Assets.utils import format_message_to_markdown


def _load_file(path: str) -> Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f) if path.endswith('.json') else f.read()


class GeminiClient:
    def __init__(
        self,
        system_prompt_path: str,
        tools_config: str,
        emoji_list: str,
    ):
        # Inicializa el cliente de Google Gen AI con la API Key de Gemini
        self.client = genai.Client(api_key=os.getenv('GEMINI_API'))
        # Carga el prompt del sistema, configuración de herramientas y emojis permitidos
        self.system_prompt = _load_file(system_prompt_path)
        self.tools_config = _load_file(tools_config)
        self.allowed_emojis = _load_file(emoji_list)

    def build_prompt(
        self,
        message: Message,
        user_info: str,
        mentions: List[str],
    ) -> str:
        """
        Construye el prompt para la API de Gemini basándose en el mensaje del usuario,
        la información del usuario y las menciones.
        """
        text = format_message_to_markdown(message)
        input_text = f"""
"Entrada": {{
    "from": @{message.from_user.username},
    "user_description": "{user_info}"
}},
"""

        if mentions:
            input_text += f"""
"About": {mentions},
"user": "{text}",
Akira answer (Nueva respuesta):"""
        else:
            input_text += f"""
"user": "{text}"
"today" = {datetime.datetime.now()}
"""

        return input_text

    async def generate_response(
        self,
        input_text: str,
        chat_id: int,
        premium: bool,
    ) -> Optional[str]:
        try:
            # Preparamos contenido de usuario
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=input_text)],
                )
            ]

            buscar_noticias_delacration = {
                "name": "buscar_noticias",
                "description": "Busca las últimas noticias de anime",
                "parameters": None
            }

            # Configuramos herramientas: buscar_noticias y GoogleSearch
            tools = [
                # types.Tool(
                #     function_declarations=[buscar_noticias_delacration],
                # ),
                types.Tool(google_search=types.GoogleSearch()),
            ]

            # Configuración de generación
            generate_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                tools=tools,
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text=self.system_prompt)],
            )

            # Stream de respuesta
            respuesta = []
            for chunk in self.client.models.generate_content_stream(
                model="gemini-2.5-flash-preview-04-17",
                contents=contents,
                config=generate_config,
            ):
                if hasattr(chunk, 'candidates') and chunk.candidates[0].content.parts[0].function_call:
                    function_call = chunk.candidates[0].content.parts[0].function_call
                    print(function_call)
                    # if function_call.name == "buscar_noticias":
                    #     print("Buscando noticias...")
                    #     result = buscar_noticias()
                    #     print(f"Resultados: {result}")
                    #     return result
                elif chunk.text:
                    respuesta.append(chunk.text)

            return "".join(respuesta)

        except Exception as e:
            print(f"API Error Gemini: {e}")
            return None

# Ejemplo de uso:
# client = GeminiClient('system_prompt.txt', 'tools.json', 'emojis.json')
# prompt = client.build_prompt(message, user_info, mentions)
# respuesta = await client.generate_response(prompt, chat_id, premium)
