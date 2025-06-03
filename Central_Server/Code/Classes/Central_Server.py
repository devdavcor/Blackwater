import socket
import threading
import pandas as pd
import os
from datetime import datetime
import ast
from .Unit import *

class Central_Server:
    def __init__(self, host='0.0.0.0', port=10000, max_clients=3):
        # Rutas base y archivos
        base_path = os.path.dirname(os.path.abspath(__file__))
        blackwater_root = os.path.abspath(os.path.join(base_path, "..", "..", ".."))
        db_path = os.path.join(blackwater_root, "Central_Server", "Resources", "DB")

        self.users_path = os.path.join(db_path, 'users.parquet')
        self.users_data_path = os.path.join(db_path, 'users_data.parquet')
        self.users_data_prueba_path = os.path.join(db_path, 'users_data_prueba.parquet')
        self.users_balance_path = os.path.join(db_path, 'users_balance.parquet')
        self.users_biometrics_path = os.path.join(db_path, 'users_biometrics.parquet')
        self.administrators_path = os.path.join(db_path, 'administrators.parquet')
        self.branches_path = os.path.join(db_path, 'branches.parquet')

        # DataFrames (inicialmente None)
        self.users_df = None
        self.users_data_df = None
        self.users_data_prueba_df = None
        self.users_balance_df = None
        self.users_biometrics_df = None
        self.administrators_df = None
        self.branches_df = None

        # Carga inicial de bases de datos parquet
        self.load_databases()

        # Configuración del servidor
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.connected_users = set ()  # Usuarios actualmente conectados

        self.server_socket = None
        self.clients_active = 0
        self.clients_lock = threading.Lock()
        self.clients_connections = []  # Lista para almacenar conexiones activas

        self.running = False

    def load_databases(self):
        try:
            self.users_df = pd.read_parquet(self.users_path)
            self.users_data_df = pd.read_parquet(self.users_data_path)
            self.users_data_prueba_df = pd.read_parquet(self.users_data_prueba_path)
            self.users_balance_df = pd.read_parquet(self.users_balance_path)
            self.users_biometrics_df = pd.read_parquet(self.users_biometrics_path)
            self.administrators_df = pd.read_parquet(self.administrators_path)
            self.branches_df = pd.read_parquet(self.branches_path)
            print("✅ Todos los archivos parquet se cargaron correctamente.\n")
        except Exception as e:
            print(f"❌ Error al cargar los archivos parquet: {e}")

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
    def validate_credentials(self, user_input, password_input) :
        print('Validando credenciales...')
        try :
            with self.clients_lock :
                if user_input in self.connected_users :
                    print(f"USER: {user_input} | PASSWORD: {password_input}")
                    print ( f"[ERROR] User already connected: {user_input}" )
                    return False  # Usuario ya está conectado

            matched = self.users_df[
                (self.users_df['user'] == user_input) &
                (self.users_df['password'] == password_input)
                ]
            print ( f"USER: {user_input} | PASSWORD: {password_input}" )
            print ( f"[ERROR] User already connected: {user_input}" )
            return not matched.empty
        except Exception as e :
            print ( f"[ERROR] Validating credentials: {e}" )
            return False

    def handle_client(self, conn, addr) :
        print ( f"[+] Client connected from: {addr}" )
        user_input = None  # Se define aquí para que esté disponible en finally

        try :
            conn.sendall ( b"Authentication required (user|password):\n" )
            data = conn.recv ( 32768 ).decode ().strip ()

            if '|' not in data :
                conn.sendall ( b"Invalid format. Disconnecting.\n" )
                return

            user_input, password_input = data.split ( '|', 1 )

            if not self.validate_credentials ( user_input, password_input ) :
                conn.sendall ( b"Invalid credentials or user already connected. Disconnecting.\n" )
                return

            with self.clients_lock :
                self.connected_users.add ( user_input )

            conn.sendall ( b"Authentication successful. Welcome.\n" )
            request_number = 1

            while True :
                data = conn.recv ( 32768 )
                if not data :
                    break

                message = data.decode ().strip ()
                print ( f"[{addr}] Request {request_number}: {message}" )
                request_number += 1

                parts = message.split ( '|' )
                command = parts[0].upper ()
                response = ""

                try :
                    if command == "HELLO" :
                        response = "Hello client 👋"

                    elif command == "NEW_USER" and len ( parts ) == 4 :
                        name = parts[1].strip ()
                        last_name = parts[2].strip ()
                        curp = parts[3].strip ()
                        result = new_user ( curp, name, last_name )
                        response = f"NEW_USER|{name}|{last_name}|{result}"

                    elif command == "CHANGE_NAME" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        new_name = parts[2].strip ()
                        result = change_name ( user_code, new_name )
                        response = f"CHANGE_NAME|{user_code}|{new_name}|{result}"

                    elif command == "CHANGE_LAST_NAME" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        new_lastname = parts[2].strip ()
                        result = change_last_name ( user_code, new_lastname )
                        response = f"CHANGE_LAST_NAME|{user_code}|{new_lastname}|{result}"

                    elif command == "CHANGE_CURP" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        new_curp = parts[2].strip ()
                        result = change_curp ( user_code, new_curp )
                        response = f"CHANGE_CURP|{user_code}|{new_curp}|{result}"

                    elif command == "UPDATE_BIOMETRICS" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        vector_str = parts[2].strip ()
                        try :
                            vector = ast.literal_eval ( vector_str )
                            result = update_biometrics ( user_code, vector )
                            response = f"UPDATE_BIOMETRICS|{user_code}|{result}"
                        except Exception as e :
                            print ( f"❌ Error interpreting biometric vector: {e}" )
                            response = f"UPDATE_BIOMETRICS|{user_code}|False"

                    elif command == "CHANGE_PASSWORD" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        new_password = parts[2].strip ()
                        result = change_password ( user_code, new_password )
                        response = f"CHANGE_PASSWORD|{user_code}|{result}"

                    elif command == "WITHDRAW_CASH" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        amount = float ( parts[2].strip () )
                        result = withdraw_cash ( user_code, amount )
                        response = f"WITHDRAW_CASH|{user_code}|{result}"

                    elif command == "DEPOSIT_CASH" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        amount = float ( parts[2].strip () )
                        result = deposit_cash ( user_code, amount )
                        response = f"DEPOSIT_CASH|{user_code}|{result}"

                    elif command == "CHECK_BALANCE" and len ( parts ) == 2 :
                        user_code = parts[1].strip ()
                        result = check_balance ( user_code )
                        response = f"CHECK_BALANCE|{user_code}|{result}"

                    elif command == "DELETE_USER" and len ( parts ) == 2 :
                        user_code = parts[1].strip ()
                        result = delete_user ( user_code )
                        response = f"DELETE_USER|{user_code}|{result}"

                    elif command == "SEARCH_USER" and len ( parts ) == 2 :
                        curp = parts[1].strip ()
                        result = get_user_by_curp ( curp )
                        response = f"SEARCH_USER|{curp}|{result}"

                    elif command == "GET_BIOMETRICS" and len ( parts ) == 2 :
                        user = parts[1].strip ()
                        result = get_biometrics ( user )
                        response = f"GET_BIOMETRICS|{user}|{result}"

                    elif command == "NEW_BRANCH" and len ( parts ) in [3, 4] :
                        name = parts[1].strip ()
                        last_name = parts[2].strip ()
                        password = parts[3].strip () if len ( parts ) == 4 else "000000"
                        result = new_branch ( name, last_name, password )
                        response = f"NEW_BRANCH|{name}|{last_name}|{result}"

                    elif command == "CHANGE_NAME_BRANCH" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        new_name = parts[2].strip ()
                        result = change_branch_name ( user_code, new_name )
                        response = f"CHANGE_NAME_BRANCH|{user_code}|{result}"

                    elif command == "CHANGE_LAST_NAME_BRANCH" and len ( parts ) == 3 :
                        user_code = parts[1].strip ()
                        new_last_name = parts[2].strip ()
                        result = change_branch_last_name ( user_code, new_last_name )
                        response = f"CHANGE_LAST_NAME_BRANCH|{user_code}|{result}"

                    elif command == "CHANGE_PASSWORD_BRANCH" and len ( parts ) == 4 :
                        user_code = parts[1].strip ()
                        new_password = parts[2].strip ()
                        result = change_password_branch ( user_code, new_password )
                        response = f"CHANGE_PASSWORD_BRANCH|{user_code}|{result}"

                    elif command == "DELETE_BRANCH" and len ( parts ) == 2 :
                        user_code = parts[1].strip ()
                        result = delete_branch ( user_code )
                        response = f"DELETE_BRANCH|{user_code}|{result}"

                    else :
                        response = f"Unknown or malformed command: {message}"

                except Exception as cmd_err :
                    response = f"[ERROR] Processing command: {cmd_err}"

                conn.sendall ( response.encode () )

        except Exception as e :
            print ( f"[ERROR] With client {addr}: {e}" )

        finally :
            conn.close ()
            with self.clients_lock :
                self.clients_active -= 1
                self.clients_connections = [c for c in self.clients_connections if c[1] != addr]
                if user_input :
                    self.connected_users.discard ( user_input )
            print ( f"[-] Client {addr} disconnected" )

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
    def start_server(self) :
        if hasattr ( self, 'server_running' ) and self.server_running :
            print ( "Servidor ya está en ejecución. No se iniciará de nuevo." )
            return False

        print ( "Starting server..." )
        self.server_running = True
        accept_thread = threading.Thread ( target=self.accept_connections, daemon=True )
        accept_thread.start ()
        return True

    # Método para detener el servidor
    def stop_server(self):
        print("Stopping server...")
        self.server_running = False
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            return True
        with self.clients_lock:
            for conn, addr in self.clients_connections:
                try:
                    conn.sendall(b"Server is shutting down. Disconnecting.\n")
                    conn.close()
                except:
                    pass
            self.clients_connections.clear()
            self.clients_active = 0
        return True

    # Método para reiniciar el servidor con nuevas configuraciones
    def settings_server(self, new_port=None, new_max_clients=None):
        print("Restarting server with new settings...")
        self.stop_server()
        if new_port:
            self.port = new_port
        if new_max_clients:
            self.max_clients = new_max_clients
        self.start_server()
        return True

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
                        return False
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

    '''------------------------------------------------------------------------'''

if __name__ == "__main__":
    server = Central_Server()
    server.start_server()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nServer stopping by user request...")
        server.stop_server()
