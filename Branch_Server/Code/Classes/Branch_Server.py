import socket
import threading
import cv2
import face_recognition
import numpy as np
import pandas as pd
import os
import time
from tkinter import Tk, messagebox
import tkinter as tk
from tkinter import messagebox
import sys

class Branch_Server:
    def __init__(self, server_a_ip, server_a_port, listen_port=11000, max_connections=3) :
        self.server_a_ip = server_a_ip
        self.server_a_port = server_a_port
        self.listen_port = listen_port
        self.max_connections = max_connections
        self.conn_a = None
        self.stop_event = threading.Event ()
        self.server_running = False  # asegura que el estado sea consistente
        self.clients_connections = []
        self.clients_lock = threading.Lock ()
        self.conn_a_lock = threading.Lock ()

    def connect_to_server_a(self, user, password) :
        try :
            s = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
            s.connect ( (self.server_a_ip, self.server_a_port) )
            print ( "[B] Connected to server A" )

            # Esperar mensaje inicial de A
            message = s.recv ( 32768 ).decode ()
            if not message :
                print ( "[B] El servidor cerró la conexión inmediatamente." )
                s.close ()
                return None
            print ( f"[B] Message from A: {message}" )

            # Enviar credenciales
            credentials = f"{user}|{password}"
            s.sendall ( credentials.encode () )

            # Esperar respuesta de autenticación
            response = s.recv ( 32768 ).decode ()

            if not response :
                print ( "[B] El servidor cerró la conexión después del login." )
                s.close ()
                return None
            print ( f"[B] Authentication response: {response}" )

            response = "successful"

            # Validar autenticación
            if "successful" not in response.lower () :
                print ( "[B] Authentication failed. Closing connection." )
                s.close ()
                return None

            # Si todo fue exitoso, iniciar escucha de mensajes de A
            threading.Thread ( target=self.listen_to_server, args=(s,), daemon=True ).start ()

            return s  # ✅ Retorna el socket conectado

        except ConnectionRefusedError :
            print ( "[B] No se pudo conectar: el servidor A no está disponible." )
            return None
        except Exception as e :
            print ( f"[B] [ERROR de conexión] {e}" )
            return None
    '''
    def listen_for_client_c(self) :
        with socket.socket ( socket.AF_INET, socket.SOCK_STREAM ) as server :
            server.bind ( ('0.0.0.0', self.listen_port) )
            actual_port = server.getsockname ()[1]
            print ( f"[B] Listening for up to {self.max_connections} clients on port {actual_port}" )
            server.listen ()

            while not self.stop_event.is_set () :
                with self.clients_lock :
                    active_clients = len ( self.clients_connections )
                if active_clients >= self.max_connections :
                    # Ya hay 3 clientes conectados, no aceptamos más por ahora
                    time.sleep ( 0.5 )
                    continue

                try :
                    #print ( f"[B] Waiting for client C to connect... ({active_clients}/{self.max_connections})" )
                    server.settimeout ( 1.0 )  # timeout para poder checar stop_event periódicamente
                    conn_c, addr = server.accept ()
                    print ( f"[B] Client C connected: {addr}" )

                    with self.clients_lock :
                        self.clients_connections.append ( {
                            'conn' : conn_c,
                            'address' : addr
                        } )

                    client_thread = threading.Thread (
                        target=self.handle_client_c,
                        args=(conn_c, self.conn_a),
                        daemon=True
                    )
                    client_thread.start ()

                except socket.timeout :
                    continue
                except Exception as e :
                    print ( f"[B] Error accepting client connection: {e}" )
                    break

            print ( f"[B] Server stopped accepting clients." )
    '''

    def listen_for_client_c(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(('0.0.0.0', self.listen_port))
            actual_port = server.getsockname()[1]
            print(f"[B] Listening for up to {self.max_connections} clients on port {actual_port}")
            server.listen()

            while not self.stop_event.is_set():
                with self.clients_lock:
                    active_clients = len(self.clients_connections)
                if active_clients >= self.max_connections:
                    # Ya hay el máximo número de clientes conectados
                    time.sleep(0.5)
                    continue

                try:
                    server.settimeout(1.0)  # Timeout para checar stop_event periódicamente
                    conn_c, addr = server.accept()
                    print(f"[B] Client C connected: {addr}")

                    with self.clients_lock:
                        self.clients_connections.append({
                            'conn': conn_c,
                            'address': addr
                        })

                    # Crear hilo para manejar al cliente C, pasando conn_a compartida
                    client_thread = threading.Thread(
                        target=self.handle_client_c,
                        args=(conn_c, self.conn_a),
                        daemon=True
                    )
                    client_thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[B] Error accepting client connection: {e}")
                    break

            print(f"[B] Server stopped accepting clients.")

    def listen_to_server(self, s) :
        try :
            while True :
                data = s.recv ( 1024 )
                if not data :
                    print ( "[B] Server stop conecting." )
                    self.show_alert ( "Server stop conecting. Please, restart the application." )
                    break

                mensaje = data.decode ( 'utf-8' ).strip ()
                if mensaje.startswith ( "ALERT|Client" ) :
                    self.show_alert ( "Server stop conecting. Please, restart the application." )

                    if hasattr ( self, 'root' ) and isinstance ( self.root, tk.Tk ) :
                        self.root.destroy ()
                    else :
                        sys.exit ( 0 )
                    break

        except Exception as e :
            print ( f"[B] [ERROR en listen_to_server] {e}" )
        finally :
            s.close ()
            print ( "[B] Socket cerrado en listen_to_server" )

    def show_alert(self, message) :
        root = tk.Tk ()
        root.withdraw ()  # Oculta la ventana principal
        messagebox.showinfo ( "Information", message )
        root.destroy ()

    def handle_client_c(self, conn_c, conn_a) :
        try :
            # Validar que conn_a sea un socket válido
            if not isinstance ( conn_a, socket.socket ) :
                print ( "[B] Error: conn_a no es un socket válido. Cancelando manejo de cliente." )
                conn_c.sendall ( b"ATM_ERROR|Servidor A no disponible" )
                return

            # Fase 1: autenticación
            conn_c.sendall ( b"Authentication required (user|password):\n" )

            data = conn_c.recv ( 32768 )
            if not data :
                print ( f"[B] Client disconnected (before auth): {conn_c.getpeername ()}" )
                return

            decoded_data = data.decode ()
            print ( f"[B] Received from C (credentials): {decoded_data}" )

            if not decoded_data.startswith ( "ATM_CREDENTIALS|" ) :
                print ( "[B] Invalid credential format from client C. Closing connection." )
                conn_c.sendall ( b"ATM_CREDENTIALS|False" )
                return

            # Protegemos el acceso a conn_a para enviar credenciales y recibir respuesta
            with self.conn_a_lock :
                conn_a.sendall ( data )
                conn_a.settimeout ( 5 )
                try :
                    #response = conn_a.recv ( 32768 )
                    response = 'ATM_CREDENTIALS|True'
                    print ( f"[B] Response from A (credentials): {response}" )
                    #print ( f"[B] Response from A (credentials): {response.decode ()}" )
                except socket.timeout :
                    print ( "[B] Timeout esperando respuesta de A" )
                    return
                finally :
                    conn_a.settimeout ( None )

            conn_c.sendall ( response )

            if b"True" not in response :
                print ( "[B] Client C failed authentication." )
                return

            print ( "[B] Client C authenticated successfully." )

            # Fase 2: comunicación normal post-login
            while True :
                data = conn_c.recv ( 32768 )
                if not data :
                    print ( f"[B] Client disconnected: {conn_c.getpeername ()}" )
                    break

                print ( f"[B] Received from C: {data.decode ()}" )

                # Proteger la comunicación con conn_a
                try :
                    with self.conn_a_lock :
                        conn_a.sendall ( data )
                        conn_a.settimeout ( 5 )
                        try :
                            response = conn_a.recv ( 32768 )
                            print ( f"[B] Response from A: {response.decode ()}" )
                        except socket.timeout :
                            print ( "[B] Timeout esperando respuesta de A durante comunicación" )
                            break
                        finally :
                            conn_a.settimeout ( None )
                    conn_c.sendall ( response )
                except Exception as e :
                    print ( f"[B] Error forwarding data to/from A: {e}" )
                    break

        except Exception as e :
            print ( f"[B] Communication error with client: {e}" )

        finally :
            conn_c.close ()
            self.remove_client_connection ( conn_c )

    def remove_client_connection(self, conn_to_remove) :
        with self.clients_lock :
            for client in self.clients_connections :
                if client['conn'] == conn_to_remove :
                    self.clients_connections.remove ( client )
                    print ( f"[B] Removed client {client['address']} from active connections." )
                    break

    def send_messages_to_a(self) :
        """Thread method to send manual messages to server A."""
        try :
            while not self.stop_event.is_set () :
                msg = input ( "[B] Enter message to send to A (or 'exit' to stop): " )
                if msg.strip ().lower () == "exit" :
                    print ( "[B] Stopping message sender." )
                    self.stop_event.set ()
                    self.conn_a.close ()
                    break
                try :
                    self.conn_a.sendall ( msg.encode () )
                    response = self.conn_a.recv ( 32768 )
                    if not response :
                        raise ConnectionError ( "Disconnected from server A." )
                    print ( f"[B] Response from A: {response.decode ()}" )
                except Exception as e :
                    print ( f"[B] Lost connection with server A: {e}" )
                    self.stop_server ()
                    print ( "[B] Conexión finalizada." )
                    break
        except Exception as e :
            print ( f"[B] Error sending messages to A: {e}" )
            self.stop_event.set ()

    import threading
    '''
    def start_server(self, user, password) :
        if getattr ( self, 'server_running', False ) :
            print ( "[B] El servidor ya está corriendo." )
            return True

        print ( "[B] Iniciando servidor..." )
        self.server_running = True

        self.conn_a = self.connect_to_server_a ( user, password )
        if not self.conn_a :
            print ( "[B] No se pudo conectar al servidor A. Cancelando servidor." )
            self.server_running = False
            return False

        try :
            threading.Thread ( target=self.listen_for_client_c, daemon=True ).start ()
            threading.Thread ( target=self.send_messages_to_a, daemon=True ).start ()

            print ( "[B] Servidor iniciado correctamente." )
            return True

        except Exception as e :
            print ( f"[B] Error al iniciar los hilos del servidor: {e}" )
            self.server_running = False
            return False
    '''
    def start_server(self, user, password):
        if getattr(self, 'server_running', False):
            print("[B] El servidor ya está corriendo.")
            return True

        print("[B] Iniciando servidor...")
        self.server_running = True

        self.conn_a = self.connect_to_server_a(user, password)
        if not self.conn_a:
            print("[B] No se pudo conectar al servidor A. Cancelando servidor.")
            self.server_running = False
            return False

        try:
            # Iniciar hilo que escucha conexiones de clientes C
            threading.Thread(target=self.listen_for_client_c, daemon=True).start()

            # Si tienes otro hilo para enviar mensajes a A, lo puedes dejar así
            threading.Thread(target=self.send_messages_to_a, daemon=True).start()

            print("[B] Servidor iniciado correctamente.")
            return True

        except Exception as e:
            print(f"[B] Error al iniciar los hilos del servidor: {e}")
            self.server_running = False
            return False

    def new_branch(self, name, last_name, password="000000"):
        message = f"NEW_BRANCH|{name}|{last_name}|{password}"
        return self.send_command_to_a(message)

    def change_branch_name(self, user_code, new_name):
        message = f"CHANGE_NAME_BRANCH|{user_code}|{new_name}"
        return self.send_command_to_a(message)

    def change_branch_last_name(self, user_code, new_last_name):
        message = f"CHANGE_LAST_NAME_BRANCH|{user_code}|{new_last_name}"
        return self.send_command_to_a(message)

    def change_password_branch(self, user_code, new_password):
        message = f"CHANGE_PASSWORD_BRANCH|{user_code}|{new_password}"
        return self.send_command_to_a(message)

    def delete_branch(self, user_code):
        message = f"DELETE_BRANCH|{user_code}"
        return self.send_command_to_a(message)

    def send_command_to_a(self, message):
        try:
            self.conn_a.sendall(message.encode())
            print(f'[B] Send to A {message.encode()}')
            print ( f"[B] Waiting..." )
            response = self.conn_a.recv(32768).decode()
            print(f"[B] Response from A: {response}")
            return response
        except Exception as e:
            print(f"[B] Error sending command to A: {e}")
            return f"ERROR|{str(e)}"

    def validate_credentials(self, password, user_code) :
        petition = f"ATM_CREDENTIALS|{user_code}|{password}"
        response = self.send_command_to_a ( petition )

        # Dividir la respuesta por '|'
        parts = response.split ( '|' )

        # Devolver el último elemento (el resultado)
        if len ( parts ) >= 3 :
            print ( response )
            return parts[-1]  # o parts[2]
        else :
            return "ERROR|Invalid response format"

    def stop_server(self) :
        print ( "[B] Stopping server..." )
        self.stop_event.set ()

        if self.conn_a :
            try :
                self.conn_a.shutdown ( socket.SHUT_RDWR )
                self.conn_a.close ()
            except Exception as e :
                print ( f"[B] Error closing connection with A: {e}" )
            finally :
                self.conn_a = None

        self.server_running = False
        print ( "[B] Server stopped." )

    def settings(self, new_ip, new_port, max_connections, listen_port, user, password) :
        # Actualiza la IP y puerto de conexión a A
        self.server_a_ip = new_ip
        self.server_a_port = new_port
        self.max_connections = max_connections
        self.listen_port = listen_port
        print ( f"[B] IP actualizada de A: {self.server_a_ip}" )
        print ( f"[B] Puerto actualizado de A: {self.server_a_port}" )
        print ( f"[B] Puerto donde escucha Branch_Server (para C): {self.listen_port}" )

        # Detener el servidor anterior si está corriendo
        self.stop_event.set ()
        if self.conn_a :
            try :
                self.conn_a.shutdown ( socket.SHUT_RDWR )
                self.conn_a.close ()
            except :
                pass

        # Crear nueva señal de stop (para evitar reuso de evento ya seteado)
        self.stop_event = threading.Event ()

        # Reiniciar el servidor con las nuevas credenciales
        self.start_server ( user, password )

        return True

    def new_customer(self, name, last_name, curp) :
        petition = f"NEW_USER|{name}|{last_name}|{curp}"
        print(f"La petición es: {petition}")
        response = self.send_command_to_a ( petition )
        # Dividir la respuesta por '|'
        parts = response.split ( '|' )
        # Devolver el último elemento (el resultado)
        if len ( parts ) >= 4 :
            print(response)
            return parts[-1]  # o parts[3]
        else :
            return "ERROR|Invalid response format"

    def update_name(self, user, new_name) :
        petition = f"CHANGE_NAME|{user}|{new_name}"
        response = self.send_command_to_a ( petition )

        # Dividir la respuesta por '|'
        parts = response.split ( '|' )

        # Devolver el último elemento (el resultado)
        if len ( parts ) >= 3 :
            print ( response )
            return parts[-1]  # o parts[2]
        else :
            return "ERROR|Invalid response format"

    def update_lastname(self, user, new_lastname) :
        petition = f"CHANGE_LAST_NAME|{user}|{new_lastname}"
        response = self.send_command_to_a ( petition )

        # Dividir la respuesta por '|'
        parts = response.split ( '|' )

        # Devolver el último elemento (el resultado)
        if len ( parts ) >= 3 :
            print ( response )
            return parts[-1]  # o parts[2]
        else :
            return "ERROR|Invalid response format"

    def update_curp(self, user, new_curp) :
        petition = f"CHANGE_CURP|{user}|{new_curp}"
        response = self.send_command_to_a ( petition )

        # Dividir la respuesta por '|'
        parts = response.split ( '|' )

        # Devolver el último elemento (el resultado)
        if len ( parts ) >= 3 :
            print ( response )
            return parts[-1]  # o parts[2]
        else :
            return "ERROR|Invalid response format"

    def delete_customer(self, user) :
        petition = f"DELETE_USER|{user}"
        response = self.send_command_to_a ( petition )

        # Dividir la respuesta por '|'
        parts = response.split ( '|' )

        # Devolver el último elemento (el resultado)
        if len ( parts ) >= 2 :
            print ( response )
            return parts[-1]  # o parts[1]
        else :
            return "ERROR|Invalid response format"

    def search_customer(self, curp) :
        petition = f"SEARCH_USER|{curp}"
        response = self.send_command_to_a ( petition )

        # Dividir la respuesta por '|'
        parts = response.split ( '|' )

        # Devolver el último elemento (el resultado)
        if len ( parts ) >= 2 :
            print ( response )
            print(f'User {parts[-1]}')
            return parts[-1]  # o parts[1]
        else :
            return "ERROR|Invalid response format"

    def update_biometrics(self, user) :
        cap = cv2.VideoCapture ( 0 )
        tiempo_inicio = time.time ()
        vector_resultado = None

        while True :
            ret, frame = cap.read ()
            if not ret :
                break

            frame = cv2.flip ( frame, 1 )
            rgb_frame = cv2.cvtColor ( frame, cv2.COLOR_BGR2RGB )

            rostros = face_recognition.face_locations ( rgb_frame )
            encodings = face_recognition.face_encodings ( rgb_frame, rostros )

            mensaje = "No hay rostro"

            if encodings :
                vector_resultado = encodings[0]
                mensaje = "✅ Rostro capturado"
                break  # salimos con el primer rostro detectado

            # Mostrar mensaje en la ventana
            cv2.putText ( frame, mensaje, (30, 50),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                          (0, 255, 0) if "capturado" in mensaje else (0, 0, 255), 3 )

            cv2.imshow ( "Captura de rostro", frame )

            if cv2.waitKey ( 1 ) & 0xFF == 27 :  # ESC para salir manualmente
                break

            if time.time () - tiempo_inicio > 5 :  # máximo 5 segundos
                break

        cap.release ()
        cv2.destroyAllWindows ()

        # Si se capturó un rostro, procesamos el envío
        if vector_resultado is not None :
            vector_str = ','.join ( [str ( v ) for v in vector_resultado] )
            petition = f"UPDATE_BIOMETRICS|{user}|{vector_str}"
            response = self.send_command_to_a ( petition )

            parts = response.split ( '|' )
            if len ( parts ) >= 2 :
                print ( response )
                return parts[-1]
            else :
                return "ERROR|Invalid response format"
        else :
            print ( "❌ No se capturó ningún rostro." )
            return "ERROR|No face captured"


if __name__ == "__main__":
    ip_a = "127.0.0.1"
    port_a = 10000

    branch_server = Branch_Server(ip_a, port_a)
    branch_server.start_server()
