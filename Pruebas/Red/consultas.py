import os
import pandas as pd
import numpy as np
import face_recognition
import pickle

# Rutas base y archivos
base_path = os.path.dirname(os.path.abspath("__file__"))
blackwater_root = os.path.abspath(os.path.join(base_path, "..", ".."))
db_path = os.path.join(blackwater_root, "Central_Server", "Resources", "DB")

users_path = os.path.join(db_path, 'users.parquet')
users_data_path = os.path.join(db_path, 'users_data.parquet')
users_data_prueba_path = os.path.join(db_path, 'users_data_prueba.parquet')
users_balance_path = os.path.join(db_path, 'users_balance.parquet')
users_biometrics_path = os.path.join(db_path, 'users_biometrics.parquet')
administrators_path = os.path.join(db_path, 'administrators.parquet')
branches_path = os.path.join(db_path, 'branches.parquet')

# Cargar archivos parquet
try:
    users_df = pd.read_parquet(users_path)
    users_data_df = pd.read_parquet(users_data_path)
    users_balance_df = pd.read_parquet(users_balance_path)
    users_biometrics_df = pd.read_parquet(users_biometrics_path)
    administrators_df = pd.read_parquet(administrators_path)
    branches_df = pd.read_parquet(branches_path)
    prueba_df = pd.read_parquet(users_data_prueba_path)
    print("Todos los archivos se cargaron correctamente.")
except Exception as e:
    print(f"Error al cargar los archivos: {e}")


# Funciones para manejo de usuarios y balances

def search_user(df, user):
    try:
        resultado = df[df['user'] == user]
        if not resultado.empty:
            print(f"{user} se encontró en la base de datos")
            return True
        else:
            print(f"{user} no se encontró en la base de datos")
            return False
    except Exception as e:
        print(f"[ERROR] Buscando usuario: {e}")
        return None


def new_user(df, nuevo_usuario, ruta_archivo):
    try:
        user = nuevo_usuario.get('user')
        if user is None:
            print("⚠️ El diccionario no tiene clave 'user'.")
            return False
        if not search_user(df, user):
            print(f"🔄 Registrando nuevo usuario: {user}")
            nuevo_df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
            nuevo_df.to_parquet(ruta_archivo, index=False)
            print(f"✅ Usuario registrado y archivo actualizado: {ruta_archivo}")
            return True
        else:
            print("⛔ Usuario ya registrado.")
            return False
    except Exception as e:
        print(f"[ERROR] Registrando usuario: {e}")
        return False


def delete_user(df, user, ruta_archivo):
    try:
        if search_user(df, user):
            print(f"🗑️ Eliminando usuario: {user}")
            nuevo_df = df[df['user'] != user]
            nuevo_df.to_parquet(ruta_archivo, index=False)
            print(f"✅ Usuario eliminado y archivo actualizado: {ruta_archivo}")
            return True
        else:
            print("⚠️ Usuario no encontrado, no se puede eliminar.")
            return False
    except Exception as e:
        print(f"[ERROR] Eliminando usuario: {e}")
        return False


def update_balance(df, user, nuevo_balance, ruta_archivo):
    try:
        if df[df['user'] == user].empty:
            print(f"⛔ Usuario {user} no se encontró en la base de datos.")
            return False
        df.loc[df['user'] == user, 'balance'] = nuevo_balance
        print(f"✅ Balance actualizado para {user} a ${nuevo_balance}")
        df.to_parquet(ruta_archivo, index=False)
        print(f"💾 Archivo guardado en {ruta_archivo}")
        return True
    except Exception as e:
        print(f"[ERROR] Al actualizar el balance: {e}")
        return False


def withdraw_cash(df, user, cantidad, ruta_archivo):
    try:
        if df[df['user'] == user].empty:
            print(f"⛔ Usuario {user} no se encontró en la base de datos.")
            return False
        balance_actual = df.loc[df['user'] == user, 'balance'].values[0]
        if balance_actual < cantidad:
            print(f"❌ Fondos insuficientes. Balance actual: ${balance_actual}, requerido: ${cantidad}")
            return False
        nuevo_balance = balance_actual - cantidad
        df.loc[df['user'] == user, 'balance'] = nuevo_balance
        print(f"✅ Retiro exitoso. Nuevo balance para {user}: ${nuevo_balance}")
        df.to_parquet(ruta_archivo, index=False)
        print(f"💾 Archivo actualizado correctamente: {ruta_archivo}")
        return True
    except Exception as e:
        print(f"[ERROR] En operación de retiro: {e}")
        return False


def deposit_cash(df, user, cantidad, ruta_archivo):
    try:
        if df[df['user'] == user].empty:
            print(f"⛔ Usuario {user} no se encontró en la base de datos.")
            return False
        balance_actual = df.loc[df['user'] == user, 'balance'].values[0]
        nuevo_balance = balance_actual + cantidad
        df.loc[df['user'] == user, 'balance'] = nuevo_balance
        print(f"✅ Depósito exitoso. Nuevo balance para {user}: ${nuevo_balance}")
        df.to_parquet(ruta_archivo, index=False)
        print(f"💾 Archivo actualizado correctamente: {ruta_archivo}")
        return True
    except Exception as e:
        print(f"[ERROR] En operación de depósito: {e}")
        return False


def add_biometrics_from_image(df, user, image_path, ruta_archivo):
    try:
        if df[df["user"] == user].empty:
            print(f"⛔ El usuario {user} no existe en la base de datos.")
            return False
        imagen = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(imagen)
        if len(encodings) == 0:
            print(f"❌ No se detectó ningún rostro en la imagen: {image_path}")
            return False
        encoding = encodings[0]
        index = df.index[df['user'] == user].tolist()
        if len(index) == 1:
            df.at[index[0], 'biometrics'] = encoding.tolist()
        else:
            print(f"❌ No se encontró un único registro para el usuario {user}.")
            return False
        df.to_parquet(ruta_archivo, index=False)
        print(f"✅ Biométrico actualizado para {user} desde imagen '{image_path}' y guardado en {ruta_archivo}")
        return True
    except Exception as e:
        print(f"[ERROR] Agregando biométrico para {user}: {e}")
        return False


# Ejemplo de uso (puedes comentar o descomentar según lo que necesites)
nuevo_usuario = {
    'number': 9,
    'user': 'A002',
    'name': 'Ana',
    'last_name': 'López',
    'curp': 'ANAL920202MDF'
}

# new_user(prueba_df, nuevo_usuario, users_data_prueba_path)
update_balance(prueba_df, "A002", 1000000, users_data_prueba_path)
withdraw_cash(prueba_df, "A002", 50000, users_data_prueba_path)
deposit_cash(prueba_df, "A002", 250000, users_data_prueba_path)

user = "A002"
image_path = r"C:\Users\devdavcor\Documents\Blackwater\Artificial_Vision\DB\KDEF_and_AKDEF\KDEF\AM01\AM01NES.JPG"
add_biometrics_from_image(prueba_df, user, image_path, users_data_prueba_path)

# Uso de pickle para medir tamaño en bytes del registro
prueba_df = pd.read_parquet(users_data_prueba_path)
registro = prueba_df[prueba_df["user"] == "A002"].iloc[0]
registro_bytes = pickle.dumps(registro)
print(f"Tamaño del registro de A002 en bytes: {len(registro_bytes)}")

print("Data")
print(prueba_df.head(10))
print("\nData (sin 'biometrics'):")
print(prueba_df.drop(columns=['biometrics']).head(10))
print("\n")
