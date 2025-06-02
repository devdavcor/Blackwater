import socket
import threading
import cv2
import face_recognition
import numpy as np
import pandas as pd
import os
import time

class Branch_Server:
    def __init__(self, server_a_ip, server_a_port, listen_port=0, max_connections=3) :
        self.server_a_ip = server_a_ip
        self.server_a_port = server_a_port
        self.listen_port = listen_port
        self.max_connections = max_connections
        self.conn_a = None
        self.stop_event = threading.Event ()
        self.server_running = False  # asegura que el estado sea consistente

    def connect_to_server_a(self, user, password):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_a_ip, self.server_a_port))
        print("[B] Connected to server A")

        message = s.recv(1024).decode()
        print(f"[B] Message from A: {message}")

        credentials = f"{user}|{password}"
        s.sendall(credentials.encode())

        response = s.recv(1024).decode()
        print(f"[B] Authentication response: {response}")

        if "successful" not in response.lower():
            print("[B] Authentication failed. Closing connection.")
            s.close()
            return None

        return s

    def handle_client_c(self, conn_c, conn_a):
        try:
            while True:
                data = conn_c.recv(1024)
                if not data:
                    break
                print(f"[B] Received from C: {data.decode()}")
                conn_a.sendall(data)

                response = conn_a.recv(1024)
                print(f"[B] Response from A: {response.decode()}")
                conn_c.sendall(response)
        except Exception as e:
            print(f"[B] Communication error: {e}")
        finally:
            conn_c.close()
            self.stop_event.set()  # Stop sending messages if client disconnects

    def listen_for_client_c(self) :
        with socket.socket ( socket.AF_INET, socket.SOCK_STREAM ) as server :
            server.bind ( ('0.0.0.0', self.listen_port) )
            actual_port = server.getsockname ()[1]
            print ( f"[B] Listening for up to {self.max_connections} clients on port {actual_port}" )
            server.listen ()

            connections_handled = 0

            while connections_handled < self.max_connections and not self.stop_event.is_set () :
                try :
                    print (
                        f"[B] Waiting for client C to connect... ({connections_handled + 1}/{self.max_connections})" )
                    conn_c, addr = server.accept ()
                    print ( f"[B] Client C connected: {addr}" )

                    client_thread = threading.Thread ( target=self.handle_client_c, args=(conn_c, self.conn_a),
                                                       daemon=True )
                    client_thread.start ()

                    connections_handled += 1

                except Exception as e :
                    print ( f"[B] Error accepting client connection: {e}" )
                    break

            print ( f"[B] Reached max client connections ({self.max_connections}). No longer accepting new clients." )

    def send_messages_to_a(self):
        """Thread method to send manual messages to server A."""
        try:
            while not self.stop_event.is_set():
                msg = input("[B] Enter message to send to A (or 'exit' to stop): ")
                if msg.strip().lower() == "exit":
                    print("[B] Stopping message sender.")
                    self.stop_event.set()
                    self.conn_a.close()
                    break
                self.conn_a.sendall(msg.encode())
                response = self.conn_a.recv(1024).decode()
                print(f"[B] Response from A: {response}")
        except Exception as e:
            print(f"[B] Error sending messages to A: {e}")
            self.stop_event.set()

    def start_server(self, user, password) :
        if hasattr ( self, 'server_running' ) and self.server_running :
            print ( "[B] El servidor ya está corriendo." )
            return

        print ( "[B] Starting server..." )
        self.server_running = True

        self.conn_a = self.connect_to_server_a ( user, password )
        if not self.conn_a :
            print ( "[B] No se pudo conectar a A. Cancelando servidor." )
            self.server_running = False
            return

        accept_thread = threading.Thread ( target=self.listen_for_client_c, daemon=True )
        accept_thread.start ()

        sender_thread = threading.Thread ( target=self.send_messages_to_a, daemon=True )
        sender_thread.start ()

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
            response = self.conn_a.recv(1024).decode()
            print(f"[B] Response from A: {response}")
            return response
        except Exception as e:
            print(f"[B] Error sending command to A: {e}")
            return f"ERROR|{str(e)}"

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

    def new_customer(self, curp, name, last_name) :
        petition = f"NEW_USER|{curp}|{name}|{last_name}"
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
