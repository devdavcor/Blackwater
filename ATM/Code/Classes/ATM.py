import socket

class ATM:
    def __init__(self, ip_branch, port_branch):
        self.ip_branch = ip_branch
        self.port_branch = port_branch

    def start(self):
        """Inicia la conexión con el servidor Branch y permite enviar mensajes manualmente."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_branch, self.port_branch))
            print("[C] Conectado con B")

            while True:
                msg = input("[C] Mensaje: ")
                if msg.strip().lower() == "salir":
                    print("[C] Cerrando conexión.")
                    break

                s.sendall(msg.encode())
                data = s.recv(1024)
                print(f"[C] Respuesta: {data.decode()}")

if __name__ == "__main__":
    # IP y puerto de Branch Server (B) quemados para pruebas
    ip_b = "127.0.0.1"
    port_b = 11000

    atm = ATM(ip_b, port_b)
    atm.start()
