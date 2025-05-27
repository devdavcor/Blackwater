import socket
import threading
import pandas as pd
import os
from datetime import datetime

class Central_Server:
    def __init__(self, host='0.0.0.0', port=10000, max_clients=3):
        # Rutas y carga inicial de bases de datos parquet
        base_path = os.path.dirname(os.path.abspath("__file__"))
        root_path = os.path.abspath(os.path.join(base_path, "..", "..", ".."))
        db_path = os.path.join(root_path, "Central_Server", "Resources", "DB")

        self.users_path = os.path.join(db_path, 'users.parquet')
        self.users_data_path = os.path.join(db_path, 'users_data.parquet')

        self.users_df = None
        self.users_data_df = None

        self.load_databases()

        # Configuración del servidor
        self.host = host
        self.port = port
        self.max_clients = max_clients

        self.server_socket = None
        self.clients_active = 0
        self.clients_lock = threading.Lock()
        self.clients_connections = []  # Lista para almacenar conexiones activas

        self.running = False

    def load_databases(self):
        try:
            self.users_df = pd.read_parquet(self.users_path)
            self.users_data_df = pd.read_parquet(self.users_data_path)
            print("✅ Parquet files loaded successfully\n")
        except Exception as e:
            print(f"❌ Error loading parquet files: {e}")

    # Función para buscar usuario por número
    def find_user_by_number(self, number):
        try:
            result = self.users_data_df[self.users_data_df['number'] == int(number)]
            if not result.empty:
                return result.iloc[0]['user']
        except Exception as e:
            print(f"[ERROR] Searching user by number: {e}")
        return None

    # Función para validar credenciales
    def validate_credentials(self, user_input, password_input):
        try:
            matched = self.users_df[
                (self.users_df['user'] == user_input) &
                (self.users_df['password'] == password_input)
            ]
            return not matched.empty
        except Exception as e:
            print(f"[ERROR] Validating credentials: {e}")
            return False

    # Método para manejar peticiones del cliente
    def handle_client(self, conn, addr):
        print(f"[+] Client connected from: {addr}")
        try:
            conn.sendall(b"Authentication required (user|password):\n")
            data = conn.recv(1024).decode().strip()

            if '|' not in data:
                conn.sendall(b"Invalid format. Disconnecting.\n")
                conn.close()
                return

            user_input, password_input = data.split('|', 1)

            if not self.validate_credentials(user_input, password_input):
                conn.sendall(b"Invalid credentials. Disconnecting.\n")
                conn.close()
                return

            conn.sendall(b"Authentication successful. Welcome.\n")
            request_number = 1

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                message = data.decode().strip().upper()
                print(f"[{addr}] Request {request_number}: {message}")
                request_number += 1

                if message == "HELLO":
                    response = "Hello client 👋"
                elif message == "TIME":
                    response = f"Current time: {datetime.now().strftime('%H:%M:%S')}"
                elif message.startswith("USER"):
                    parts = message.split('|')
                    if len(parts) > 1:
                        user = self.find_user_by_number(parts[1])
                        if user:
                            response = f"User {parts[1]} is: {user}"
                        else:
                            response = f"User {parts[1]} not found"
                    else:
                        response = "Incorrect format for USER. Use: USER|number"
                elif message == "EXIT":
                    response = "Goodbye 👋"
                    conn.sendall(response.encode())
                    break
                else:
                    response = f"Unknown command: {message}"

                conn.sendall(response.encode())

        except Exception as e:
            print(f"[ERROR] With client {addr}: {e}")
        finally:
            conn.close()
            with self.clients_lock:
                self.clients_active -= 1
                self.clients_connections = [c for c in self.clients_connections if c[1] != addr]
            print(f"[-] Client {addr} disconnected")

    # Método para aceptar y validar conexiones
    def accept_connections(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"🚀 Server listening on {self.host}:{self.port} (max {self.max_clients} clients)\n")

        self.running = True

        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                with self.clients_lock:
                    if self.clients_active >= self.max_clients:
                        conn.sendall(b"Server busy. Try later.")
                        conn.close()
                        continue
                    self.clients_active += 1
                    self.clients_connections.append((conn, addr))

                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
            except Exception as e:
                print(f"[ERROR] Accepting connections: {e}")

    # Método para iniciar el servidor
    def start_server(self):
        print("Starting server...")
        accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
        accept_thread.start()

    # Método para detener el servidor
    def stop_server(self):
        print("Stopping server...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        with self.clients_lock:
            for conn, addr in self.clients_connections:
                try:
                    conn.sendall(b"Server is shutting down. Disconnecting.\n")
                    conn.close()
                except:
                    pass
            self.clients_connections.clear()
            self.clients_active = 0

    # Método para reiniciar el servidor con nuevas configuraciones
    def settings_server(self, new_host=None, new_port=None, new_max_clients=None):
        print("Restarting server with new settings...")
        self.stop_server()
        if new_host:
            self.host = new_host
        if new_port:
            self.port = new_port
        if new_max_clients:
            self.max_clients = new_max_clients
        self.start_server()

    # Método para desconectar clientes manualmente por dirección
    def disconnect_client(self, addr):
        with self.clients_lock:
            for conn, client_addr in self.clients_connections:
                if client_addr == addr:
                    try:
                        conn.sendall(b"Disconnected by server.\n")
                        conn.close()
                        print(f"Client {addr} disconnected manually.")
                    except Exception as e:
                        print(f"[ERROR] Disconnecting client {addr}: {e}")
                    self.clients_connections = [c for c in self.clients_connections if c[1] != addr]
                    self.clients_active -= 1
                    return True
        print(f"No client found with address {addr}")
        return False

    # Método para mostrar clientes conectados
    def show_connected_clients(self):
        with self.clients_lock:
            clients_list = [addr for _, addr in self.clients_connections]
        print(f"Connected clients ({len(clients_list)}): {clients_list}")
        return clients_list


if __name__ == "__main__":
    server = Central_Server()
    server.start_server()

    # Para evitar que el script termine inmediatamente y el hilo pueda correr,
    # se puede poner un loop infinito o usar otra técnica, por ejemplo:
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServer stopping by user request...")
        server.stop_server()
