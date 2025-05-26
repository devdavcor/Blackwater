import socket

# Configuración del cliente
SERVER_IP = '127.0.0.1'  # Cambia esto por la IP del servidor si no es local
PORT = 49914













def start_client():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, PORT))

            # Recibe mensaje de bienvenida
            bienvenida = client_socket.recv(1024)
            print("🟢 Servidor:", bienvenida.decode('utf-8'))

            while True:
                mensaje = input("💬 Tú: ")
                if mensaje.lower() in ["salir", "exit", "quit"]:
                    print("👋 Desconectando del servidor...")
                    break
                client_socket.sendall(mensaje.encode('utf-8'))

                respuesta = client_socket.recv(1024)
                print("📨 Servidor:", respuesta.decode('utf-8'))

    except ConnectionRefusedError:
        print("❌ No se pudo conectar con el servidor.")
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    start_client()
