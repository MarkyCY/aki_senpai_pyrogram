import os
import psutil

def verif_ram(umbral):
    mem = psutil.virtual_memory()
    
    # Calcular el uso de la RAM en porcentaje
    uso_ram = mem.percent
    
    # Verificar si el uso de la RAM supera el umbral
    if uso_ram >= umbral:
        print(f"Uso de RAM: {uso_ram:.2f}%")
        os.system(f"kill -9 {os.getpid()} && bash startup.sh")
    else:
        print(f"Uso de RAM: {uso_ram:.2f}%")