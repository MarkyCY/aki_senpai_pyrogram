from plugins.others.compare_img import comparar_imagenes
from database.mongodb import get_db

import os



async def img_error(downloaded_file, file_id):
    db = await get_db()
    img_bl = db.img_blacklist
    user = await img_bl.find_one({"file_id": file_id})

    if user is not None:
        return True
    
    directorio = './revise/blacklist'

    archivos_jpg = [archivo for archivo in os.listdir(directorio) if archivo.lower().endswith('.jpg')]

    coincide = False

    for archivo in archivos_jpg:

        name, ext = os.path.splitext(archivo)

        origin = f"{directorio}/{name}{ext}"
        compara = await comparar_imagenes(origin, downloaded_file)

        if compara is False:
            continue
        else:
            coincide = True

    return coincide