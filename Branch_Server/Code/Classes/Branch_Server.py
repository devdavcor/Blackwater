import socket
import threading

class BranchServer:
    def __init__(self, server_a_ip, server_a_port, listen_port=11000):
        self.server_a_ip = server_a_ip
        self.server_a_port = server_a_port
        self.listen_port = listen_port
        self.conn_a = None

    def connect_to_server_a(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_a_ip, self.server_a_port))
        print("[B] Conectado a servidor A")

        message = s.recv(1024).decode()
        print(f"[B] Mensaje de A: {message}")

        credentials = "admin|admin"
        s.sendall(credentials.encode())

        response = s.recv(1024).decode()
        print(f"[B] Respuesta de autenticación: {response}")

        if "successful" not in response.lower():
            print("[B] Autenticación fallida. Cerrando conexión.")
            s.close()
            return None

        return s

    def handle_client_c(self, conn_c, conn_a):
        try:
            while True:
                data = conn_c.recv(1024)
                if not data:
                    break
                print(f"[B] Recibido de C: {data.decode()}")
                conn_a.sendall(data)

                response = conn_a.recv(1024)
                print(f"[B] Respuesta de A: {response.decode()}")
                conn_c.sendall(response)
        except Exception as e:
            print(f"[B] Error en la comunicación: {e}")
        finally:
            conn_c.close()

    def listen_for_client_c(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('0.0.0.0', self.listen_port))
            server.listen()
            print("[B] Esperando conexión de C...")
            conn_c, addr = server.accept()
            print(f"[B] Cliente C conectado: {addr}")
            self.handle_client_c(conn_c, self.conn_a)

    def start(self):
        self.conn_a = self.connect_to_server_a()
        if self.conn_a:
            self.listen_for_client_c()


if __name__ == "__main__":
    # Argumentos quemados (puedes modificarlos aquí para pruebas)
    ip_a = "127.0.0.1"
    port_a = 10000

    branch_server = BranchServer(ip_a, port_a)
    branch_server.start()

