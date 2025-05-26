import socket
import threading
import pandas as pd
import os
from datetime import datetime

# ----------------------------------------------------------------------
# Carga de archivos .parquet
base_path = os.path.dirname(os.path.abspath("__file__"))
root_path = os.path.abspath(os.path.join(base_path, "..", ".."))
db_path = os.path.join(root_path, "Central_Server", "Resources", "DB")

users_path = os.path.join(db_path, 'users.parquet')
users_data_path = os.path.join(db_path, 'users_data.parquet')

try:
    users_df = pd.read_parquet(users_path)
    users_data_df = pd.read_parquet(users_data_path)
    print("✅ Archivos .parquet cargados correctamente\n")
except Exception as e:
    print(f"❌ Error al cargar archivos .parquet: {e}")

# ----------------------------------------------------------------------
# Funciones auxiliares

def buscar_usuario_por_numero(numero):
    try:
        resultado = users_data_df[users_data_df['number'] == int(numero)]
        if not resultado.empty:
            return resultado.iloc[0]['user']
    except Exception as e:
        print(f"[ERROR] Buscando usuario por número: {e}")
    return None

def validar_credenciales(user_input, password_input):
    try:
        match = users_df[
            (users_df['user'] == user_input) &
            (users_df['password'] == password_input)
        ]
        return not match.empty
    except Exception as e:
        print(f"[ERROR] Validando credenciales: {e}")
        return False

# ----------------------------------------------------------------------
# Configuración del servidor

HOST = '0.0.0.0'
PORT = 10000
MAX_CLIENTES = 3
clientes_activos = 0
lock = threading.Lock()

def manejar_cliente(conn, addr):
    global clientes_activos
    print(f"[+] Cliente conectado desde: {addr}")

    try:
        conn.sendall(b"Autenticacion requerida (user|password):\n")
        datos = conn.recv(1024).decode().strip()

        if '|' not in datos:
            conn.sendall(b"Formato invalido. Desconectando.\n")
            conn.close()
            return

        user_input, password_input = datos.split('|', 1)

        if not validar_credenciales(user_input, password_input):
            conn.sendall(b"Credenciales invalidas. Desconectando.\n")
            conn.close()
            return

        conn.sendall(b"Autenticacion exitosa. Bienvenido.\n")
        peticion_num = 1

        while True:
            datos = conn.recv(1024)
            if not datos:
                break

            mensaje = datos.decode().strip().upper()
            print(f"[{addr}] Petición {peticion_num}: {mensaje}")
            peticion_num += 1

            if mensaje == "HOLA":
                respuesta = "Hola cliente 👋"
            elif mensaje == "HORA":
                respuesta = f"Hora actual: {datetime.now().strftime('%H:%M:%S')}"
            elif mensaje.startswith("USER"):
                partes = mensaje.split('|')
                if len(partes) > 1:
                    usuario = buscar_usuario_por_numero(partes[1])
                    if usuario:
                        respuesta = f"El usuario {partes[1]} es: {usuario}"
                    else:
                        respuesta = f"Usuario {partes[1]} no encontrado"
                else:
                    respuesta = "Formato incorrecto para USER. Usa: USER|numero"
            elif mensaje == "SALIR":
                respuesta = "Adiós 👋"
                conn.sendall(respuesta.encode())
                break
            else:
                respuesta = f"Comando desconocido: {mensaje}"

            conn.sendall(respuesta.encode())

    except Exception as e:
        print(f"[ERROR] Con cliente {addr}: {e}")
    finally:
        conn.close()
        with lock:
            clientes_activos -= 1
        print(f"[-] Cliente {addr} desconectado")

def aceptar_conexiones():
    global clientes_activos

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"🚀 Servidor A escuchando en {HOST}:{PORT} (máximo {MAX_CLIENTES} clientes)\n")

    while True:
        conn, addr = servidor.accept()
        with lock:
            if clientes_activos >= MAX_CLIENTES:
                conn.sendall(b"Servidor ocupado. Intenta luego.")
                conn.close()
                continue
            clientes_activos += 1

        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
        hilo.start()

if __name__ == "__main__":
    aceptar_conexiones()
