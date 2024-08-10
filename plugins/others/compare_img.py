from PIL import Image

import os

async def comparar_imagenes(imagen1, imagen2):
    # Abrir las imágenes
    img1 = Image.open(imagen1)
    img2 = Image.open(imagen2)

    # Verificar si las dimensiones de las imágenes son iguales
    if img1.size != img2.size:
        return False

    # Comparar los píxeles de ambas imágenes
    diferencia = 0
    for i in range(img1.size[0]):  # Ancho
        for j in range(img1.size[1]):  # Alto
            pixel_img1 = img1.getpixel((i, j))
            pixel_img2 = img2.getpixel((i, j))
            if pixel_img1 != pixel_img2:
                diferencia += 1

    # Calcular el porcentaje de similitud
    porcentaje_similitud = (1 - (diferencia / (img1.size[0] * img1.size[1]))) * 100

    # Definir un umbral de similitud (puedes ajustarlo según tus necesidades)
    umbral_similitud = 90

    # Devolver True si el porcentaje de similitud supera el umbral, False en caso contrario
    #print("Similaridad en porciento: ",porcentaje_similitud)
    
    if porcentaje_similitud >= umbral_similitud:
        return True
    else:
        return False
    

async def compare_images(image1):
    directorio = './revise'

    archivos_jpg = [archivo for archivo in os.listdir(directorio) if archivo.lower().endswith('.jpg')]

    coincide = False

    for archivo in archivos_jpg:

        name, ext = os.path.splitext(archivo)

        origin = f"{directorio}/{name}{ext}"
        compara = await comparar_imagenes(origin, image1)

        if compara is False:
            continue
        else:
            coincide = True

    return coincide