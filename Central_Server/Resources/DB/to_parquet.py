import os
import pandas as pd

# Ruta base: donde está este script (to_parquet.py)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Carpeta donde están los CSV (subcarpeta 'csv' dentro de base_dir)
csv_folder = os.path.join(base_dir, "csv")

# Recorrer todos los archivos CSV de la carpeta
for filename in os.listdir(csv_folder):
    if filename.endswith(".csv"):
        csv_path = os.path.join(csv_folder, filename)

        # Guardar el .parquet en base_dir (donde está el script)
        parquet_filename = os.path.splitext(filename)[0] + ".parquet"
        parquet_path = os.path.join(base_dir, parquet_filename)

        try:
            df = pd.read_csv(csv_path)
            df.to_parquet(parquet_path, index=False)
            print(f"✅ Convertido: {filename} → {parquet_filename}")
        except Exception as e:
            print(f"❌ Error al convertir {filename}: {e}")
