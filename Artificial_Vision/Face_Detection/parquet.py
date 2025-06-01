import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np

# Estructura del DataFrame: columna "user" (str) y "vector" (lista de 128 float)
df = pd.DataFrame(columns=["user", "vector"])

# Definir el tipo de cada columna para asegurarnos que es compatible
schema = pa.schema([
    ("user", pa.string()),
    ("vector", pa.list_(pa.float32(), list_size=128)),  # vector fijo de 128 floats
])

# Convertir el DataFrame vacío al formato compatible con pyarrow
table = pa.Table.from_pandas(df, schema=schema)

# Guardar el archivo .parquet
pq.write_table(table, "info.parquet")

print("✅ Archivo info.parquet creado con esquema compatible.")
