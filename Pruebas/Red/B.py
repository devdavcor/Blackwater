import socket
import threading

# B se conecta a A con autenticación
def conectar_a_servidor_A():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 10000))
    print("[B] Conectado a servidor A")

    # Recibir solicitud de autenticación
    mensaje = s.recv(1024).decode()
    print(f"[B] Mensaje de A: {mensaje}")

    # Enviar credenciales
    credenciales = "admin|admin"  # <-- aquí cambias tus credenciales
    s.sendall(credenciales.encode())

    # Esperar respuesta
    respuesta = s.recv(1024).decode()
    print(f"[B] Respuesta de autenticación: {respuesta}")

    if "exitosa" not in respuesta.lower():
        print("[B] Autenticación fallida. Cerrando conexión.")
        s.close()
        return None
    return s

# B actúa como servidor para C
def manejar_cliente_c(conn_c, conn_a):
    try:
        while True:
            data = conn_c.recv(1024)
            if not data:
                break
            print(f"[B] Recibido de C: {data.decode()}")
            conn_a.sendall(data)  # Reenviar a A

            respuesta = conn_a.recv(1024)
            print(f"[B] Respuesta de A: {respuesta.decode()}")
            conn_c.sendall(respuesta)
    except Exception as e:
        print(f"[B] Error en la comunicación: {e}")
    finally:
        conn_c.close()

def escuchar_a_cliente_C(conn_a):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind(('0.0.0.0', 11000))
        servidor.listen()
        print("[B] Esperando conexión de C...")
        conn_c, addr = servidor.accept()
        print(f"[B] Cliente C conectado: {addr}")
        manejar_cliente_c(conn_c, conn_a)

# Principal
conn_a = conectar_a_servidor_A()
if conn_a:
    escuchar_a_cliente_C(conn_a)
