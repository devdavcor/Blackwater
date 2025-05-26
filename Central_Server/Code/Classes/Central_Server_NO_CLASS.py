import socket
import threading
import pandas as pd
import numpy as np
import os
from datetime import datetime

# ----------------------------------------------------------------------------------
# Configuración de rutas
base_path = os.path.dirname(os.path.abspath("__file__"))
blackwater_root = os.path.abspath(os.path.join(base_path, "..", "..",".."))

db_path = os.path.join(blackwater_root, "Central_Server", "Resources", "DB")

users_path = os.path.join(db_path, 'users.parquet')
users_data_path = os.path.join(db_path, 'users_data.parquet')
users_balance_path = os.path.join(db_path, 'users_balance.parquet')
users_biometrics_path = os.path.join(db_path, 'users_biometrics.parquet')
administrators_path = os.path.join(db_path, 'administrators.parquet')
branches_path = os.path.join(db_path, 'branches.parquet')

try:
    users_df = pd.read_parquet(users_path)
    users_data_df = pd.read_parquet(users_data_path)
    users_balance_df = pd.read_parquet(users_balance_path)
    users_biometrics_df = pd.read_parquet(users_biometrics_path)
    administrators_df = pd.read_parquet(administrators_path)
    branches_df = pd.read_parquet(branches_path)

    print("✅ Todos los archivos se cargaron correctamente.\n")

except Exception as e:
    print(f"❌ Error al cargar los archivos: {e}")

# ----------------------------------------------------------------------------------
# Funciones de autenticación
def buscar_usuario_por_numero(numero_buscado):
    try:
        resultado = users_data_df[users_data_df['number'] == int(numero_buscado)]
        if not resultado.empty:
            return resultado.iloc[0]['user']
    except Exception as e:
        print(f"[ERROR] buscando usuario: {e}")
    return None

def validar_credenciales(user_input, password_input):
    try:
        resultado = users_df[
            (users_df['user'] == user_input) &
            (users_df['password'] == password_input)
        ]
        return not resultado.empty
    except Exception as e:
        print(f"[ERROR] Validando credenciales: {e}")
        return False

# ----------------------------------------------------------------------------------
# Configuración del servidor
HOST = '0.0.0.0'
PUERTO = 0
MAX_CLIENTES = 3

clientes_activos = 0
lock = threading.Lock()

def manejar_cliente(conexion, direccion):
    global clientes_activos
    peticion_numero = 1
    print(f"[+] Conexión de {direccion}")

    try:
        conexion.sendall(b"Autenticacion requerida. Envia: user|password\n")
        datos = conexion.recv(1024).decode().strip()

        if '|' not in datos:
            conexion.sendall(b"Formato invalido. Desconectando.\n")
            conexion.close()
            return

        user_input, password_input = datos.split('|', 1)

        if not validar_credenciales(user_input, password_input):
            conexion.sendall(b"Credenciales invalidas. Desconectando.\n")
            conexion.close()
            return

        conexion.sendall(b"Autenticacion exitosa. Bienvenido.\n")

        while True:
            datos = conexion.recv(1024)
            if not datos:
                break

            print(f"Peticion {peticion_numero}")
            peticion_numero += 1

            mensaje = datos.decode().strip().upper()
            print(f"[{direccion}] -> {mensaje}")

            if mensaje == "HOLA":
                respuesta = "Hola cliente 👋"
            elif mensaje == "HORA":
                respuesta = f"Hora actual: {datetime.now().strftime('%H:%M:%S')}"
            elif mensaje.startswith("USER"):
                partes = mensaje.split('|')
                if len(partes) > 1:
                    usuariobuscado = buscar_usuario_por_numero(partes[1])
                    if usuariobuscado:
                        respuesta = f"El usuario {partes[1]} es: {usuariobuscado}"
                    else:
                        respuesta = f"El usuario {partes[1]} no existe"
                else:
                    respuesta = "Formato incorrecto para USER. Usa: USER|numero"
            elif mensaje == "SALIR":
                respuesta = "Adiós 👋"
                conexion.sendall(respuesta.encode())
                break
            else:
                respuesta = f"No entiendo: {mensaje}"

            conexion.sendall(respuesta.encode())

    except Exception as e:
        print(f"[ERROR] Con cliente {direccion}: {e}")
    finally:
        conexion.close()
        with lock:
            clientes_activos -= 1
        print(f"[-] Cliente {direccion} desconectado")

def aceptar_conexiones():
    global clientes_activos

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PUERTO))
    assigned_port = servidor.getsockname ()[1]  # Aquí está el puerto asignado
    print ( f"🚀 Servidor escuchando en {HOST}:{assigned_port}..." )
    servidor.listen()

    print(f"[SERVIDOR] Escuchando en {HOST}:{PUERTO} (máximo {MAX_CLIENTES} clientes)\n")

    while True:
        conexion, direccion = servidor.accept()
        with lock:
            if clientes_activos >= MAX_CLIENTES:
                print(f"[!] Cliente rechazado ({direccion}), límite alcanzado")
                conexion.sendall(b"Servidor ocupado. Intenta luego.")
                conexion.close()
                continue
            clientes_activos += 1

        hilo = threading.Thread(target=manejar_cliente, args=(conexion, direccion), daemon=True)
        hilo.start()

if __name__ == "__main__":
    aceptar_conexiones()
