import os
import json
import base64

from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# api_key = os.getenv('GROQ_API')

# def to_base64(image_path, output_size=(200, 200)):
#     # Abrir la imagen
#     with Image.open(image_path) as img:
#         # Convertir la imagen a modo RGB
#         img = img.convert("RGB")
#         # Redimensionar la imagen
#         img = img.resize(output_size, Image.LANCZOS)
        
#         # Guardar la imagen en un buffer
#         buffered = BytesIO()
#         img.save(buffered, format="JPEG")
        
#         # Convertir la imagen a base64
#         img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
#         return img_base64

# def detect_safe_search(path):
#     """Detects unsafe features in the file."""
#     from groq import Groq

#     client = Groq(
#         api_key=api_key,
#     )

#     base64_image = to_base64(path)

#     completion = client.chat.completions.create(
#     model="llama-3.2-11b-vision-preview",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {
#                     "type": "text",
#                     "text": """Completa este json del 1 al 5 de puntaje con las categorías que consideres para la imagen, tu decides si esto lo pueden ver niños:

# Indicador de puntaje:
# 1. Muy permitido
# 2. Medianamente permitido
# 3. Permitido
# 4. Aún se puede mostrar porque no hay contenido delicado
# 5. No se puede mostrar porque hay contenido delicado

# Indicador de etiqueta del json sobre la imagen:
# adult_score: Porno, Desnudos, Sexo, Pene, Teta, Culo, Vagina
# medical_score: Incisiones, Sangre, Heridas abiertas
# violence_score: Asesinato, Golpes, Tortura
# what_see: Descripción de la imagen

# Formato:
# {
#     "adult_score": int,
#     "medical_score": int,
#     "violence_score": int,
#     "what_see": str
#  }

# IMPORTANTE: Debes ser estricto y sincero con cada categoría."""
#                 },
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{base64_image}"
#                     }
#                 }
#             ]
#         },
#         {
#             "role": "assistant",
#             "content": ""
#         }
#     ],
#     temperature=1,
#     # max_tokens=1024,
#     # top_p=1,
#     stream=False,
#     response_format={"type": "json_object"},
# )

#     comp = json.loads(completion.choices[0].message.content)

#     text = f"""
# Adulto {comp["adult_score"]} 
# Médico {comp["medical_score"]} 
# Violencia {comp["violence_score"]}

# Que se ve?: {comp["what_see"]}
# """
    
    
#     #"adult", comp.adult, "medical", comp.medical, "violence", comp.violence, "racy", comp.racy

#     safe = True
    
#     if comp["adult_score"] >= 5:
#         safe = False

#     if comp["medical_score"] >= 5:
#         safe = False

#     if comp["violence_score"] >= 5:
#         safe = False
    
#     return safe, text


import base64
import io
from groq import Groq
from PIL import Image
import requests

# Función para codificar imágenes a base64
# def encode_image(image):
#     buffered = io.BytesIO()
#     image.save(buffered, format="JPEG")
#     return base64.b64encode(buffered.getvalue()).decode('utf-8')

def encode_image(image_path, output_size=(200, 200)):
    # Abrir la imagen
    with Image.open(image_path) as img:
        # Convertir la imagen a modo RGB
        img = img.convert("RGB")
        # Redimensionar la imagen
        img = img.resize(output_size, Image.LANCZOS)
        
        # Guardar la imagen en un buffer
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        
        # Convertir la imagen a base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return img_base64

# Función de análisis de imágenes con el modelo de visión
def analyze_image(image, prompt, api_key, is_url=False):
    client = Groq(api_key=api_key)
    
    try:
        if is_url:
            # Si es una URL, usamos directamente la URL de la imagen
            image_url = image
        else:
            # Si es una imagen subida, la codificamos en base64
            base64_image = encode_image(image)
            image_url = f"data:image/jpeg;base64,{base64_image}"

        # Llamada a la API de Groq con el formato adecuado
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            temperature=2,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Función de verificación de seguridad con Llama Guard
def check_content_safety(image_description, api_key):
    client = Groq(api_key=api_key)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are a content safety classifier. Analyze the text and determine if it contains unsafe content for kids or younger viewers."
                },
                {
                    "role": "user", 
                    "content": f"Analyze this image description for unsafe content: {image_description}\nRespond with 'safe' or 'unsafe' with reasons."
                }
            ],
            model="llama-guard-3-8b",
        )
        res = chat_completion.choices[0].message.content
        print(image_description, res.lower())
        if "unsafe" in res.lower():
            return "unsafe"
        return "safe"
    except Exception as e:
        return f"Error: {str(e)}"

# Función principal de procesamiento
def process_image(image, url, prompt, api_key):
    if not api_key:
        return "Please enter your Groq API Key", ""
        
    try:
        if image:
            description = analyze_image(image, prompt, api_key)
            safety = check_content_safety(description, api_key)
            return description, safety
        elif url:
            try:
                response = requests.get(url)
                img = Image.open(io.BytesIO(response.content))
                description = analyze_image(url, prompt, api_key, is_url=True)
                safety = check_content_safety(description, api_key)
                return description, safety
            except:
                return "Invalid URL or image format", ""
        else:
            return "Please upload an image or enter a URL", ""
    except Exception as e:
        return f"Error processing image: {str(e)}", ""
