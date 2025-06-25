import os
import json
from groq import Groq
from typing import Optional, Any
from pyrogram.types import Message

#from plugins.handler.AI_Assets.get_web_data import WebGetContents_Tool
from plugins.handler.AI_Assets.news import buscar_noticias
from plugins.handler.AI_Assets.utils import format_message_to_markdown
from plugins.others.WebNewSearch import web_new_search
from plugins.others.WebSearch import web_search

class GroqClient:
    def __init__(self, system_prompt_path: str, tools_config: str, emoji_list: str):
        self.client = Groq(api_key=os.getenv('GROQ_API'))
        self.system_prompt = self._load_file(system_prompt_path)
        self.tools = self._load_file(tools_config)
        self.allowed_emojis = self._load_file(emoji_list)
        
    def _load_file(self, path: str) -> Any:
        with open(path, 'r', encoding='utf-8') as f:  # Especifica la codificación utf-8
            return json.load(f) if path.endswith('.json') else f.read()
        
    def build_prompt(self, message: Message, user_info: str, mentions: list) -> str:
        """
        Construye el prompt para la API de Groq basándose en el mensaje del usuario,
        la información del usuario y las menciones.
        """
        text = format_message_to_markdown(message)
        input_text = f"""
"Entrada" : {{
    "from": "@{message.from_user.username}",
    "user_description": "{user_info}"
}},
"""

        if mentions:
            input_text += f""""Reply" : {mentions},
"user": "{text}",
Akira answer (New answer of you):"""
        else:
            input_text += f"""
"user": "{text}"
"""
        return input_text

    async def generate_response(self, input_text: str, chat_id: int, premium: bool) -> Optional[str]:
        try:
            messages = self._build_messages(input_text)
            response = self.client.chat.completions.create(
                messages=messages,
                model="llama-3.3-70b-versatile",
                # tools=self.tools,
                # tool_choice="auto",
                max_tokens=1000
            )
            
            return self._process_tool_calls(response, messages, premium)
            
        except Exception as e:
            print(f"API Error: {e}")
            return None

    def _build_messages(self, input_text: str) -> list:
        print(f"""
---------------------------------
{self.system_prompt}
+++++++++++++++++++++++++++++++++
{input_text}
---------------------------------
""")
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": input_text}
        ]

    def _process_tool_calls(self, response, messages, premium) -> str:
        if not response.choices[0].message.tool_calls:
            return response.choices[0].message.content

        available_functions = {
            # "buscar_noticias": buscar_noticias,
            #"web_search": web_search,
            #"web_new_search": web_new_search,
            #"view_web": WebGetContents_Tool,
        }

        messages.append(response.choices[0].message)

        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            print(tool_call.function.arguments)
            function_args = json.loads(tool_call.function.arguments)
            function_args["premium"] = premium
            
            if function_name in available_functions:
                print(f"Utilizando la función {function_name}")
                print(function_args)
                function_response = available_functions[function_name](**function_args)
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

        second_response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
        )

        return second_response.choices[0].message.content