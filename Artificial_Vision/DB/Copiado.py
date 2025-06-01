import os
import shutil

# Carpeta origen y destino
carpeta_origen = r"C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\DB\KDEF_and_AKDEF\KDEF"
carpeta_destino = r"C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\DB\impress"

# Crear carpeta destino si no existe
os.makedirs(carpeta_destino, exist_ok=True)

# Lista para guardar los archivos encontrados
archivos_encontrados = []

for root, dirs, files in os.walk(carpeta_origen):
    for file in files:
        if file.endswith("S.JPG"):
            ruta_completa = os.path.join(root, file)
            archivos_encontrados.append(ruta_completa)

print(f"Archivos encontrados: {len(archivos_encontrados)}")

# Copiar los archivos a la carpeta destino
for archivo in archivos_encontrados:
    nombre_archivo = os.path.basename(archivo)
    destino = os.path.join(carpeta_destino, nombre_archivo)
    shutil.copy2(archivo, destino)

print("Copiado completado.")
